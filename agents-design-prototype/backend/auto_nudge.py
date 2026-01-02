"""
Automatic nudging module for AgentsDynex
Broadcasts messages to all locations in GPTeam simulation
"""
import asyncio
import json
import os
import sys
from datetime import datetime
from uuid import uuid4

import pytz

# Add GPTeam to Python path
gpteam_path = os.getenv("GPTEAM_PATH")
if gpteam_path:
    sys.path.append(gpteam_path)

try:
    from src.utils.database.client import get_database
    from src.utils.database.base import Tables
    from src.utils.database.sqlite import SqliteDatabase
except ImportError as e:
    print(f"Warning: Could not import GPTeam modules: {e}")
    print(f"Make sure GPTEAM_PATH is set correctly in .env")


async def broadcast_to_all_locations(message: str) -> dict:
    """
    Sends a message to everyone at EVERY location in the GPTeam simulation.
    
    Args:
        message: The message to broadcast to all agents
        
    Returns:
        dict with:
            - success: bool
            - results: list of dicts with location_name, agents_notified, event_id
            - error: str (if success is False)
    """
    print(f"[BROADCAST] Starting broadcast with message: '{message}'")
    database = None
    try:
        # Initialize database with explicit GPTeam path and retry logic
        print("[BROADCAST] Initializing database connection...")
        gpteam_path = os.getenv("GPTEAM_PATH")
        if not gpteam_path:
            return {
                "success": False,
                "error": "GPTEAM_PATH environment variable not set"
            }
        
        db_path = os.path.join(gpteam_path, "database.db")
        print(f"[BROADCAST] Using database path: {db_path}")
        
        # Retry logic for database connection (handles "database is locked" errors)
        max_retries = 3
        retry_delay = 0.5  # seconds
        database = None
        
        for attempt in range(max_retries):
            try:
                database = await SqliteDatabase.create(db_path)
                print(f"[BROADCAST] Database connection established (attempt {attempt + 1})")
                break
            except Exception as e:
                if "locked" in str(e).lower() and attempt < max_retries - 1:
                    print(f"[BROADCAST] Database locked, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    raise
        
        if database is None:
            return {
                "success": False,
                "error": "Failed to connect to database after retries"
            }
        
        print(f"[BROADCAST] Database object: {database}")
        print(f"[BROADCAST] Database type: {type(database)}")
        
        # Get the first world
        print("[BROADCAST] Fetching worlds...")
        worlds = await database.get_all(Tables.Worlds)
        print(f"[BROADCAST] Found {len(worlds)} worlds")
        
        if not worlds:
            await database.close()
            print("[BROADCAST] ERROR: No worlds found")
            return {
                "success": False,
                "error": "No worlds found in GPTeam database"
            }
        
        world_id = worlds[0]["id"]
        print(f"[BROADCAST] Using world_id: {world_id}")
        
        # Get all locations and agents
        print("[BROADCAST] Fetching locations and agents...")
        locations = await database.get_by_field(Tables.Locations, "world_id", str(world_id))
        agents = await database.get_by_field(Tables.Agents, "world_id", str(world_id))
        print(f"[BROADCAST] Found {len(locations)} locations and {len(agents)} agents")
        
        if not locations:
            await database.close()
            print("[BROADCAST] ERROR: No locations found")
            return {
                "success": False,
                "error": "No locations found in GPTeam database"
            }
        
        results = []
        total_agents_notified = 0
        
        # Check if agents exist
        if not agents:
            await database.close()
            print("[BROADCAST] ERROR: No agents found")
            return {
                "success": False,
                "error": "No agents found in GPTeam database"
            }
        
        # Loop through each location and send message to everyone there
        print(f"[BROADCAST] Broadcasting to {len(locations)} locations...")
        for location in locations:
            location_id = location["id"]
            location_name = location["name"]
            
            # Get agents at this location
            agents_at_location = [a for a in agents if a["location_id"] == location_id]
            
            if not agents_at_location:
                # Skip empty locations
                print(f"[BROADCAST] Skipping empty location: {location_name}")
                continue
            
            print(f"[BROADCAST] Sending to {len(agents_at_location)} agents at '{location_name}'")
            
            # Use the first agent at this location as the speaker
            speaker_agent = agents_at_location[0]
            speaker_agent_id = speaker_agent["id"]
            speaker_agent_name = speaker_agent.get("name") or f"{speaker_agent.get('first_name', '')} {speaker_agent.get('last_name', '')}".strip()
            print(f"[BROADCAST] Using agent '{speaker_agent_name}' (ID: {speaker_agent_id}) as speaker")
            
            # Create message event for this location
            event_id = str(uuid4())
            
            event = {
                "id": event_id,
                "agent_id": speaker_agent_id,  # Use real agent ID from simulation
                "type": "message",
                "subtype": "human-agent-reply",
                "description": f"Human said to everyone: '{message}'",
                "location_id": location_id,
                "timestamp": datetime.now(pytz.utc).isoformat(),
                "witness_ids": json.dumps([agent["id"] for agent in agents_at_location]),
                "metadata": json.dumps({"referenced_agent_id": None})  # None for broadcast to everyone
            }
            
            # Insert event into database
            await database.insert(Tables.Events, event)
            print(f"[BROADCAST] Event {event_id} inserted for location '{location_name}'")
            
            results.append({
                "location": location_name,
                "agents_notified": len(agents_at_location),
                "event_id": event_id
            })
            
            total_agents_notified += len(agents_at_location)
        
        # Close database connection
        await database.close()
        print(f"[BROADCAST] SUCCESS: Notified {total_agents_notified} agents across {len(results)} locations")
        
        return {
            "success": True,
            "results": results,
            "total_locations": len(results),
            "total_agents_notified": total_agents_notified,
            "message": message
        }
        
    except Exception as e:
        print(f"[BROADCAST] EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


def send_nudge_sync(message: str) -> dict:
    """
    Synchronous wrapper for broadcast_to_all_locations.
    Used by Flask endpoints.
    
    Args:
        message: The message to broadcast
        
    Returns:
        dict with success status and results
    """
    return asyncio.run(broadcast_to_all_locations(message))


if __name__ == "__main__":
    # Test the function
    test_message = "This is a test message from AgentsDynex auto-nudge system."
    result = send_nudge_sync(test_message)
    print(json.dumps(result, indent=2))
