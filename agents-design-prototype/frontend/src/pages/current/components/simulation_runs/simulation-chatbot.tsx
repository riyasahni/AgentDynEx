import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Typography,
  Button,
  CircularProgress,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import ChatIcon from "@mui/icons-material/Chat";
import CloseIcon from "@mui/icons-material/Close";
import RefreshIcon from "@mui/icons-material/Refresh";
import axios from "axios";
import { SERVER_URL } from "../..";
import { useAppContext } from "../../hooks/app-context";

type Message = {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
};

const SimulationChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadedLogs, setLoadedLogs] = useState<string>("");
  const [lastLoadedTime, setLastLoadedTime] = useState<Date | null>(null);
  const [isLoadingLogs, setIsLoadingLogs] = useState(false);
  const { isRunningSimulation } = useAppContext();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Clear chat when simulation stops
  useEffect(() => {
    if (!isRunningSimulation) {
      setMessages([]);
      setIsOpen(false);
      setLoadedLogs("");
      setLastLoadedTime(null);
    }
  }, [isRunningSimulation]);

  // Load latest logs
  const handleLoadLogs = async () => {
    setIsLoadingLogs(true);
    try {
      const response = await axios.get(`${SERVER_URL}/get_logs`);
      setLoadedLogs(response.data.logs || "");
      setLastLoadedTime(new Date());

      // Add system message to chat
      const systemMessage: Message = {
        role: "assistant",
        content:
          "✅ Latest logs loaded! You can now ask me questions about the simulation. I'll support every answer with direct quotes from the logs.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, systemMessage]);
    } catch (error) {
      console.error("Error loading logs:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "❌ Failed to load logs. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoadingLogs(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // Check if logs are loaded
    if (!loadedLogs) {
      const warningMessage: Message = {
        role: "assistant",
        content:
          "⚠️ Please load the latest logs first using the 'Load Latest Logs' button.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, warningMessage]);
      return;
    }

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await axios.post(`${SERVER_URL}/chat_with_simulation`, {
        question: input,
        logs: loadedLogs, // Send loaded logs to backend
      });

      const assistantMessage: Message = {
        role: "assistant",
        content: response.data.answer,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "Sorry, I couldn't process that question. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isRunningSimulation) return null;

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <IconButton
          onClick={() => setIsOpen(true)}
          sx={{
            position: "fixed",
            bottom: 20,
            right: 20,
            backgroundColor: "#4A8AB8",
            color: "white",
            "&:hover": { backgroundColor: "#3A7AA8" },
            width: 60,
            height: 60,
            zIndex: 1000,
          }}
        >
          <ChatIcon />
        </IconButton>
      )}

      {/* Chat Window */}
      {isOpen && (
        <Paper
          elevation={8}
          sx={{
            position: "fixed",
            bottom: 20,
            right: 20,
            width: 450,
            height: 600,
            display: "flex",
            flexDirection: "column",
            zIndex: 1000,
          }}
        >
          {/* Header */}
          <Box
            sx={{
              backgroundColor: "#4A8AB8",
              color: "white",
              p: 2,
            }}
          >
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 1,
              }}
            >
              <Typography variant="h6">Simulation Assistant</Typography>
              <IconButton
                onClick={() => setIsOpen(false)}
                sx={{ color: "white" }}
              >
                <CloseIcon />
              </IconButton>
            </Box>

            {/* Load Logs Button */}
            <Button
              variant="contained"
              size="small"
              onClick={handleLoadLogs}
              disabled={isLoadingLogs}
              startIcon={
                isLoadingLogs ? (
                  <CircularProgress size={16} sx={{ color: "white" }} />
                ) : (
                  <RefreshIcon />
                )
              }
              sx={{
                backgroundColor: "#E89B6C",
                "&:hover": { backgroundColor: "#D67B4A" },
                width: "100%",
                color: "white",
              }}
            >
              {isLoadingLogs ? "Loading..." : "Load Latest Logs"}
            </Button>

            {/* Last Loaded Time */}
            {lastLoadedTime && (
              <Typography
                variant="caption"
                sx={{ display: "block", mt: 0.5, opacity: 0.8 }}
              >
                Logs loaded: {lastLoadedTime.toLocaleTimeString()}
              </Typography>
            )}
          </Box>

          {/* Messages */}
          <Box sx={{ flex: 1, overflowY: "auto", p: 2, backgroundColor: "#f9f9f9" }}>
            {messages.length === 0 && (
              <Box sx={{ textAlign: "center", mt: 4 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  👋 Welcome to the Simulation Assistant!
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Click "Load Latest Logs" to start asking questions.
                </Typography>
              </Box>
            )}
            {messages.map((msg, idx) => (
              <Box
                key={idx}
                sx={{
                  mb: 2,
                  display: "flex",
                  justifyContent:
                    msg.role === "user" ? "flex-end" : "flex-start",
                }}
              >
                <Paper
                  elevation={1}
                  sx={{
                    p: 1.5,
                    maxWidth: "85%",
                    backgroundColor:
                      msg.role === "user" ? "#E89B6C" : "white",
                    color: msg.role === "user" ? "white" : "black",
                  }}
                >
                  <Typography
                    variant="body2"
                    sx={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}
                  >
                    {msg.content}
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      display: "block",
                      mt: 0.5,
                      opacity: 0.7,
                      fontSize: "0.7rem",
                    }}
                  >
                    {msg.timestamp.toLocaleTimeString()}
                  </Typography>
                </Paper>
              </Box>
            ))}
            {isLoading && (
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <CircularProgress size={16} />
                <Typography variant="body2" color="text.secondary">
                  Thinking...
                </Typography>
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Box>

          {/* Input */}
          <Box sx={{ p: 2, borderTop: "1px solid #ddd", backgroundColor: "white" }}>
            <Box sx={{ display: "flex", gap: 1 }}>
              <TextField
                fullWidth
                size="small"
                placeholder="Ask about the simulation..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                disabled={isLoading}
                multiline
                maxRows={3}
              />
              <IconButton
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                sx={{
                  color: "#4A8AB8",
                  "&:disabled": { color: "#ccc" },
                }}
              >
                <SendIcon />
              </IconButton>
            </Box>
          </Box>
        </Paper>
      )}
    </>
  );
};

export default SimulationChatbot;
