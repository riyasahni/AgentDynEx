import React, { useEffect, useState } from "react";
import { Stack, Typography, Divider, Switch, Box } from "@mui/material";
import axios from "axios";
import { SERVER_URL } from "../..";
import { useAppContext } from "../../hooks/app-context";
import ChangeLog from "./change-log";
import Dynamics from "./dynamics-table";
import ManualNudgePanel from "./manual-nudge";
import TextField from "../../../../components/TextField";
import Button from "../../../../components/Button";
import { ExpandLess, ExpandMore } from "@mui/icons-material";

const ContinuousData = ({ parentExpand }: { parentExpand: boolean }) => {
  const [expand, setExpand] = useState(parentExpand);

  const [status, setStatus] = useState("");
  const [dynamicReflection, setDynamicReflection] = useState("");
  
  // Auto-nudge state
  const [autoNudgeEnabled, setAutoNudgeEnabled] = useState(false);
  const [lastNudgeTime, setLastNudgeTime] = useState<number | null>(null);
  const [cooldownRemaining, setCooldownRemaining] = useState(0);
  const [lastNudgeStatus, setLastNudgeStatus] = useState<any>(null);
  const [isExecutingNudge, setIsExecutingNudge] = useState(false);

  const { isRunningSimulation, currentPrototype, currentRunId } =
    useAppContext();
  const getStatus = () => {
    // updateIsLoading(true);
    axios({
      method: "GET",
      url: `${SERVER_URL}/get_status`,
    })
      .then((response) => {
        console.log("/get_status request successful:", response.data);
        setStatus(response.data.status);
      })
      .catch((error) => {
        console.error("Error calling /get_status request:", error);
      })
      .finally(() => {
        // updateIsLoading(false);
      });
  };

  const getDynamicReflection = () => {
    // updateIsLoading(true);
    axios({
      method: "GET",
      url: `${SERVER_URL}/get_dynamic_reflection`,
    })
      .then((response) => {
        console.log(
          "/get_dynamic_reflection request successful:",
          response.data,
        );
        setDynamicReflection(response.data.dynamic_reflection);
      })
      .catch((error) => {
        console.error("Error calling /get_dynamic_reflection request:", error);
      })
      .finally(() => {
        // updateIsLoading(false);
      });
  };

  useEffect(() => {
    if (isRunningSimulation && expand) {
      const statusIntervalId = setInterval(getStatus, 30000);
      const reflectionIntervalId = setInterval(getDynamicReflection, 60005);

      return () => {
        clearInterval(statusIntervalId);
        clearInterval(reflectionIntervalId);
      };
    }
  }, [isRunningSimulation, expand]);

  useEffect(() => {
    setStatus("");
    setDynamicReflection("");
    setAutoNudgeEnabled(false);
    setLastNudgeTime(null);
    setLastNudgeStatus(null);
  }, [currentPrototype, currentRunId]);

  // Auto-nudge functions
  const toggleAutoNudge = () => {
    const newStatus = !autoNudgeEnabled;
    setAutoNudgeEnabled(newStatus);
    
    axios({
      method: "POST",
      url: `${SERVER_URL}/set_auto_nudge_status`,
      data: { enabled: newStatus },
    })
      .then((response) => {
        console.log("/set_auto_nudge_status successful:", response.data);
      })
      .catch((error) => {
        console.error("Error calling /set_auto_nudge_status:", error);
      });
  };

  const executeNudge = (manual: boolean = false) => {
    if (isExecutingNudge) return;
    
    // Check if there's a "say" command in dynamic reflection
    const hasSayCommand = dynamicReflection.toLowerCase().includes("say");
    if (!hasSayCommand) {
      console.log("No 'say' command found in dynamic reflection");
      return;
    }

    // Check cooldown
    if (lastNudgeTime) {
      const timeSinceLastNudge = (Date.now() - lastNudgeTime) / 1000;
      if (timeSinceLastNudge < 45) {
        console.log(`Cooldown active: ${45 - Math.floor(timeSinceLastNudge)}s remaining`);
        if (manual) {
          alert(`Please wait ${45 - Math.floor(timeSinceLastNudge)} more seconds before nudging again`);
        }
        return;
      }
    }

    setIsExecutingNudge(true);
    
    axios({
      method: "POST",
      url: `${SERVER_URL}/execute_auto_nudge`,
      data: { dynamic_reflection: dynamicReflection },
    })
      .then((response) => {
        console.log("/execute_auto_nudge successful:", response.data);
        if (response.data.success) {
          setLastNudgeTime(Date.now());
          setLastNudgeStatus(response.data);
        } else {
          console.error("Nudge failed:", response.data.error);
        }
      })
      .catch((error) => {
        console.error("Error calling /execute_auto_nudge:", error);
      })
      .finally(() => {
        setIsExecutingNudge(false);
      });
  };

  // Auto-execute nudge when conditions are met
  useEffect(() => {
    if (autoNudgeEnabled && dynamicReflection && isRunningSimulation) {
      // Check if there's a "say" command
      const hasSayCommand = dynamicReflection.toLowerCase().includes("say");
      if (!hasSayCommand) return;

      // Check if it's not "running smoothly"
      if (dynamicReflection === "Simulation is running smoothly.") return;

      // Check cooldown
      if (lastNudgeTime) {
        const timeSinceLastNudge = (Date.now() - lastNudgeTime) / 1000;
        if (timeSinceLastNudge < 45) {
          setCooldownRemaining(45 - Math.floor(timeSinceLastNudge));
          return;
        }
      }

      // Execute the nudge
      executeNudge(false);
    }
  }, [autoNudgeEnabled, dynamicReflection, lastNudgeTime, isRunningSimulation]);

  // Update cooldown timer
  useEffect(() => {
    if (lastNudgeTime) {
      const interval = setInterval(() => {
        const timeSinceLastNudge = (Date.now() - lastNudgeTime) / 1000;
        const remaining = Math.max(0, 45 - Math.floor(timeSinceLastNudge));
        setCooldownRemaining(remaining);
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [lastNudgeTime]);

  if (!expand) {
    return (
      <Stack direction="row" spacing="10px" sx={{ alignItems: "center" }}>
        <Button onClick={() => setExpand(true)}>
          <ExpandMore fontSize="small" />
        </Button>
        <Typography variant="body1" sx={{ fontWeight: "bold" }}>
          SIMULATION DATA
        </Typography>
      </Stack>
    );
  }
  return (
    <Stack spacing="20px">
      <Stack direction="row" spacing="10px" sx={{ alignItems: "center" }}>
        <Button onClick={() => setExpand(false)} sx={{ width: "30px" }}>
          <ExpandLess fontSize="small" />
        </Button>
        <Typography
          variant="body1"
          sx={{
            fontWeight: "bold",
          }}
        >
          SIMULATION DATA
        </Typography>
      </Stack>
      <Stack
        direction="row"
        spacing="20px"
        sx={{ justifyContent: "space-between" }}
      >
        <Stack width="40%">
          <Typography
            variant="h6"
            sx={{
              fontWeight: "bold",
            }}
          >
            Status
          </Typography>
          <TextField
            className={"Status"}
            rows={5}
            value={status}
            readOnly={true}
            code={true}
          />
        </Stack>
        <Stack width="60%">
          <Typography
            variant="h6"
            sx={{
              fontWeight: "bold",
            }}
          >
            Dynamic Reflection
          </Typography>
          <TextField
            className={"Dynamic Reflection"}
            rows={10}
            value={dynamicReflection}
            readOnly={true}
            code={true}
          />
          
          {/* Auto-Nudge Controls */}
          <Box
            sx={{
              marginTop: "16px",
              padding: "12px",
              border: autoNudgeEnabled ? "2px solid #8FB339" : "2px solid #A8C957",
              backgroundColor: "transparent",
            }}
          >
            <Stack direction="row" spacing={1} alignItems="center" sx={{ marginBottom: "8px" }}>
              <Typography variant="body1" sx={{ fontWeight: "bold" }}>
                Auto-Nudge:
              </Typography>
              <Switch
                checked={autoNudgeEnabled}
                onChange={toggleAutoNudge}
                sx={{
                  "& .MuiSwitch-switchBase.Mui-checked": {
                    color: "#8FB339",
                  },
                  "& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track": {
                    backgroundColor: "#A8C957",
                  },
                }}
              />
              <Typography
                variant="body2"
                sx={{
                  fontWeight: "bold",
                  color: autoNudgeEnabled ? "#6D8A2B" : "#666",
                }}
              >
                {autoNudgeEnabled ? "ON" : "OFF"}
              </Typography>
            </Stack>

            {cooldownRemaining > 0 && (
              <Typography
                variant="caption"
                sx={{
                  color: "#6D8A2B",
                  fontWeight: "bold",
                  display: "block",
                  marginBottom: "8px",
                }}
              >
                ⏱️ Cooldown: {cooldownRemaining}s remaining
              </Typography>
            )}

            <Button
              onClick={() => executeNudge(true)}
              disabled={
                !dynamicReflection ||
                !dynamicReflection.toLowerCase().includes("say") ||
                cooldownRemaining > 0 ||
                isExecutingNudge
              }
              sx={{
                width: "100%",
                borderColor: "#A8C957",
                color: "#6D8A2B",
                "&:hover": {
                  borderColor: "#8FB339",
                  backgroundColor: "rgba(168, 201, 87, 0.1)",
                },
                "&:disabled": {
                  borderColor: "#D4E4B0",
                  color: "#B8CCA0",
                },
              }}
            >
              {isExecutingNudge ? "Sending..." : "Execute Nudge Manually 📤"}
            </Button>

            {lastNudgeStatus && lastNudgeStatus.success && (
              <Box
                sx={{
                  marginTop: "8px",
                  padding: "8px",
                  borderRadius: "4px",
                  backgroundColor: "rgba(168, 201, 87, 0.1)",
                  borderLeft: "3px solid #8FB339",
                }}
              >
                <Typography variant="caption" sx={{ color: "#4CAF50", display: "block" }}>
                  ✅ Last nudge: {Math.floor((Date.now() - (lastNudgeTime || 0)) / 1000)}s ago
                </Typography>
                <Typography variant="caption" sx={{ color: "#6D8A2B", display: "block" }}>
                  🌿 Message sent to {lastNudgeStatus.total_locations} locations
                </Typography>
              </Box>
            )}

            {!dynamicReflection.toLowerCase().includes("say") &&
              dynamicReflection !== "Simulation is running smoothly." &&
              dynamicReflection !== "" && (
                <Typography
                  variant="caption"
                  sx={{
                    color: "#A8C957",
                    fontStyle: "italic",
                    display: "block",
                    marginTop: "8px",
                  }}
                >
                  ℹ️ No message to send (waiting for "say" command)
                </Typography>
              )}
          </Box>
        </Stack>
      </Stack>
      <Divider />
      <ManualNudgePanel />
      <Divider />
      <Stack direction="row" spacing="10px">
        <Stack width="66%">
          <Typography
            variant="h6"
            sx={{
              fontWeight: "bold",
            }}
          >
            Change Log
          </Typography>
          <ChangeLog expand={expand} />
        </Stack>
        <Stack width="34%">
          <Typography
            variant="h6"
            sx={{
              fontWeight: "bold",
            }}
          >
            Notable Dynamics
          </Typography>
          <Dynamics expand={expand} />
        </Stack>
      </Stack>

      <Divider />
    </Stack>
  );
};

export default ContinuousData;
