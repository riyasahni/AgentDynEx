"""
Manual Nudging Module for AgentDynEx
Provides functions to manually intervene in GPTeam simulations:
- Get agents and their locations
- Move agents between locations
- Make agents say things
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from uuid import uuid4
import pytz

# Add GPTeam to path
gpteam_path = "/Users/riya/Desktop/gpteam/GPTeam"
if gpteam_path not in sys.path:
    sys.path.insert(0, gpteam_path)

from src.utils.database.client import get_database
from src.utils.database.base import Tables
from src.utils.database.sqlite import SqliteDatabase


async def get_agents_and_locations(world_id: str = None):
    """
    Get all agents grouped by their current locations.
    
    Returns:
        {
            "locations": [
                {
                    "id": "location-uuid",
                    "name": "School Courtyard",
                    "agents": [
                        {"id": "agent-uuid", "full_name": "Bob"},
                        {"id": "agent-uuid", "full_name": "Alice"}
                    ]
                }
            ]
        }
    """
    # Use the correct database path with retry logic
    db_path = "/Users/riya/Desktop/gpteam/GPTeam/database.db"
    max_retries = 3
    retry_delay = 0.5
    database = None
    
    for attempt in range(max_retries):
        try:
            database = await SqliteDatabase.create(db_path)
            break
        except Exception as e:
            if "locked" in str(e).lower() and attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                raise
    
    try:
        # Get the first world if no world_id provided
        if world_id is None:
            worlds = await database.get_all(Tables.Worlds)
            if not worlds:
                return {"error": "No worlds found"}
            world_id = worlds[0]["id"]
        
        # Get all locations and agents for this world
        locations = await database.get_by_field(Tables.Locations, "world_id", str(world_id))
        agents = await database.get_by_field(Tables.Agents, "world_id", str(world_id))
        
        # Group agents by location
        result = {"locations": []}
        
        for location in locations:
            agents_at_location = [
                {
                    "id": str(agent["id"]),
                    "full_name": agent["full_name"]
                }
                for agent in agents
                if str(agent["location_id"]) == str(location["id"])
            ]
            
            result["locations"].append({
                "id": str(location["id"]),
                "name": location["name"],
                "agents": agents_at_location
            })
        
        return result
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        await database.close()


async def move_agent(agent_id: str, destination_location_id: str):
    """
    Move an agent to a different location.
    
    Args:
        agent_id: UUID of the agent to move
        destination_location_id: UUID of the destination location
        
    Returns:
        {"success": True, "message": "Agent moved successfully"}
        or
        {"success": False, "error": "Error message"}
    """
    # Use the correct database path with retry logic
    db_path = "/Users/riya/Desktop/gpteam/GPTeam/database.db"
    max_retries = 3
    retry_delay = 0.5
    database = None
    
    for attempt in range(max_retries):
        try:
            database = await SqliteDatabase.create(db_path)
            break
        except Exception as e:
            if "locked" in str(e).lower() and attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                raise
    
    try:
        # Get the agent
        agent_data = await database.get_by_id(Tables.Agents, str(agent_id))
        if not agent_data or len(agent_data) == 0:
            return {"success": False, "error": "Agent not found"}
        
        agent = agent_data[0]
        old_location_id = agent["location_id"]
        
        # Get location names for events
        old_location = await database.get_by_id(Tables.Locations, str(old_location_id))
        new_location = await database.get_by_id(Tables.Locations, str(destination_location_id))
        
        if not old_location or len(old_location) == 0 or not new_location or len(new_location) == 0:
            return {"success": False, "error": "Location not found"}
        
        old_location_name = old_location[0]["name"]
        new_location_name = new_location[0]["name"]
        
        # Update agent's location
        agent["location_id"] = str(destination_location_id)
        await database.update(Tables.Agents, str(agent_id), agent)
        
        # Create departure event
        departure_event = {
            "id": str(uuid4()),
            "type": "non_message",
            "subtype": None,
            "description": f"{agent['full_name']} left the {old_location_name}",
            "location_id": str(old_location_id),
            "agent_id": str(agent_id),
            "timestamp": datetime.now(pytz.utc).isoformat(),
            "witness_ids": json.dumps([]),
            "metadata": json.dumps({})
        }
        
        # Create arrival event
        arrival_event = {
            "id": str(uuid4()),
            "type": "non_message",
            "subtype": None,
            "description": f"{agent['full_name']} arrived at the {new_location_name}",
            "location_id": str(destination_location_id),
            "agent_id": str(agent_id),
            "timestamp": datetime.now(pytz.utc).isoformat(),
            "witness_ids": json.dumps([]),
            "metadata": json.dumps({})
        }
        
        # Insert events
        await database.insert(Tables.Events, departure_event)
        await database.insert(Tables.Events, arrival_event)
        
        return {
            "success": True,
            "message": f"{agent['full_name']} moved from {old_location_name} to {new_location_name}"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        await database.close()


async def agent_say(agent_id: str, message: str):
    """
    Make an agent say something at their current location.
    All agents at that location will witness the message.
    
    Args:
        agent_id: UUID of the agent who will speak
        message: The message the agent will say
        
    Returns:
        {"success": True, "message": "Agent spoke successfully"}
        or
        {"success": False, "error": "Error message"}
    """
    # Use the correct database path with retry logic
    db_path = "/Users/riya/Desktop/gpteam/GPTeam/database.db"
    max_retries = 3
    retry_delay = 0.5
    database = None
    
    for attempt in range(max_retries):
        try:
            database = await SqliteDatabase.create(db_path)
            break
        except Exception as e:
            if "locked" in str(e).lower() and attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                raise
    
    try:
        # Get the agent
        agent_data = await database.get_by_id(Tables.Agents, str(agent_id))
        if not agent_data or len(agent_data) == 0:
            return {"success": False, "error": "Agent not found"}
        
        agent = agent_data[0]
        location_id = agent["location_id"]
        
        # Get location name
        location_data = await database.get_by_id(Tables.Locations, str(location_id))
        if not location_data or len(location_data) == 0:
            return {"success": False, "error": "Location not found"}
        
        location_name = location_data[0]["name"]
        
        # Get all agents at this location (witnesses)
        all_agents = await database.get_by_field(Tables.Agents, "world_id", str(agent["world_id"]))
        agents_at_location = [
            str(a["id"]) for a in all_agents
            if str(a["location_id"]) == str(location_id)
        ]
        
        # Create message event
        event = {
            "id": str(uuid4()),
            "type": "message",
            "subtype": "human-agent-reply",
            "description": f"{agent['full_name']} said to everyone in the {location_name}: '{message}'",
            "location_id": str(location_id),
            "agent_id": str(agent_id),
            "timestamp": datetime.now(pytz.utc).isoformat(),
            "witness_ids": json.dumps(agents_at_location),
            "metadata": json.dumps({
                "referenced_agent_id": None,
                "priority": "urgent",
                "is_manual_nudge": True,
                "requires_immediate_response": True
            })
        }
        
        # Insert event
        await database.insert(Tables.Events, event)
        
        return {
            "success": True,
            "message": f"{agent['full_name']} said: '{message}'"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        await database.close()


# Synchronous wrappers for Flask
def get_agents_and_locations_sync(world_id: str = None):
    """Synchronous wrapper for get_agents_and_locations"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(get_agents_and_locations(world_id))
        return result
    finally:
        loop.close()


def move_agent_sync(agent_id: str, destination_location_id: str):
    """Synchronous wrapper for move_agent"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(move_agent(agent_id, destination_location_id))
        return result
    finally:
        loop.close()


def agent_say_sync(agent_id: str, message: str):
    """Synchronous wrapper for agent_say"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(agent_say(agent_id, message))
        return result
    finally:
        loop.close()
