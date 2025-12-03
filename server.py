from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
# Ensure cli.py is in the same directory and has the DnDDungeonMaster class
from cli import DnDDungeonMaster 
import json
import traceback

app = FastAPI()

# ⚠️ CRITICAL: Allows frontend (5173) to talk to backend (8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to http://localhost:5173
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    input: str
    campaign_name: str = "web_campaign" # Hardcoding campaign name for simplicity

dm_instances = {}

@app.post("/api/message")
def send_message(req: MessageRequest):
    campaign = req.campaign_name
    
    # Initialize DM for the campaign if it doesn't exist
    if campaign not in dm_instances:
        try:
            dm_instances[campaign] = DnDDungeonMaster(campaign_name=campaign)
        except Exception as e:
            # Handle API key missing/load error during initialization
            return {"response": f"❌ DM INIT ERROR: {str(e)}"}
            
    dm = dm_instances[campaign]

    # Handle character setup if it hasn't happened yet (important for first message)
    if not dm.campaign_data.get("character"):
        dm.setup_web_character() # Use a new method for web character setup
        
    
    # 1. Add user message
    dm.campaign_data["history"].append({"role": "user", "content": req.input})
    
    # 2. Call Anthropic API
    try:
        response = dm.client.messages.create(
            model=dm.model,
            max_tokens=2048,
            system=dm.get_dm_system_prompt(),
            messages=dm.campaign_data["history"]
        )
        
        dm_response = response.content[0].text
        
        # 3. Save DM response and campaign state
        dm.campaign_data["history"].append({"role": "assistant", "content": dm_response})
        dm.save_campaign()
        
        return {"response": dm_response}
    
    except Exception as e:
        # 4. Handle API/network errors and log them
        print("\n--- ANTHROPIC API ERROR ---")
        traceback.print_exc()
        print("---------------------------\n")
        
        # If the API call fails, remove the user message so they can try again
        if dm.campaign_data["history"] and dm.campaign_data["history"][-1]["role"] == "user":
            dm.campaign_data["history"].pop() 

        return {"response": f"❌ API Error: {str(e)}. Check Uvicorn terminal for details."}