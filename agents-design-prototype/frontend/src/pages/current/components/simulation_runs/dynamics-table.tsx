import React, { useEffect, useRef, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";
import axios from "axios";
import { SERVER_URL } from "../..";
import { useAppContext } from "../../hooks/app-context";

type DynamicsData = {
  milestone: string;
  dynamic: string;
  log_excerpt: string;
};

const Dynamics = ({ expand }: { expand: boolean }) => {
  const [dynamicsData, setDynamicsData] = useState<DynamicsData[]>([]);
  const { isRunningSimulation, currentRunId, currentPrototype } =
    useAppContext();

  console.log(dynamicsData);

  const fetchDynamics = () => {
    // updateIsLoading(true);
    axios({
      method: "GET",
      url: `${SERVER_URL}/fetch_dynamics`,
    })
      .then((response) => {
        console.log("/fetch_dynamics request successful:", response.data);
        setDynamicsData(response.data.dynamics_data);
      })
      .catch((error) => {
        console.error("Error calling /fetch_dynamics request:", error);
      })
      .finally(() => {
        // updateIsLoading(false);
      });
  };

  const getDynamics = () => {
    // updateIsLoading(true);
    axios({
      method: "GET",
      url: `${SERVER_URL}/get_dynamics`,
    })
      .then((response) => {
        console.log("/get_dynamics request successful:", response.data);
        setDynamicsData(response.data.dynamics_data);
      })
      .catch((error) => {
        console.error("Error calling /get_dynamics request:", error);
      })
      .finally(() => {
        // updateIsLoading(false);
      });
  };
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isRunningSimulation) {
      intervalRef.current = setInterval(fetchDynamics, 15000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null; // Ensure it's reset
      }
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isRunningSimulation]);

  useEffect(() => {
    getDynamics();
  }, [currentRunId, currentPrototype]);
  console.log("hi jenny currentRunId " + currentRunId);

  useEffect(() => {
    getDynamics();
  }, []);

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow sx={{ backgroundColor: "#4A8AB8" }}>
            <TableCell sx={{ color: "white", width: "20%" }}>MILESTONE</TableCell>
            <TableCell sx={{ color: "white", width: "30%" }}>DYNAMICS</TableCell>
            <TableCell sx={{ color: "white", width: "50%" }}>LOG EVIDENCE</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {dynamicsData
            .filter((row) => row?.dynamic?.trim() !== "")
            .map((row, index, array) => {
              const showMilestone =
                index === 0 || row.milestone !== array[index - 1].milestone;

              return (
                <TableRow key={index}>
                  <TableCell sx={{ width: "20%" }}>
                    {showMilestone ? row.milestone : ""}
                  </TableCell>
                  <TableCell sx={{ width: "30%" }}>{row.dynamic}</TableCell>
                  <TableCell 
                    sx={{ 
                      width: "50%",
                      fontStyle: "italic", 
                      fontSize: "0.9em",
                      color: "#555"
                    }}
                  >
                    {row.log_excerpt || "No citation available"}
                  </TableCell>
                </TableRow>
              );
            })}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default Dynamics;
