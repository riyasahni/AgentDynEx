import React, { useEffect, useRef, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Typography,
  Box,
} from "@mui/material";
import axios from "axios";
import { SERVER_URL } from "../..";
import { useAppContext } from "../../hooks/app-context";

type ChangeLogData = {
  where: string;
  what: string;
  change: string;
  milestone: string;
};

type AnalysisResult = {
  context_analysis: string;
  log_excerpt: string;
  config_analysis: string;
};

const ChangeLog = ({ expand }: { expand: boolean }) => {
  const [changeLogData, setChangeLogData] = useState<ChangeLogData[]>([]);
  const [analysisDialogOpen, setAnalysisDialogOpen] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResult | null>(null);
  const [analyzingIndex, setAnalyzingIndex] = useState<number | null>(null);

  const { isRunningSimulation, currentPrototype, currentRunId } =
    useAppContext();

  const fetchChanges = () => {
    // updateIsLoading(true);
    axios({
      method: "GET",
      url: `${SERVER_URL}/fetch_changes`,
    })
      .then((response) => {
        console.log("/fetch_changes request successful:", response.data);
        setChangeLogData(response.data.changes_data);
      })
      .catch((error) => {
        console.error("Error calling /fetch_changes request:", error);
      })
      .finally(() => {
        // updateIsLoading(false);
      });
  };

  const getChanges = () => {
    // updateIsLoading(true);
    axios({
      method: "GET",
      url: `${SERVER_URL}/get_changes`,
    })
      .then((response) => {
        console.log("/get_changes request successful:", response.data);
        setChangeLogData(response.data.changes_data);
      })
      .catch((error) => {
        console.error("Error calling /get_changes request:", error);
      })
      .finally(() => {
        // updateIsLoading(false);
      });
  };

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isRunningSimulation) {
      intervalRef.current = setInterval(fetchChanges, 5000);
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
    getChanges();
  }, [expand, currentRunId, currentPrototype]);
  console.log("hi jenny currentRunId " + currentRunId);

  useEffect(() => {
    getChanges();
  }, []);

  const handleVerifyClick = (changeSummary: string, index: number) => {
    setAnalyzingIndex(index);
    setCurrentAnalysis(null);
    setAnalysisDialogOpen(true);

    axios({
      method: "POST",
      url: `${SERVER_URL}/analyze_change_log`,
      data: { change_summary: changeSummary },
    })
      .then((response) => {
        console.log("/analyze_change_log successful:", response.data);
        setCurrentAnalysis(response.data);
      })
      .catch((error) => {
        console.error("Error calling /analyze_change_log:", error);
        setCurrentAnalysis({
          context_analysis: "Error analyzing change",
          log_excerpt: "Error fetching excerpt",
          config_analysis: "Error analyzing config",
        });
      })
      .finally(() => {
        setAnalyzingIndex(null);
      });
  };

  const handleCloseDialog = () => {
    setAnalysisDialogOpen(false);
    setCurrentAnalysis(null);
  };

  if (!changeLogData) return <></>;
  return (
    <>
      <Dialog
        open={analysisDialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Change Log Analysis</DialogTitle>
        <DialogContent>
          {!currentAnalysis ? (
            <Box sx={{ display: "flex", justifyContent: "center", p: 3 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                Context Analysis
              </Typography>
              <Typography
                variant="body2"
                sx={{ whiteSpace: "pre-wrap", mb: 3 }}
              >
                {currentAnalysis.context_analysis}
              </Typography>

              <Typography variant="h6" gutterBottom>
                Log Excerpt
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  whiteSpace: "pre-wrap",
                  mb: 3,
                  fontFamily: "monospace",
                  backgroundColor: "#f5f5f5",
                  p: 2,
                  borderRadius: 1,
                }}
              >
                {currentAnalysis.log_excerpt}
              </Typography>

              <Typography variant="h6" gutterBottom>
                Config Analysis
              </Typography>
              <Typography
                variant="body2"
                sx={{ whiteSpace: "pre-wrap" }}
              >
                {currentAnalysis.config_analysis}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Close</Button>
        </DialogActions>
      </Dialog>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: "#4A8AB8" }}>
              <TableCell sx={{ color: "white" }}>MILESTONE</TableCell>
              <TableCell sx={{ color: "white" }}>WHERE</TableCell>
              <TableCell sx={{ color: "white" }}>WHAT</TableCell>
              <TableCell sx={{ color: "white" }}>CHANGE</TableCell>
              <TableCell sx={{ color: "white" }}>ACTION</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {changeLogData
              .filter((row) => row.change.trim() !== "")
              .map((row, index, array) => {
                const showMilestone =
                  index === 0 || row.milestone !== array[index - 1].milestone;
                return (
                  <TableRow key={index}>
                    <TableCell>{showMilestone ? row.milestone : ""}</TableCell>
                    <TableCell>{row.where}</TableCell>
                    <TableCell>{row.what}</TableCell>
                    <TableCell>{row.change}</TableCell>
                    <TableCell>
                      <Button
                        variant="contained"
                        size="small"
                        onClick={() => handleVerifyClick(row.change, index)}
                        disabled={analyzingIndex === index}
                        sx={{
                          backgroundColor: "#E89B6C",
                          "&:hover": {
                            backgroundColor: "#D67B4A",
                          },
                        }}
                      >
                        {analyzingIndex === index ? (
                          <CircularProgress size={20} sx={{ color: "white" }} />
                        ) : (
                          "Verify"
                        )}
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
};

export default ChangeLog;
