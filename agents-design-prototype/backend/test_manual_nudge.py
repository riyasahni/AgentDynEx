"""
Test file for manual nudging functionality
Tests database operations for getting agents/locations, moving agents, and making agents speak
"""

import asyncio
import sys

# Add GPTeam to path
gpteam_path = "/Users/riya/Desktop/gpteam/GPTeam"
if gpteam_path not in sys.path:
    sys.path.insert(0, gpteam_path)

from manual_nudge import get_agents_and_locations, move_agent, agent_say


async def test_manual_nudge():
    """Test all manual nudging functions"""
    
    print("=" * 80)
    print("TESTING MANUAL NUDGING FUNCTIONALITY")
    print("=" * 80)
    
    # Test 1: Get agents and locations
    print("\n✓ Test 1: Get Agents and Locations")
    result = await get_agents_and_locations()
    
    if "error" in result:
        print(f"  ❌ FAILED: {result['error']}")
        return
    
    print(f"  ✅ SUCCESS: Found {len(result['locations'])} locations")
    for location in result['locations']:
        print(f"    📍 {location['name']}: {len(location['agents'])} agents")
        for agent in location['agents']:
            print(f"       👤 {agent['full_name']}")
    
    # If we have agents and locations, test moving and speaking
    if result['locations'] and any(loc['agents'] for loc in result['locations']):
        # Find first agent and a different location
        first_location = result['locations'][0]
        if first_location['agents']:
            test_agent = first_location['agents'][0]
            agent_id = test_agent['id']
            agent_name = test_agent['full_name']
            
            # Test 2: Make agent say something
            print(f"\n✓ Test 2: Make Agent Say Something")
            print(f"  Agent: {agent_name}")
            test_message = "Hello everyone! This is a test message from manual nudging."
            
            say_result = await agent_say(agent_id, test_message)
            
            if say_result['success']:
                print(f"  ✅ SUCCESS: {say_result['message']}")
            else:
                print(f"  ❌ FAILED: {say_result.get('error', 'Unknown error')}")
            
            # Test 3: Move agent (if there's another location)
            if len(result['locations']) > 1:
                print(f"\n✓ Test 3: Move Agent")
                destination_location = result['locations'][1]
                destination_id = destination_location['id']
                destination_name = destination_location['name']
                
                print(f"  Moving {agent_name} to {destination_name}")
                
                move_result = await move_agent(agent_id, destination_id)
                
                if move_result['success']:
                    print(f"  ✅ SUCCESS: {move_result['message']}")
                else:
                    print(f"  ❌ FAILED: {move_result.get('error', 'Unknown error')}")
                
                # Verify the move by getting agents/locations again
                print(f"\n✓ Test 4: Verify Move")
                verify_result = await get_agents_and_locations()
                
                agent_found = False
                for location in verify_result['locations']:
                    for agent in location['agents']:
                        if agent['id'] == agent_id:
                            print(f"  ✅ Agent {agent_name} is now at: {location['name']}")
                            agent_found = True
                            break
                    if agent_found:
                        break
                
                if not agent_found:
                    print(f"  ❌ Could not find agent after move")
            else:
                print(f"\n⚠️  Test 3 SKIPPED: Only one location available, cannot test move")
        else:
            print(f"\n⚠️  Tests 2-4 SKIPPED: No agents found in first location")
    else:
        print(f"\n⚠️  Tests 2-4 SKIPPED: No agents or locations found")
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_manual_nudge())
