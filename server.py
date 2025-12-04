"""
FastAPI server for the D&D Dungeon Master web application.

Provides REST endpoints for game messaging and campaign management,
bridging the web client with the Gemini-powered DM engine.
"""

import os
import traceback
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.genai import types
from pydantic import BaseModel, Field

from cli import DnDDungeonMaster

# =============================================================================
# Application Setup
# =============================================================================

app = FastAPI(
    title="D&D Dungeon Master API",
    description="REST API for the AI-powered Dungeon Master game",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Request/Response Models
# =============================================================================


class MessageRequest(BaseModel):
    """Request model for sending a message to the DM."""

    input: str = Field(..., description="The player's input message")
    campaign_name: str = Field(default="web_campaign", description="Campaign identifier")
    initial: bool = Field(default=False, description="Whether this is the initial game prompt")


class ResetRequest(BaseModel):
    """Request model for resetting a campaign."""

    campaign_name: str = Field(..., description="Campaign identifier to reset")


class MessageResponse(BaseModel):
    """Response model for DM messages."""

    response: str


class ResetResponse(BaseModel):
    """Response model for campaign reset."""

    status: str
    detail: str


# =============================================================================
# DM Instance Management
# =============================================================================

_dm_instances: dict[str, DnDDungeonMaster] = {}


def get_dm_instance(campaign_name: str) -> DnDDungeonMaster:
    """
    Retrieves or creates a DM instance for the specified campaign.

    Args:
        campaign_name: The campaign identifier.

    Returns:
        The DnDDungeonMaster instance for the campaign.

    Raises:
        RuntimeError: If DM initialization fails.
    """
    if campaign_name not in _dm_instances:
        try:
            _dm_instances[campaign_name] = DnDDungeonMaster(campaign_name=campaign_name)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize DM: {e}") from e

    return _dm_instances[campaign_name]


def remove_dm_instance(campaign_name: str) -> None:
    """Removes a DM instance from memory."""
    _dm_instances.pop(campaign_name, None)


# =============================================================================
# Gemini API Helpers
# =============================================================================


def convert_history_to_gemini_format(history: list[dict]) -> list[types.Content]:
    """
    Converts internal message history to Gemini SDK format.

    Args:
        history: List of message dicts with 'role' and 'content' keys.

    Returns:
        List of Gemini Content objects.
    """
    contents = []
    for message in history:
        role = "model" if message["role"] == "assistant" else message["role"]
        text_part = types.Part(text=message["content"])
        contents.append(types.Content(role=role, parts=[text_part]))
    return contents


def generate_dm_response(dm: DnDDungeonMaster, contents: list[types.Content]) -> str:
    """
    Generates a response from the Gemini model.

    Args:
        dm: The DungeonMaster instance.
        contents: The conversation history in Gemini format.

    Returns:
        The generated response text.
    """
    response = dm.client.models.generate_content(
        model=dm.model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=dm.get_dm_system_prompt(),
            max_output_tokens=2048,
        ),
    )
    return response.text


# =============================================================================
# API Endpoints
# =============================================================================


@app.post("/api/message", response_model=MessageResponse)
def send_message(req: MessageRequest) -> MessageResponse:
    """
    Processes a player message and returns the DM's response.

    The endpoint manages conversation history, ensuring proper message
    sequencing for the Gemini API.
    """
    try:
        dm = get_dm_instance(req.campaign_name)
    except RuntimeError as e:
        return MessageResponse(response=f"❌ DM INIT ERROR: {e}")

    # Ensure character exists
    if not dm.campaign_data.get("character"):
        dm.setup_web_character()

    history = dm.campaign_data["history"]

    # Append user input to history (skip for initial setup message)
    if not req.initial:
        history.append({"role": "user", "content": req.input})

    # Prepare messages for Gemini API
    messages_to_send = history.copy()
    if req.initial:
        messages_to_send.append({"role": "user", "content": req.input})

    gemini_contents = convert_history_to_gemini_format(messages_to_send)

    try:
        dm_response = generate_dm_response(dm, gemini_contents)
        history.append({"role": "assistant", "content": dm_response})
        dm.save_campaign()
        return MessageResponse(response=dm_response)

    except Exception as e:
        print("\n--- GEMINI API ERROR ---")
        traceback.print_exc()
        print("------------------------\n")

        # Rollback user message on failure
        if not req.initial and history and history[-1]["role"] == "user":
            history.pop()

        return MessageResponse(
            response=f"❌ API Error: {e}. Check Uvicorn terminal for details."
        )


@app.post("/api/reset", response_model=ResetResponse)
def reset_campaign(req: ResetRequest) -> ResetResponse:
    """
    Fully resets a campaign by removing the entire campaign folder.

    This ensures a completely fresh start with new character, setting,
    and story - preventing repetitive gameplay.
    """
    import shutil

    campaign_dir = os.path.join("campaigns", req.campaign_name)

    # Clear from memory
    remove_dm_instance(req.campaign_name)

    # Check if directory exists
    if not os.path.exists(campaign_dir):
        return ResetResponse(
            status="success",
            detail=f"No folder found at {campaign_dir}, nothing to delete.",
        )

    # Delete entire campaign folder and all contents
    try:
        shutil.rmtree(campaign_dir)
        return ResetResponse(
            status="success",
            detail=f"Completely reset campaign: deleted {campaign_dir} and all contents.",
        )
    except OSError as e:
        return ResetResponse(
            status="error",
            detail=f"Failed to delete campaign folder: {e}",
        )

    # Remove empty directory
    try:
        if not os.listdir(campaign_dir):
            os.rmdir(campaign_dir)
    except OSError:
        pass  # Directory not empty or other issue; ignore

    detail = f"Deleted: {deleted_files}" if deleted_files else "No JSON files found"
    return ResetResponse(status="success", detail=detail)