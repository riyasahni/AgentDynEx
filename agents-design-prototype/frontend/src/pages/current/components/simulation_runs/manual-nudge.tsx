import React, { useState, useEffect } from 'react';
import { colors } from '../../../../theme/colors';
import Button from '../../../../components/Button';
import TextField from '../../../../components/TextField';

interface Agent {
  id: string;
  full_name: string;
}

interface Location {
  id: string;
  name: string;
  agents: Agent[];
}

interface AgentsLocationsData {
  locations: Location[];
}

type TabType = 'move' | 'say';

const ManualNudgePanel: React.FC = () => {
  const [data, setData] = useState<AgentsLocationsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>('move');
  
  // Move tab state
  const [selectedAgents, setSelectedAgents] = useState<Set<string>>(new Set());
  const [selectedLocation, setSelectedLocation] = useState<string>('');
  const [moveMessage, setMoveMessage] = useState<string>('');
  
  // Say tab state
  const [selectedSpeaker, setSelectedSpeaker] = useState<string>('');
  const [message, setMessage] = useState<string>('');
  const [sayMessage, setSayMessage] = useState<string>('');

  // Fetch agents and locations
  const fetchAgentsLocations = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/manual_nudge/get_agents_locations');
      const result = await response.json();
      if (!result.error) {
        setData(result);
      }
    } catch (error) {
      console.error('Error fetching agents/locations:', error);
    }
  };

  useEffect(() => {
    fetchAgentsLocations();
    // Refresh every 5 seconds
    const interval = setInterval(fetchAgentsLocations, 5000);
    return () => clearInterval(interval);
  }, []);

  // Handle move agent
  const handleMove = async () => {
    if (selectedAgents.size === 0 || !selectedLocation) {
      setMoveMessage('Please select at least one agent and a destination location');
      return;
    }

    setLoading(true);
    setMoveMessage('');

    try {
      const promises = Array.from(selectedAgents).map(agentId =>
        fetch('http://127.0.0.1:5000/manual_nudge/move_agent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agent_id: agentId,
            destination_location_id: selectedLocation
          })
        }).then(res => res.json())
      );

      const results = await Promise.all(promises);
      const successCount = results.filter(r => r.success).length;
      
      setMoveMessage(`✅ Successfully moved ${successCount} agent(s)`);
      setSelectedAgents(new Set());
      setSelectedLocation('');
      
      // Refresh data
      await fetchAgentsLocations();
    } catch (error) {
      setMoveMessage('❌ Error moving agent(s)');
    } finally {
      setLoading(false);
    }
  };

  // Handle agent say
  const handleSay = async () => {
    if (!selectedSpeaker || !message.trim()) {
      setSayMessage('Please select an agent and enter a message');
      return;
    }

    setLoading(true);
    setSayMessage('');

    try {
      const response = await fetch('http://127.0.0.1:5000/manual_nudge/agent_say', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: selectedSpeaker,
          message: message
        })
      });

      const result = await response.json();
      
      if (result.success) {
        setSayMessage(`✅ ${result.message}`);
        setMessage('');
        setSelectedSpeaker('');
      } else {
        setSayMessage(`❌ ${result.error}`);
      }
    } catch (error) {
      setSayMessage('❌ Error sending message');
    } finally {
      setLoading(false);
    }
  };

  // Toggle agent selection
  const toggleAgent = (agentId: string) => {
    const newSelected = new Set(selectedAgents);
    if (newSelected.has(agentId)) {
      newSelected.delete(agentId);
    } else {
      newSelected.add(agentId);
    }
    setSelectedAgents(newSelected);
  };

  // Get all agents for "say" tab
  const allAgents = data?.locations.flatMap(loc => loc.agents) || [];

  return (
    <div style={{
      backgroundColor: colors.white,
      borderRadius: '8px',
      padding: '20px',
      marginBottom: '20px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <h3 style={{ 
        margin: '0 0 20px 0', 
        color: colors.darkTeal,
        fontSize: '18px',
        fontWeight: 'bold'
      }}>
        Manual Nudging
      </h3>

      <div style={{ display: 'flex', gap: '20px' }}>
        {/* Left Panel: Current Locations */}
        <div style={{ flex: 1, minWidth: '300px' }}>
          <h4 style={{ 
            margin: '0 0 15px 0', 
            color: colors.darkBlue,
            fontSize: '16px'
          }}>
            📍 Current Locations
          </h4>
          
          <div style={{ 
            maxHeight: '400px', 
            overflowY: 'auto',
            border: `1px solid ${colors.teal}`,
            borderRadius: '4px',
            padding: '10px'
          }}>
            {data?.locations.map(location => (
              <div key={location.id} style={{ marginBottom: '15px' }}>
                <div style={{ 
                  fontWeight: 'bold', 
                  color: colors.darkTeal,
                  marginBottom: '5px'
                }}>
                  {location.name} ({location.agents.length})
                </div>
                {location.agents.map(agent => (
                  <div key={agent.id} style={{ 
                    marginLeft: '15px', 
                    color: colors.brown,
                    fontSize: '14px'
                  }}>
                    👤 {agent.full_name}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Right Panel: Manual Intervention */}
        <div style={{ flex: 1, minWidth: '300px' }}>
          <h4 style={{ 
            margin: '0 0 15px 0', 
            color: colors.darkBlue,
            fontSize: '16px'
          }}>
            🎮 Manual Intervention
          </h4>

          {/* Tabs */}
          <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
            <button
              onClick={() => setActiveTab('move')}
              style={{
                flex: 1,
                padding: '10px',
                backgroundColor: activeTab === 'move' ? colors.primary : colors.white,
                color: activeTab === 'move' ? colors.white : colors.darkTeal,
                border: `2px solid ${colors.primary}`,
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '14px'
              }}
            >
              MOVE
            </button>
            <button
              onClick={() => setActiveTab('say')}
              style={{
                flex: 1,
                padding: '10px',
                backgroundColor: activeTab === 'say' ? colors.primary : colors.white,
                color: activeTab === 'say' ? colors.white : colors.darkTeal,
                border: `2px solid ${colors.primary}`,
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '14px'
              }}
            >
              AGENT SAYS
            </button>
          </div>

          {/* Move Tab Content */}
          {activeTab === 'move' && (
            <div>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '8px',
                  color: colors.darkTeal,
                  fontWeight: 'bold',
                  fontSize: '14px'
                }}>
                  Select Agents to Move:
                </label>
                <div style={{ 
                  maxHeight: '150px', 
                  overflowY: 'auto',
                  border: `1px solid ${colors.teal}`,
                  borderRadius: '4px',
                  padding: '10px'
                }}>
                  {allAgents.map(agent => (
                    <label key={agent.id} style={{ 
                      display: 'block', 
                      marginBottom: '5px',
                      cursor: 'pointer'
                    }}>
                      <input
                        type="checkbox"
                        checked={selectedAgents.has(agent.id)}
                        onChange={() => toggleAgent(agent.id)}
                        style={{ marginRight: '8px' }}
                      />
                      {agent.full_name}
                    </label>
                  ))}
                </div>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '8px',
                  color: colors.darkTeal,
                  fontWeight: 'bold',
                  fontSize: '14px'
                }}>
                  Destination Location:
                </label>
                <select
                  value={selectedLocation}
                  onChange={(e) => setSelectedLocation(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: `1px solid ${colors.teal}`,
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}
                >
                  <option value="">-- Select Location --</option>
                  {data?.locations.map(location => (
                    <option key={location.id} value={location.id}>
                      {location.name}
                    </option>
                  ))}
                </select>
              </div>

              <Button
                onClick={handleMove}
                disabled={loading || selectedAgents.size === 0 || !selectedLocation}
                colorVariant="primary"
                style={{
                  width: '100%',
                  padding: '12px',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}
              >
                {loading ? 'MOVING...' : 'SUBMIT MOVE'}
              </Button>

              {moveMessage && (
                <div style={{ 
                  marginTop: '10px', 
                  padding: '10px',
                  backgroundColor: moveMessage.includes('✅') ? colors.lightGreen : colors.lightOrange,
                  borderRadius: '4px',
                  fontSize: '14px'
                }}>
                  {moveMessage}
                </div>
              )}
            </div>
          )}

          {/* Say Tab Content */}
          {activeTab === 'say' && (
            <div>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '8px',
                  color: colors.darkTeal,
                  fontWeight: 'bold',
                  fontSize: '14px'
                }}>
                  Select Agent to Speak:
                </label>
                <div style={{ 
                  maxHeight: '150px', 
                  overflowY: 'auto',
                  border: `1px solid ${colors.teal}`,
                  borderRadius: '4px',
                  padding: '10px'
                }}>
                  {allAgents.map(agent => (
                    <label key={agent.id} style={{ 
                      display: 'block', 
                      marginBottom: '5px',
                      cursor: 'pointer'
                    }}>
                      <input
                        type="radio"
                        name="speaker"
                        checked={selectedSpeaker === agent.id}
                        onChange={() => setSelectedSpeaker(agent.id)}
                        style={{ marginRight: '8px' }}
                      />
                      {agent.full_name}
                    </label>
                  ))}
                </div>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '8px',
                  color: colors.darkTeal,
                  fontWeight: 'bold',
                  fontSize: '14px'
                }}>
                  Message:
                </label>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Enter what the agent should say..."
                  style={{
                    width: '100%',
                    minHeight: '100px',
                    padding: '8px',
                    border: `1px solid ${colors.teal}`,
                    borderRadius: '4px',
                    fontSize: '14px',
                    fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                />
              </div>

              <Button
                onClick={handleSay}
                disabled={loading || !selectedSpeaker || !message.trim()}
                colorVariant="primary"
                style={{
                  width: '100%',
                  padding: '12px',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}
              >
                {loading ? 'SENDING...' : 'SUBMIT STATEMENT'}
              </Button>

              {sayMessage && (
                <div style={{ 
                  marginTop: '10px', 
                  padding: '10px',
                  backgroundColor: sayMessage.includes('✅') ? colors.lightGreen : colors.lightOrange,
                  borderRadius: '4px',
                  fontSize: '14px'
                }}>
                  {sayMessage}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ManualNudgePanel;
