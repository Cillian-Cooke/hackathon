#!/usr/bin/env python3
"""
Claude D&D Dungeon Master CLI

A CLI tool where Claude acts as your Dungeon Master in D&D campaigns.
Your adventure history is automatically saved between sessions!

Author: Built with Claude for epic adventures
"""

import os
import sys
import json
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DnDDungeonMaster:
    """Claude as your personal D&D Dungeon Master!"""

    def __init__(self, campaign_name="default"):
        """Initialize the Dungeon Master"""
        # Get API key from environment variable
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            print("❌ Error: ANTHROPIC_API_KEY not found!")
            print("\n📝 To fix this:")
            print("1. Copy .env.example to .env")
            print("2. Add your API key from https://console.anthropic.com/")
            print("3. Run this script again")
            sys.exit(1)

        # Create the Claude client
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-haiku-4-5"
        
        # Campaign settings
        self.campaign_name = campaign_name
        self.save_file = f"campaign_{campaign_name}.json"
        
        # Load or create campaign
        self.campaign_data = self.load_campaign()

    def load_campaign(self):
        """Load existing campaign or create a new one"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"\n📜 Loaded campaign: {self.campaign_name}")
                    print(f"🗓️  Last played: {data.get('last_played', 'Unknown')}")
                    print(f"📊 Total messages: {len(data.get('history', []))}")
                    return data
            except Exception as e:
                print(f"⚠️  Could not load campaign: {e}")
                return self.create_new_campaign()
        else:
            print(f"\n✨ Creating new campaign: {self.campaign_name}")
            return self.create_new_campaign()

    def create_new_campaign(self):
        """Create a new campaign data structure"""
        return {
            "campaign_name": self.campaign_name,
            "created": datetime.now().isoformat(),
            "last_played": datetime.now().isoformat(),
            "character": {},
            "history": [],
            "summary": "A new adventure begins..."
        }

    def save_campaign(self):
        """Save campaign to file"""
        try:
            self.campaign_data["last_played"] = datetime.now().isoformat()
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(self.campaign_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save campaign: {e}")

    def get_dm_system_prompt(self):
        """Create the system prompt that makes Claude act as a DM"""
        prompt = """You are an expert Dungeon Master for Dungeons & Dragons 5th Edition. Your role is to:

1. Create immersive, engaging narratives with rich descriptions
2. Follow D&D 5e rules but prioritize fun over rigid rule enforcement
3. Respond to player actions with appropriate consequences
4. Ask for dice rolls when needed (use standard D&D format like "Roll a d20 for Perception")
5. Keep track of important details about the world and story
6. Be creative and adapt to player choices
7. Use vivid descriptions to bring scenes to life
8. Include NPCs with distinct personalities
9. Balance combat, exploration, and roleplay

Style:
- Be descriptive but concise
- Use emotive language to set mood
- Ask clarifying questions if player intent is unclear
- Celebrate creative solutions
- Make failures interesting, not just dead ends

Remember: You're here to help the player have an epic adventure!"""

        # Add campaign context if there's history
        if self.campaign_data["history"]:
            prompt += f"\n\nCampaign Summary: {self.campaign_data['summary']}"
            
            if self.campaign_data.get("character"):
                char = self.campaign_data["character"]
                prompt += f"\n\nPlayer Character: {char.get('name', 'Unknown')} - {char.get('description', 'No description')}"

        return prompt

    def start_adventure(self):
        """Start or continue the D&D adventure"""
        print("\n" + "="*60)
        print("🎲  WELCOME TO YOUR D&D ADVENTURE  🎲")
        print("="*60)
        
        # Character setup if new campaign
        if not self.campaign_data.get("character"):
            self.setup_character()
        else:
            char = self.campaign_data["character"]
            print(f"\n⚔️  Welcome back, {char.get('name', 'Adventurer')}!")
        
        print("\n📖 Commands:")
        print("  - Type your actions naturally")
        print("  - Type 'status' to see your character")
        print("  - Type 'summary' for story recap")
        print("  - Type 'quit' or 'exit' to end session")
        print("\n" + "="*60 + "\n")

        # Start the interactive session
        self.play()

    def setup_character(self):
        """Quick character creation"""
        print("\n🎭 Let's create your character!\n")
        
        name = input("Character Name: ").strip() or "Mysterious Adventurer"
        char_class = input("Class (Fighter/Wizard/Rogue/Cleric/etc.): ").strip() or "Fighter"
        race = input("Race (Human/Elf/Dwarf/etc.): ").strip() or "Human"
        background = input("Brief background (optional): ").strip() or "A brave soul seeking adventure"
        
        self.campaign_data["character"] = {
            "name": name,
            "class": char_class,
            "race": race,
            "description": f"{race} {char_class}",
            "background": background
        }
        
        print(f"\n✨ {name} the {race} {char_class} is ready for adventure!\n")
        self.save_campaign()

    def play(self):
        """Main game loop"""
        history = self.campaign_data["history"]
        
        # If new game, DM introduces the adventure
        if not history:
            print("🎭 Dungeon Master: Let me set the scene...\n")
            
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    system=self.get_dm_system_prompt(),
                    messages=[{
                        "role": "user",
                        "content": "Begin our adventure! Introduce the setting and give me my first choice."
                    }]
                )
                
                dm_response = response.content[0].text
                print(f"🎭 DM: {dm_response}\n")
                
                # Save this opening
                history.append({"role": "user", "content": "Begin our adventure! Introduce the setting and give me my first choice."})
                history.append({"role": "assistant", "content": dm_response})
                self.save_campaign()
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                return

        # Main game loop
        while True:
            user_input = input("\n⚔️  You: ").strip()

            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n🌙 The adventure pauses here... Your progress has been saved!")
                print("👋 Until next time, brave adventurer!")
                self.save_campaign()
                break

            if user_input.lower() == 'status':
                self.show_status()
                continue

            if user_input.lower() == 'summary':
                print(f"\n📖 Campaign Summary:\n{self.campaign_data['summary']}\n")
                continue

            # Add user action to history
            history.append({
                "role": "user",
                "content": user_input
            })

            try:
                # Get DM response
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    system=self.get_dm_system_prompt(),
                    messages=history
                )

                dm_response = response.content[0].text
                
                # Add DM response to history
                history.append({
                    "role": "assistant",
                    "content": dm_response
                })

                # Display response
                print(f"\n🎭 DM: {dm_response}")

                # Save after each exchange
                self.save_campaign()

                # Update summary periodically (every 10 exchanges)
                if len(history) % 20 == 0:
                    self.update_summary()

            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                # Remove the last user message if there was an error
                if history and history[-1]["role"] == "user":
                    history.pop()
                break

    def show_status(self):
        """Display character status"""
        char = self.campaign_data.get("character", {})
        print("\n" + "="*40)
        print("📋 CHARACTER STATUS")
        print("="*40)
        print(f"Name: {char.get('name', 'Unknown')}")
        print(f"Race: {char.get('race', 'Unknown')}")
        print(f"Class: {char.get('class', 'Unknown')}")
        print(f"Background: {char.get('background', 'Unknown')}")
        print("="*40 + "\n")

    def update_summary(self):
        """Generate a summary of recent events"""
        try:
            recent_history = self.campaign_data["history"][-10:]
            
            summary_request = [{
                "role": "user",
                "content": "Provide a brief 2-3 sentence summary of the most important events that have happened in our adventure so far."
            }]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                system="You are a D&D Dungeon Master. Summarize the adventure concisely.",
                messages=recent_history + summary_request
            )
            
            self.campaign_data["summary"] = response.content[0].text
            
        except Exception as e:
            print(f"⚠️  Could not update summary: {e}")


def print_help():
    """Display help information"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║       🎲 D&D Dungeon Master CLI - Help Guide  🎲          ║
╚═══════════════════════════════════════════════════════════╝

📖 Available Commands:

  python cli.py play [campaign_name]
      Start or continue a D&D adventure
      Example: python cli.py play
      Example: python cli.py play dragon_heist

  python cli.py campaigns
      List all saved campaigns

  python cli.py help
      Show this help message

╔═══════════════════════════════════════════════════════════╗
║  🎮 In-Game Commands                                      ║
╚═══════════════════════════════════════════════════════════╝

  status  - View your character sheet
  summary - Get a recap of your adventure
  quit    - Save and exit the game

╔═══════════════════════════════════════════════════════════╗
║  💡 Tips                                                  ║
╚═══════════════════════════════════════════════════════════╝

• Your adventure is automatically saved after each action
• Be descriptive with your actions for better responses
• Claude will ask you to roll dice when needed
• Have fun and be creative!

🎲 May your rolls be high and your adventures epic! 🎲
""")


def list_campaigns():
    """List all saved campaigns"""
    campaigns = [f for f in os.listdir('.') if f.startswith('campaign_') and f.endswith('.json')]
    
    if not campaigns:
        print("\n📭 No saved campaigns found.")
        print("Start a new adventure with: python cli.py play\n")
        return
    
    print("\n📚 Saved Campaigns:\n")
    for campaign_file in campaigns:
        try:
            with open(campaign_file, 'r') as f:
                data = json.load(f)
                name = data.get('campaign_name', 'Unknown')
                last_played = data.get('last_played', 'Unknown')
                messages = len(data.get('history', []))
                char_name = data.get('character', {}).get('name', 'No character')
                
                print(f"  🎲 {name}")
                print(f"     Character: {char_name}")
                print(f"     Last played: {last_played}")
                print(f"     Progress: {messages} messages")
                print()
        except:
            continue


def main():
    """Main entry point for the CLI"""

    # Check if user provided any arguments
    if len(sys.argv) < 2:
        command = 'play'
        campaign_name = 'default'
    else:
        command = sys.argv[1].lower()
        campaign_name = sys.argv[2] if len(sys.argv) > 2 else 'default'

    # Handle help command
    if command in ['help', '-h', '--help']:
        print_help()
        sys.exit(0)

    # Handle campaigns list
    if command == 'campaigns':
        list_campaigns()
        sys.exit(0)

    # Handle play command
    if command == 'play':
        dm = DnDDungeonMaster(campaign_name=campaign_name)
        dm.start_adventure()
    else:
        print(f"\n❌ Error: Unknown command '{command}'")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()