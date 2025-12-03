from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from cli import DnDDungeonMaster 
import json
import traceback
import os
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    input: str
    campaign_name: str = "web_campaign"
    initial: bool = False

class ResetRequest(BaseModel):
    campaign_name: str

dm_instances = {}

@app.post("/api/message")
def send_message(req: MessageRequest):
    campaign = req.campaign_name
    
    if campaign not in dm_instances:
        try:
            dm_instances[campaign] = DnDDungeonMaster(campaign_name=campaign)
        except Exception as e:
            return {"response": f"❌ DM INIT ERROR: {str(e)}"}
            
    dm = dm_instances[campaign]
    
    if not dm.campaign_data.get("character"):
        dm.setup_web_character()

    if not req.initial:
        dm.campaign_data["history"].append({"role": "user", "content": req.input})
    
    messages_to_send = dm.campaign_data["history"].copy()
    
    if req.initial:
        messages_to_send.append({"role": "user", "content": req.input})
    
    try:
        response = dm.client.messages.create(
            model=dm.model,
            max_tokens=2048,
            system=dm.get_dm_system_prompt(),
            messages=messages_to_send
        )
        
        dm_response = response.content[0].text
        
        dm.campaign_data["history"].append({"role": "assistant", "content": dm_response})
        dm.save_campaign()
        
        return {"response": dm_response}
    
    except Exception as e:
        print("\n--- ANTHROPIC API ERROR ---")
        traceback.print_exc()
        print("---------------------------\n")
        
        if not req.initial and dm.campaign_data["history"] and dm.campaign_data["history"][-1]["role"] == "user":
            dm.campaign_data["history"].pop() 

        return {"response": f"❌ API Error: {str(e)}. Check Uvicorn terminal for details."}



@app.post("/api/reset")
def reset_campaign(req: ResetRequest):
    campaign = req.campaign_name

    # 1. Remove DM from memory
    if campaign in dm_instances:
        del dm_instances[campaign]

    # 2. Compute folder path
    campaign_dir = os.path.join("campaigns", campaign)

    if not os.path.exists(campaign_dir):
        return {
            "status": "success",
            "detail": f"No folder found at {campaign_dir}, nothing to delete."
        }

    deleted_files = []

    # 3. Delete only JSON files inside this directory
    for file in os.listdir(campaign_dir):
        if file.endswith(".json"):
            full_path = os.path.join(campaign_dir, file)
            try:
                os.remove(full_path)
                deleted_files.append(full_path)
            except Exception as e:
                return {
                    "status": "error",
                    "detail": f"Failed to delete {full_path}: {str(e)}"
                }

    # 4. Delete folder if it's now empty
    try:
        if not os.listdir(campaign_dir):
            os.rmdir(campaign_dir)
    except Exception as e:
        pass  # folder might not be empty, that's fine

    return {
        "status": "success",
        "detail": f"Deleted: {deleted_files if deleted_files else 'No JSON files found'}"
    }
