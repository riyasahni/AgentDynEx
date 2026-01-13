import React, { useEffect, useState } from "react";
import {
  FormControl,
  Select,
  MenuItem,
  SelectChangeEvent,
  CircularProgress,
  Typography,
  Box,
} from "@mui/material";
import axios from "axios";
import { SERVER_URL } from "..";
import { useAppContext } from "../hooks/app-context";

type SavedSimulation = {
  uuid: string;
  prototype: string;
  problem: string;
  timestamp: string;
};

const SavedSimulationsDropdown = () => {
  const [simulations, setSimulations] = useState<SavedSimulation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedValue, setSelectedValue] = useState("");
  const { updateCurrentPrototype } = useAppContext();

  useEffect(() => {
    fetchSavedSimulations();
  }, []);

  const fetchSavedSimulations = () => {
    setLoading(true);
    axios({
      method: "GET",
      url: `${SERVER_URL}/get_saved_simulations`,
    })
      .then((response) => {
        console.log("/get_saved_simulations successful:", response.data);
        setSimulations(response.data.simulations || []);
      })
      .catch((error) => {
        console.error("Error calling /get_saved_simulations:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleChange = (event: SelectChangeEvent<string>) => {
    const value = event.target.value;
    setSelectedValue(value);

    if (!value) return;

    // Parse the value (format: "uuid|prototype")
    const [uuid, prototype] = value.split("|");

    // First, load the simulation globals
    axios({
      method: "GET",
      url: `${SERVER_URL}/set_globals_for_uuid/${uuid}`,
    })
      .then((response) => {
        console.log("/set_globals_for_uuid successful:", response.data);

        // Then set the current prototype
        return axios({
          method: "POST",
          url: `${SERVER_URL}/set_current_prototype`,
          data: { current_prototype: prototype },
        });
      })
      .then((response) => {
        console.log("/set_current_prototype successful:", response.data);
        
        // Update the app context to trigger UI refresh and navigate to simulation dashboard
        updateCurrentPrototype(prototype);
      })
      .catch((error) => {
        console.error("Error loading simulation:", error);
        alert("Failed to load simulation. Please try again.");
      });
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", alignItems: "center", minWidth: 200 }}>
        <CircularProgress size={20} sx={{ color: "white" }} />
        <Typography sx={{ ml: 1, color: "white" }}>Loading...</Typography>
      </Box>
    );
  }

  return (
    <FormControl sx={{ minWidth: 250 }} size="small">
      <Select
        value={selectedValue}
        onChange={handleChange}
        displayEmpty
        sx={{
          color: "white",
          ".MuiOutlinedInput-notchedOutline": {
            borderColor: "white",
          },
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: "white",
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: "white",
          },
          ".MuiSvgIcon-root": {
            color: "white",
          },
        }}
      >
        <MenuItem value="" disabled>
          <em>Load Saved Simulation</em>
        </MenuItem>
        {simulations.map((sim, index) => (
          <MenuItem key={index} value={`${sim.uuid}|${sim.prototype}`}>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: "bold" }}>
                {sim.prototype}
              </Typography>
              <Typography variant="caption" sx={{ color: "text.secondary" }}>
                {sim.timestamp}
              </Typography>
            </Box>
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default SavedSimulationsDropdown;
