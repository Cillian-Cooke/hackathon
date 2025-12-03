#!/usr/bin/env python3
"""
Claude D&D Dungeon Master CLI - Merged Version
Updated to enforce EXTREME MINIMALISM (max_tokens=20) for the absolute shortest outputs.
"""

import os
import sys
import json
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------------------
# DATA TABLES
# ---------------------------

CAMPAIGN_THEMES = [
    "Medieval Fantasy",
    "Steampunk",
    "Post-Apocalyptic",
    "Sci-Fi Galactic",
    "Ancient Mythology",
    "Other"
]

RACES = {
    "Human": {"abilities": ["Adaptable", "Extra Skill Point"]},
    "Elf": {"abilities": ["Darkvision", "Keen Senses"]},
    "Dwarf": {"abilities": ["Resilience", "Stonecunning"]},
    "Orc": {"abilities": ["Savage Strength", "Intimidation"]},
}

CLASSES = {
    "Warrior": {"abilities": ["Power Strike", "Shield Block"]},
    "Mage": {"abilities": ["Spellcasting", "Arcane Shield"]},
    "Rogue": {"abilities": ["Stealth", "Backstab"]},
    "Engineer": {"abilities": ["Gadgeteering", "Mechanical Companion"]},
    "Cleric": {"abilities": ["Divine Heal", "Radiant Smite"]},
    "Other": {"abilities": []}
}

STAT_TEMPLATE = {
    "Strength": 0,
    "Dexterity": 0,
    "Intelligence": 0,
    "Wisdom": 0,
    "Charisma": 0,
}

# ---------------------------
# UTILITIES
# ---------------------------

def ask(prompt):
    """Prompt and strip input."""
    # NOTE: This function is only used in the CLI setup/play loop, not in the web API
    return input(f"{prompt}\n> ").strip()

def choose_list(options, prompt):
    """Present a numbered list of options (list of strings) and return chosen string."""
    # NOTE: This function is only used in the CLI setup/play loop
    print(prompt)
    for i, opt in enumerate(options, start=1):
        print(f"  {i}. {opt}")
    while True:
        choice = ask("Choose by number:")
        if choice.isdigit():
            n = int(choice)
            if 1 <= n <= len(options):
                return options[n - 1]
        print("Invalid choice — try again.")

def safe_filename(s: str) -> str:
    """Make a safe filename from a string."""
    return "".join(c for c in s if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_")

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ---------------------------
# MAIN CLASS
# ---------------------------

class DnDDungeonMaster:
    """D&D CLI with setting-aware DM"""

    def __init__(self, campaign_name="default"):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            # We raise a system exit error only in the CLI context; 
            # in the web server, we let FastAPI catch it.
            if campaign_name == "default":
                 print("❌ Missing ANTHROPIC_API_KEY in environment (.env).")
                 sys.exit(1)
            else:
                 # In web mode, raise an error that FastAPI can catch
                 raise EnvironmentError("ANTHROPIC_API_KEY not set.")


        self.client = Anthropic(api_key=api_key)
        # Using the model name from the second (working) file's __init__ for reliability
        self.model = "claude-sonnet-4-20250514" 

        # State initialization based on new structure
        self.current_campaign_folder = None
        self.campaign_meta = None
        self.character_name = None
        self.save_file = None
        self.campaign_data = None
        
        # --- Web-Compatibility Initialization ---
        if campaign_name and campaign_name != "default":
            self.current_campaign_folder = os.path.join("campaigns", safe_filename(campaign_name))
            os.makedirs(self.current_campaign_folder, exist_ok=True)
            self.load_or_create_web_campaign(campaign_name)
            self.setup_web_character() # Ensures character data exists for initial load


    def load_or_create_web_campaign(self, campaign_name):
        """Initializes campaign meta for web use (single file)"""
        meta_path = os.path.join(self.current_campaign_folder, "campaign.json")
        meta = load_json(meta_path)
        
        if meta is None:
            # Create minimal campaign meta if it doesn't exist
            meta = {
                "name": campaign_name,
                "theme": "Medieval Fantasy",
                "description": "A bustling kingdom on the edge of a wild frontier.",
                "created": datetime.now().isoformat(),
                "last_played": datetime.now().isoformat()
            }
            write_json(meta_path, meta)
        
        self.campaign_meta = meta

    def setup_web_character(self):
        """
        Creates a single, default character file for the web client if none exists.
        """
        web_char_name = "Brave_Web_Adventurer"
        filename = f"character_{web_char_name}.json"
        path = os.path.join(self.current_campaign_folder, filename)

        if os.path.exists(path):
            self.save_file = path
            self.campaign_data = load_json(path)
            # Ensure history key exists for FastAPI logic
            self.campaign_data.setdefault("history", []) 
            self.character_name = self.campaign_data["character"]["name"]
            return # Character already set up

        # Default stats (30 total points)
        default_stats = STAT_TEMPLATE.copy()
        default_stats.update({
            "Strength": 10,
            "Dexterity": 8,
            "Intelligence": 5,
            "Wisdom": 5,
            "Charisma": 2,
        })

        data = {
            "character": {
                "name": web_char_name.replace("_", " "),
                "race": "Human",
                "class": "Warrior",
                "background": "An adventurer who arrived via a magic portal (the web browser).",
                "stats": default_stats,
                "race_abilities": RACES["Human"]["abilities"],
                "class_abilities": CLASSES["Warrior"]["abilities"],
            },
            "created": datetime.now().isoformat(),
            "last_played": datetime.now().isoformat(),
            "history": [],
            "summary": "A new adventure begins…"
        }

        write_json(path, data)
        self.save_file = path
        self.campaign_data = data
        self.character_name = data["character"]["name"]
        print(f"✨ Web Character '{self.character_name}' initialized.")


    # ---------------------------
    # Campaign management (CLI only)
    # ---------------------------

    def select_or_create_campaign(self):
        root = "campaigns"
        os.makedirs(root, exist_ok=True)

        campaigns = sorted(
            [name for name in os.listdir(root) if os.path.isdir(os.path.join(root, name))]
        )

        print("\n📚 Select a Campaign:\n")

        if campaigns:
            for i, name in enumerate(campaigns, start=1):
                print(f"  {i}. {name}")
        else:
            print("  (no campaigns found)")

        print(f"  {len(campaigns) + 1}. Create new campaign\n")

        choice = ask("Select campaign number:")
        if choice.isdigit():
            n = int(choice)
            if 1 <= n <= len(campaigns):
                folder_name = campaigns[n - 1]
                self.current_campaign_folder = os.path.join(root, folder_name)
                meta = load_json(os.path.join(self.current_campaign_folder, "campaign.json"))
                if meta is None:
                    print("⚠️ campaign.json missing or corrupted; creating a minimal meta.")
                    meta = {"name": folder_name, "theme": "Unknown", "description": "", "created": datetime.now().isoformat()}
                    write_json(os.path.join(self.current_campaign_folder, "campaign.json"), meta)
                self.campaign_meta = meta
                print(f"\n✨ Loaded campaign: {folder_name}")
                self.select_or_create_character()
                return
            elif n == len(campaigns) + 1:
                self.create_new_campaign()
                return

        # fallback
        print("❌ Invalid choice. Creating new campaign…")
        self.create_new_campaign()

    def create_new_campaign(self):
        root = "campaigns"
        os.makedirs(root, exist_ok=True)

        print("\n📜 Create New Campaign\n")
        name = ask("Campaign Name:")
        if not name:
            print("Campaign name required.")
            return self.create_new_campaign()

        theme = choose_list(CAMPAIGN_THEMES, "Choose a campaign theme:")
        if theme == "Other":
            theme = ask("Enter custom theme:")

        description = ask("Short description of the setting/world (one sentence):") or f"A {theme} adventure."

        safe = safe_filename(name)
        folder = os.path.join(root, safe)
        os.makedirs(folder, exist_ok=True)
        self.current_campaign_folder = folder

        meta = {
            "name": name,
            "theme": theme,
            "description": description,
            "created": datetime.now().isoformat(),
            "last_played": datetime.now().isoformat()
        }

        write_json(os.path.join(folder, "campaign.json"), meta)
        self.campaign_meta = meta

        print(f"\n✨ Campaign '{name}' created with theme '{theme}'!")
        self.select_or_create_character()

    # ---------------------------
    # Character management (CLI only)
    # ---------------------------

    def select_or_create_character(self):
        files = os.listdir(self.current_campaign_folder)
        character_files = [f for f in files if f.startswith("character_") and f.endswith(".json")]

        print("\n🧝 Select Character:\n")
        if character_files:
            for i, fname in enumerate(character_files, start=1):
                full = os.path.join(self.current_campaign_folder, fname)
                data = load_json(full)
                if data and "character" in data and "name" in data["character"]:
                    print(f"  {i}. {data['character']['name']}")
                else:
                    print(f"  {i}. (corrupted file)")
        else:
            print("  (no characters found)")

        print(f"  {len(character_files) + 1}. Create new character\n")

        choice = ask("Select character number:")
        if choice.isdigit():
            n = int(choice)
            if 1 <= n <= len(character_files):
                filename = character_files[n - 1]
                full = os.path.join(self.current_campaign_folder, filename)
                data = load_json(full)
                if not data:
                    print("⚠️ Character file corrupted. Creating a new one instead.")
                    return self.create_new_character()
                self.save_file = full
                self.campaign_data = data
                self.campaign_data.setdefault("history", []) # Ensure history exists
                self.character_name = data["character"]["name"]
                return
            elif n == len(character_files) + 1:
                return self.create_new_character()

        print("❌ Invalid choice. Creating new character…")
        return self.create_new_character()

    def create_new_character(self):
        print("\n🎭 Create New Character\n")
        name = ask("Character Name:")
        if not name:
            print("Name is required.")
            return self.create_new_character()

        race = choose_list(list(RACES.keys()), "Choose a race:")
        clazz = choose_list(list(CLASSES.keys()), "Choose a class:")
        background = ask("Background (one sentence, optional):") or "An adventurer seeking destiny."

        print(f"\nRace Abilities: {', '.join(RACES[race]['abilities'])}")
        print(f"Class Abilities: {', '.join(CLASSES[clazz]['abilities'])}\n")

        stats = self.assign_stats()

        safe = safe_filename(name)
        filename = f"character_{safe}.json"
        path = os.path.join(self.current_campaign_folder, filename)

        self.save_file = path
        self.character_name = name

        data = {
            "character": {
                "name": name,
                "race": race,
                "class": clazz,
                "background": background,
                "stats": stats,
                "race_abilities": RACES[race]["abilities"],
                "class_abilities": CLASSES[clazz]["abilities"],
            },
            "created": datetime.now().isoformat(),
            "last_played": datetime.now().isoformat(),
            "history": [],
            "summary": "A new adventure begins…"
        }

        write_json(path, data)
        self.campaign_data = data

        print(f"\n✨ Character '{name}' created!")

    def assign_stats(self):
        print("\nAssign 30 stat points across the following stats:")
        remaining = 30
        stats = STAT_TEMPLATE.copy()

        for s in stats:
            while True:
                v = ask(f"{s} (remaining {remaining}):")
                if v.isdigit():
                    v_int = int(v)
                    if 0 <= v_int <= remaining:
                        stats[s] = v_int
                        remaining -= v_int
                        break
                print("Invalid number. Enter an integer between 0 and remaining points.")
        if remaining > 0:
            print(f"\nYou have {remaining} unspent points; they will be distributed as +1 to Strength until used.")
            # distribute remaining to Strength
            stats["Strength"] += remaining
        return stats

    # ---------------------------
    # Save & summary
    # ---------------------------

    def save_campaign(self):
        if not self.save_file or not self.campaign_data:
            return
        self.campaign_data["last_played"] = datetime.now().isoformat()
        write_json(self.save_file, self.campaign_data)

    def generate_summary(self):
        history = self.campaign_data.get("history", [])
        if not history:
            return "A new adventure begins…"

        # Only print 'Generating summary' in CLI mode
        if os.environ.get('TERM', '').startswith('xterm') or sys.stdin.isatty():
             print("\n📖 Generating summary…")
             
        try:
            recent = history[-25:]
            # build a focused system prompt for summarization
            system_prompt = (
                "You are a concise D&D DM summarizer. Produce a tight **one-sentence** recap. **Be extremely brief.**"
            )
            response = self.client.messages.create(
                model=self.model,
                max_tokens=20, # ⬅️ FINAL CHANGE: max_tokens reduced to 20
                system=system_prompt,
                messages=recent + [{"role": "user", "content": "Summarize what happened recently."}]
            )
            summary = response.content[0].text.strip()
            self.campaign_data["summary"] = summary
            self.save_campaign()
            return summary
        except Exception as e:
            # Only print error in CLI mode
            if os.environ.get('TERM', '').startswith('xterm') or sys.stdin.isatty():
                 print("⚠️ Summary generation failed:", e)
            return self.campaign_data.get("summary", "Adventure continues…")

    # ---------------------------
    # DM System prompt (SETTING-AWARE)
    # ---------------------------

    def get_dm_system_prompt(self):
        # Guard rails: campaign_meta may be missing
        campaign = self.campaign_meta or {}
        char = self.campaign_data.get("character", {}) if self.campaign_data else {}
        summary = self.campaign_data.get("summary", "") if self.campaign_data else ""

        campaign_theme = campaign.get("theme", "Unknown")
        campaign_desc = campaign.get("description", "")

        # ⚠️ CRITICAL CHANGE: System prompt insists on 1-2 sentences only
        return (
            "You are a concise and vivid D&D 5e Dungeon Master. **Your response must be no longer than 1 to 2 sentences.** "
            "Write short paragraphs with concrete sensory details. One of your highest priorities is **MAINTAINING AND BUILDING THE SETTING**: "
            "always incorporate the campaign theme, atmosphere, technology level, culture, architecture, "
            "common dangers, typical NPC attitudes, and tone into your narration. "
            "Use the campaign description and theme to shape NPC behavior, conflicts, challenges, and scene details. "
            "If the players introduce something that conflicts with the established setting, treat it as a notable anomaly "
            "and hint at consequences or lore.\n\n"
            f"Campaign Theme: {campaign_theme}\n"
            f"Campaign Description: {campaign_desc}\n\n"
            f"Current Summary: {summary}\n"
            f"Player Character: {char.get('name', 'Unknown')} — {char.get('race','')} {char.get('class','')}\n"
        )

    # ---------------------------
    # Game loop (CLI only)
    # ---------------------------

    def start_adventure(self):
        print("\n🎲 Welcome to your D&D Adventure!")
        self.select_or_create_campaign()

        # Load an empty campaign_data if none (shouldn't happen but safe)
        if self.campaign_data is None:
            # create a fallback character
            print("No character loaded — creating a quick default character.")
            self.create_new_character()

        if self.campaign_data.get("history"):
            print("\n📖 Story so far:")
            print(self.campaign_data.get("summary", "A new adventure begins…"))

        print("\nCommands: status | summary | quit\n")
        self.play()

    def play(self):
        history = self.campaign_data.setdefault("history", [])

        # ⚠️ FIX APPLIED HERE for CLI mode: Fresh intro if no history is outside the while loop
        if not history:
            print("\n🎭 The DM prepares the opening scene...\n")
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=20, # ⬅️ FINAL CHANGE: max_tokens reduced to 20
                    system=self.get_dm_system_prompt(),
                    messages=[{"role": "user", "content": "Start the adventure with a short, setting-focused intro."}]
                )
                dm_text = response.content[0].text
                print(f"🎭 DM: {dm_text}\n")
                history.append({"role": "assistant", "content": dm_text})
                self.save_campaign()
            except Exception as e:
                print("❌ Failed to contact DM API:", e)
                return

        # Main interaction loop
        while True:
            user_input = input("\n⚔️ You: ").strip()
            if not user_input:
                continue

            cmd = user_input.lower().strip()
            if cmd in ("quit", "exit"):
                print("\n🌙 Saving and exiting…")
                summary = self.generate_summary()
                print("\n📖 Final Summary:\n", summary)
                print("\n👋 Farewell, adventurer.")
                break

            if cmd == "status":
                self.show_status()
                continue

            if cmd == "summary":
                print("\n📖 Summary:\n", self.generate_summary())
                continue

            # Regular gameplay input appended to history
            history.append({"role": "user", "content": user_input})

            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=20, # ⬅️ FINAL CHANGE: max_tokens reduced to 20
                    system=self.get_dm_system_prompt(),
                    messages=history
                )
                dm_text = response.content[0].text
                print(f"\n🎭 DM: {dm_text}")
                history.append({"role": "assistant", "content": dm_text})
                self.save_campaign()
            except Exception as e:
                print("\n❌ Error while contacting DM API:", e)
                # rollback user message to avoid corrupt history
                if history and history[-1].get("role") == "user" and history[-1].get("content") == user_input:
                    history.pop()
                break

    # ---------------------------
    # Status screen
    # ---------------------------

    def show_status(self):
        char = self.campaign_data.get("character", {})
        print("\n📋 CHARACTER STATUS")
        print(f"Name: {char.get('name', 'Unknown')}")
        print(f"Race: {char.get('race', 'Unknown')}")
        print(f"Class: {char.get('class', 'Unknown')}")
        print(f"Background: {char.get('background', '')}\n")
        stats = char.get("stats", {})
        if stats:
            print("Stats:")
            for k, v in stats.items():
                print(f"  {k}: {v}")
        print("\nAbilities:")
        print("  Race:", ", ".join(char.get("race_abilities", [])) or "(none)")
        print("  Class:", ", ".join(char.get("class_abilities", [])) or "(none)")
        print("")

# ---------------------------
# ENTRY POINT
# ---------------------------

def main():
    # This main function is only for the CLI usage
    dm = DnDDungeonMaster()
    dm.start_adventure()

if __name__ == "__main__":
    main()