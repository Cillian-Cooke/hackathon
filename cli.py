#!/usr/bin/env python3
"""
Gemini-powered D&D Dungeon Master CLI.

A text-based RPG engine that uses Google's Gemini API to generate
dynamic, setting-aware dungeon master responses. Supports campaign
and character persistence, stat management, and both CLI and web modes.
"""

import json
import os
import random
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# =============================================================================
# Game Data Constants
# =============================================================================

CAMPAIGN_THEMES = [
    "Medieval Fantasy",
    "Steampunk",
    "Post-Apocalyptic",
    "Sci-Fi Galactic",
    "Ancient Mythology",
    "Other",
]

RACES: dict[str, dict[str, list[str]]] = {
    "Human": {"abilities": ["Adaptable", "Extra Skill Point"]},
    "Elf": {"abilities": ["Darkvision", "Keen Senses"]},
    "Dwarf": {"abilities": ["Resilience", "Stonecunning"]},
    "Orc": {"abilities": ["Savage Strength", "Intimidation"]},
}

CLASSES: dict[str, dict[str, list[str]]] = {
    "Warrior": {"abilities": ["Power Strike", "Shield Block"]},
    "Mage": {"abilities": ["Spellcasting", "Arcane Shield"]},
    "Rogue": {"abilities": ["Stealth", "Backstab"]},
    "Engineer": {"abilities": ["Gadgeteering", "Mechanical Companion"]},
    "Cleric": {"abilities": ["Divine Heal", "Radiant Smite"]},
    "Other": {"abilities": []},
}

DEFAULT_STATS = {
    "Strength": 0,
    "Dexterity": 0,
    "Intelligence": 0,
    "Wisdom": 0,
    "Charisma": 0,
}

TOTAL_STAT_POINTS = 30
CAMPAIGNS_ROOT = "campaigns"
GEMINI_MODEL = "gemini-2.5-flash"

# Random Setting Descriptions (for web mode variety)
SETTING_DESCRIPTIONS = [
    "A bustling kingdom on the edge of a wild frontier.",
    "A fog-shrouded port city where pirates and merchants clash.",
    "An ancient forest realm where elves guard forgotten secrets.",
    "A desert empire built upon the ruins of a fallen civilization.",
    "A frozen northern stronghold besieged by creatures from the ice.",
    "A volcanic island chain ruled by dragon-worshipping cults.",
    "A sprawling underground city carved into a mountain's heart.",
    "A war-torn borderland where rival kingdoms vie for control.",
    "A mystical archipelago where reality bends and shifts.",
    "A decadent capital city hiding corruption beneath gilded facades.",
    "A remote monastery perched atop misty peaks, guarding ancient knowledge.",
    "A cursed swampland where the dead refuse to stay buried.",
]

# Random Character Name Components
NAME_PREFIXES = [
    "Brave", "Swift", "Iron", "Shadow", "Storm", "Fire", "Frost", "Stone",
    "Silver", "Golden", "Dark", "Light", "Wild", "Grim", "Bold", "Keen",
]
NAME_SUFFIXES = [
    "heart", "blade", "walker", "seeker", "bane", "sworn", "born", "wind",
    "strike", "shield", "forge", "hunter", "warden", "spirit", "song", "wolf",
]

# =============================================================================
# Configuration
# =============================================================================


@dataclass
class DMConfig:
    """Configuration for the Dungeon Master engine."""

    max_output_tokens: int = 2048
    summary_max_tokens: int = 100
    history_context_limit: int = 25


DEFAULT_CONFIG = DMConfig()

# =============================================================================
# Utility Functions
# =============================================================================


def prompt_input(message: str) -> str:
    """Prompts user for input and returns stripped response."""
    return input(f"{message}\n> ").strip()


def choose_from_list(options: list[str], prompt: str) -> str:
    """
    Displays a numbered list and returns the user's choice.

    Args:
        options: List of string options to display.
        prompt: The prompt message to show.

    Returns:
        The selected option string.
    """
    print(prompt)
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")

    while True:
        choice = prompt_input("Choose by number:")
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(options):
                return options[index - 1]
        print("Invalid choice — try again.")


def sanitize_filename(name: str) -> str:
    """Converts a string to a safe filename."""
    safe_chars = "".join(c for c in name if c.isalnum() or c in " _-")
    return safe_chars.replace(" ", "_")


def load_json(path: str) -> Optional[dict[str, Any]]:
    """Loads JSON from file, returning None on failure."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_json(path: str, data: dict[str, Any]) -> None:
    """Saves data to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def is_interactive_terminal() -> bool:
    """Checks if running in an interactive terminal."""
    return os.environ.get("TERM", "").startswith("xterm") or sys.stdin.isatty()


# =============================================================================
# Dungeon Master Class
# =============================================================================


class DnDDungeonMaster:
    """
    D&D Dungeon Master engine powered by Google's Gemini API.

    Manages campaigns, characters, conversation history, and AI interactions
    for both CLI and web-based gameplay.
    """

    def __init__(
        self,
        campaign_name: str = "default",
        config: DMConfig = DEFAULT_CONFIG,
    ) -> None:
        """
        Initializes the Dungeon Master.

        Args:
            campaign_name: Name of the campaign to load/create.
            config: Configuration settings for the DM.

        Raises:
            EnvironmentError: If GEMINI_API_KEY is not set.
        """
        self.config = config
        self._initialize_api_client(campaign_name)
        self._initialize_state()

        if campaign_name != "default":
            self._setup_web_campaign(campaign_name)

    def _initialize_api_client(self, campaign_name: str) -> None:
        """Sets up the Gemini API client."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            message = "Missing GEMINI_API_KEY in environment (.env)."
            if campaign_name == "default":
                print(f"❌ {message}")
                sys.exit(1)
            raise EnvironmentError(message)

        self.client = genai.Client(api_key=api_key)
        self.model = GEMINI_MODEL

    def _initialize_state(self) -> None:
        """Initializes instance state variables."""
        self.current_campaign_folder: Optional[str] = None
        self.campaign_meta: Optional[dict[str, Any]] = None
        self.character_name: Optional[str] = None
        self.save_file: Optional[str] = None
        self.campaign_data: Optional[dict[str, Any]] = None

    def _setup_web_campaign(self, campaign_name: str) -> None:
        """Sets up campaign folder and data for web mode."""
        self.current_campaign_folder = os.path.join(
            CAMPAIGNS_ROOT, sanitize_filename(campaign_name)
        )
        os.makedirs(self.current_campaign_folder, exist_ok=True)
        self._load_or_create_campaign_meta(campaign_name)
        self.setup_web_character()

    # =========================================================================
    # Campaign Management
    # =========================================================================

    def _load_or_create_campaign_meta(self, campaign_name: str) -> None:
        """Loads existing campaign metadata or creates new with randomized setting."""
        meta_path = os.path.join(self.current_campaign_folder, "campaign.json")
        meta = load_json(meta_path)

        if meta is None:
            meta = {
                "name": campaign_name,
                "theme": random.choice(CAMPAIGN_THEMES[:-1]),  # Exclude "Other"
                "description": random.choice(SETTING_DESCRIPTIONS),
                "created": datetime.now().isoformat(),
                "last_played": datetime.now().isoformat(),
            }
            save_json(meta_path, meta)

        self.campaign_meta = meta

    def setup_web_character(self) -> None:
        """Creates or loads a randomized web character."""
        # Check for existing character file
        existing_chars = [
            f for f in os.listdir(self.current_campaign_folder)
            if f.startswith("character_") and f.endswith(".json")
        ]

        if existing_chars:
            # Load existing character
            path = os.path.join(self.current_campaign_folder, existing_chars[0])
            self.save_file = path
            self.campaign_data = load_json(path)
            self.campaign_data.setdefault("history", [])
            self.character_name = self.campaign_data["character"]["name"]
            return

        # Generate random character
        char_name = f"{random.choice(NAME_PREFIXES)}{random.choice(NAME_SUFFIXES)}"
        race = random.choice(list(RACES.keys()))
        char_class = random.choice([c for c in CLASSES.keys() if c != "Other"])

        # Randomize stats (total 30 points)
        stats = self._generate_random_stats()

        # Random background based on race/class combo
        backgrounds = [
            f"A {race.lower()} {char_class.lower()} seeking glory in distant lands.",
            f"Once a humble villager, now a {char_class.lower()} with a mysterious past.",
            f"A wandering {race.lower()} who heard the call to adventure.",
            f"Exiled from their homeland, this {char_class.lower()} seeks redemption.",
            f"A {race.lower()} trained in the ways of the {char_class.lower()} since youth.",
        ]

        filename = f"character_{char_name}.json"
        path = os.path.join(self.current_campaign_folder, filename)

        data = {
            "character": {
                "name": char_name,
                "race": race,
                "class": char_class,
                "background": random.choice(backgrounds),
                "stats": stats,
                "race_abilities": RACES[race]["abilities"],
                "class_abilities": CLASSES[char_class]["abilities"],
            },
            "created": datetime.now().isoformat(),
            "last_played": datetime.now().isoformat(),
            "history": [],
            "summary": "A new adventure begins…",
        }

        save_json(path, data)
        self.save_file = path
        self.campaign_data = data
        self.character_name = char_name
        print(f"✨ New character '{char_name}' ({race} {char_class}) created!")

    def _generate_random_stats(self) -> dict[str, int]:
        """Generates randomized but balanced stat distribution."""
        stats = {key: 2 for key in DEFAULT_STATS}  # Base 2 in each (10 points)
        remaining = TOTAL_STAT_POINTS - 10

        # Distribute remaining 20 points randomly
        stat_names = list(stats.keys())
        while remaining > 0:
            stat = random.choice(stat_names)
            # Add 1-3 points at a time, but don't exceed remaining
            points = min(random.randint(1, 3), remaining)
            stats[stat] += points
            remaining -= points

        return stats

    def select_or_create_campaign(self) -> None:
        """Interactive campaign selection for CLI mode."""
        os.makedirs(CAMPAIGNS_ROOT, exist_ok=True)

        campaigns = sorted([
            name for name in os.listdir(CAMPAIGNS_ROOT)
            if os.path.isdir(os.path.join(CAMPAIGNS_ROOT, name))
        ])

        print("\n📚 Select a Campaign:\n")

        if campaigns:
            for i, name in enumerate(campaigns, start=1):
                print(f"  {i}. {name}")
        else:
            print("  (no campaigns found)")

        print(f"  {len(campaigns) + 1}. Create new campaign\n")

        choice = prompt_input("Select campaign number:")
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(campaigns):
                self._load_existing_campaign(campaigns[index - 1])
                return
            elif index == len(campaigns) + 1:
                self._create_new_campaign()
                return

        print("❌ Invalid choice. Creating new campaign…")
        self._create_new_campaign()

    def _load_existing_campaign(self, folder_name: str) -> None:
        """Loads an existing campaign from disk."""
        self.current_campaign_folder = os.path.join(CAMPAIGNS_ROOT, folder_name)
        meta_path = os.path.join(self.current_campaign_folder, "campaign.json")
        meta = load_json(meta_path)

        if meta is None:
            print("⚠️ campaign.json missing or corrupted; creating minimal meta.")
            meta = {
                "name": folder_name,
                "theme": "Unknown",
                "description": "",
                "created": datetime.now().isoformat(),
            }
            save_json(meta_path, meta)

        self.campaign_meta = meta
        print(f"\n✨ Loaded campaign: {folder_name}")
        self.select_or_create_character()

    def _create_new_campaign(self) -> None:
        """Creates a new campaign interactively."""
        print("\n📜 Create New Campaign\n")

        name = prompt_input("Campaign Name:")
        if not name:
            print("Campaign name required.")
            return self._create_new_campaign()

        theme = choose_from_list(CAMPAIGN_THEMES, "Choose a campaign theme:")
        if theme == "Other":
            theme = prompt_input("Enter custom theme:")

        description = (
            prompt_input("Short description of the setting/world (one sentence):")
            or f"A {theme} adventure."
        )

        safe_name = sanitize_filename(name)
        folder = os.path.join(CAMPAIGNS_ROOT, safe_name)
        os.makedirs(folder, exist_ok=True)
        self.current_campaign_folder = folder

        meta = {
            "name": name,
            "theme": theme,
            "description": description,
            "created": datetime.now().isoformat(),
            "last_played": datetime.now().isoformat(),
        }

        save_json(os.path.join(folder, "campaign.json"), meta)
        self.campaign_meta = meta

        print(f"\n✨ Campaign '{name}' created with theme '{theme}'!")
        self.select_or_create_character()

    # =========================================================================
    # Character Management
    # =========================================================================

    def select_or_create_character(self) -> None:
        """Interactive character selection for CLI mode."""
        files = os.listdir(self.current_campaign_folder)
        character_files = [
            f for f in files
            if f.startswith("character_") and f.endswith(".json")
        ]

        print("\n🧝 Select Character:\n")

        if character_files:
            for i, filename in enumerate(character_files, start=1):
                path = os.path.join(self.current_campaign_folder, filename)
                data = load_json(path)
                name = data.get("character", {}).get("name", "(corrupted)") if data else "(corrupted)"
                print(f"  {i}. {name}")
        else:
            print("  (no characters found)")

        print(f"  {len(character_files) + 1}. Create new character\n")

        choice = prompt_input("Select character number:")
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(character_files):
                self._load_existing_character(character_files[index - 1])
                return
            elif index == len(character_files) + 1:
                return self._create_new_character()

        print("❌ Invalid choice. Creating new character…")
        return self._create_new_character()

    def _load_existing_character(self, filename: str) -> None:
        """Loads an existing character from disk."""
        path = os.path.join(self.current_campaign_folder, filename)
        data = load_json(path)

        if not data:
            print("⚠️ Character file corrupted. Creating a new one instead.")
            return self._create_new_character()

        self.save_file = path
        self.campaign_data = data
        self.campaign_data.setdefault("history", [])
        self.character_name = data["character"]["name"]

    def _create_new_character(self) -> None:
        """Creates a new character interactively."""
        print("\n🎭 Create New Character\n")

        name = prompt_input("Character Name:")
        if not name:
            print("Name is required.")
            return self._create_new_character()

        race = choose_from_list(list(RACES.keys()), "Choose a race:")
        char_class = choose_from_list(list(CLASSES.keys()), "Choose a class:")
        background = (
            prompt_input("Background (one sentence, optional):")
            or "An adventurer seeking destiny."
        )

        print(f"\nRace Abilities: {', '.join(RACES[race]['abilities'])}")
        print(f"Class Abilities: {', '.join(CLASSES[char_class]['abilities'])}\n")

        stats = self._assign_stats()

        safe_name = sanitize_filename(name)
        filename = f"character_{safe_name}.json"
        path = os.path.join(self.current_campaign_folder, filename)

        self.save_file = path
        self.character_name = name

        data = {
            "character": {
                "name": name,
                "race": race,
                "class": char_class,
                "background": background,
                "stats": stats,
                "race_abilities": RACES[race]["abilities"],
                "class_abilities": CLASSES[char_class]["abilities"],
            },
            "created": datetime.now().isoformat(),
            "last_played": datetime.now().isoformat(),
            "history": [],
            "summary": "A new adventure begins…",
        }

        save_json(path, data)
        self.campaign_data = data
        print(f"\n✨ Character '{name}' created!")

    def _assign_stats(self) -> dict[str, int]:
        """Interactive stat point allocation."""
        print(f"\nAssign {TOTAL_STAT_POINTS} stat points across the following stats:")

        remaining = TOTAL_STAT_POINTS
        stats = DEFAULT_STATS.copy()

        for stat_name in stats:
            while True:
                value_str = prompt_input(f"{stat_name} (remaining {remaining}):")
                if value_str.isdigit():
                    value = int(value_str)
                    if 0 <= value <= remaining:
                        stats[stat_name] = value
                        remaining -= value
                        break
                print("Invalid number. Enter an integer between 0 and remaining points.")

        if remaining > 0:
            print(f"\nDistributing {remaining} unspent points to Strength.")
            stats["Strength"] += remaining

        return stats

    # =========================================================================
    # Persistence
    # =========================================================================

    def save_campaign(self) -> None:
        """Saves the current campaign state to disk."""
        if not self.save_file or not self.campaign_data:
            return

        self.campaign_data["last_played"] = datetime.now().isoformat()
        save_json(self.save_file, self.campaign_data)

    # =========================================================================
    # AI Integration
    # =========================================================================

    def get_dm_system_prompt(self) -> str:
        """
        Generates the system prompt for the DM AI.

        Incorporates campaign theme, description, character info,
        and current story summary.
        """
        campaign = self.campaign_meta or {}
        character = self.campaign_data.get("character", {}) if self.campaign_data else {}
        summary = self.campaign_data.get("summary", "") if self.campaign_data else ""

        theme = campaign.get("theme", "Unknown")
        description = campaign.get("description", "")

        return (
            "You are a concise and vivid D&D 5e Dungeon Master. "
            "**Your response must be no longer than 1 to 2 sentences.** "
            "Write short paragraphs with concrete sensory details. "
            "One of your highest priorities is **MAINTAINING AND BUILDING THE SETTING**: "
            "always incorporate the campaign theme, atmosphere, technology level, culture, "
            "architecture, common dangers, typical NPC attitudes, and tone into your narration. "
            "Use the campaign description and theme to shape NPC behavior, conflicts, "
            "challenges, and scene details. If the players introduce something that "
            "conflicts with the established setting, treat it as a notable anomaly "
            "and hint at consequences or lore.\n\n"
            f"Campaign Theme: {theme}\n"
            f"Campaign Description: {description}\n\n"
            f"Current Summary: {summary}\n"
            f"Player Character: {character.get('name', 'Unknown')} — "
            f"{character.get('race', '')} {character.get('class', '')}\n"
        )

    def _convert_to_gemini_format(
        self, history: list[dict[str, str]]
    ) -> list[types.Content]:
        """Converts message history to Gemini SDK format."""
        contents = []
        for message in history:
            role = "model" if message["role"] == "assistant" else message["role"]
            part = types.Part.from_text(message["content"])
            contents.append(types.Content(role=role, parts=[part]))
        return contents

    def _call_gemini_api(
        self,
        contents: list[types.Content],
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Makes a call to the Gemini API.

        Args:
            contents: The conversation contents.
            max_tokens: Maximum tokens for response.
            system_prompt: Override system prompt.

        Returns:
            The generated response text.
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt or self.get_dm_system_prompt(),
                max_output_tokens=max_tokens or self.config.max_output_tokens,
            ),
        )
        return response.text

    def generate_summary(self) -> str:
        """Generates a summary of recent story events."""
        history = self.campaign_data.get("history", [])
        if not history:
            return "A new adventure begins…"

        if is_interactive_terminal():
            print("\n📖 Generating summary…")

        try:
            recent = history[-self.config.history_context_limit:]
            gemini_messages = self._convert_to_gemini_format(recent)
            gemini_messages.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text("Summarize what happened recently.")]
                )
            )

            system_prompt = (
                "You are a concise D&D DM summarizer. "
                "Produce a tight **one-sentence** recap. **Be extremely brief.**"
            )

            summary = self._call_gemini_api(
                gemini_messages,
                max_tokens=self.config.summary_max_tokens,
                system_prompt=system_prompt,
            ).strip()

            self.campaign_data["summary"] = summary
            self.save_campaign()
            return summary

        except Exception as e:
            if is_interactive_terminal():
                print(f"⚠️ Summary generation failed: {e}")
            return self.campaign_data.get("summary", "Adventure continues…")

    # =========================================================================
    # CLI Game Loop
    # =========================================================================

    def start_adventure(self) -> None:
        """Entry point for CLI gameplay."""
        print("\n🎲 Welcome to your D&D Adventure!")
        self.select_or_create_campaign()

        if self.campaign_data is None:
            print("No character loaded — creating a quick default character.")
            self._create_new_character()

        if self.campaign_data.get("history"):
            print("\n📖 Story so far:")
            print(self.campaign_data.get("summary", "A new adventure begins…"))

        print("\nCommands: status | summary | quit\n")
        self._game_loop()

    def _game_loop(self) -> None:
        """Main CLI game loop."""
        history = self.campaign_data.setdefault("history", [])

        # Generate opening scene if no history
        if not history:
            self._generate_opening_scene(history)

        while True:
            user_input = input("\n⚔️ You: ").strip()
            if not user_input:
                continue

            command = user_input.lower()

            if command in ("quit", "exit"):
                self._handle_quit()
                break

            if command == "status":
                self._show_status()
                continue

            if command == "summary":
                print("\n📖 Summary:\n", self.generate_summary())
                continue

            self._process_player_input(user_input, history)

    def _generate_opening_scene(self, history: list[dict[str, str]]) -> None:
        """Generates and displays the opening scene."""
        print("\n🎭 The DM prepares the opening scene...\n")

        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(
                        "Start the adventure with a short, setting-focused intro."
                    )]
                )
            ]

            dm_text = self._call_gemini_api(contents)
            print(f"🎭 DM: {dm_text}\n")
            history.append({"role": "assistant", "content": dm_text})
            self.save_campaign()

        except Exception as e:
            print(f"❌ Failed to contact DM API: {e}")

    def _process_player_input(
        self,
        user_input: str,
        history: list[dict[str, str]],
    ) -> None:
        """Processes a player's game input."""
        history.append({"role": "user", "content": user_input})

        try:
            gemini_messages = self._convert_to_gemini_format(history)
            dm_text = self._call_gemini_api(gemini_messages)
            print(f"\n🎭 DM: {dm_text}")
            history.append({"role": "assistant", "content": dm_text})
            self.save_campaign()

        except Exception as e:
            print(f"\n❌ Error while contacting DM API: {e}")
            # Rollback user message
            if history and history[-1].get("content") == user_input:
                history.pop()

    def _handle_quit(self) -> None:
        """Handles graceful game exit."""
        print("\n🌙 Saving and exiting…")
        summary = self.generate_summary()
        print("\n📖 Final Summary:\n", summary)
        print("\n👋 Farewell, adventurer.")

    def _show_status(self) -> None:
        """Displays current character status."""
        character = self.campaign_data.get("character", {})

        print("\n📋 CHARACTER STATUS")
        print(f"Name: {character.get('name', 'Unknown')}")
        print(f"Race: {character.get('race', 'Unknown')}")
        print(f"Class: {character.get('class', 'Unknown')}")
        print(f"Background: {character.get('background', '')}\n")

        stats = character.get("stats", {})
        if stats:
            print("Stats:")
            for stat, value in stats.items():
                print(f"  {stat}: {value}")

        print("\nAbilities:")
        print("  Race:", ", ".join(character.get("race_abilities", [])) or "(none)")
        print("  Class:", ", ".join(character.get("class_abilities", [])) or "(none)")
        print()


# =============================================================================
# Entry Point
# =============================================================================


def main() -> None:
    """CLI entry point."""
    dm = DnDDungeonMaster()
    dm.start_adventure()


if __name__ == "__main__":
    main()