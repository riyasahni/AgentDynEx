// Monsters Inc Color Palette
export const colors = {
  // Primary colors from Monsters Inc
  green: "#8FB339",      // Lime green (Mike Wazowski)
  lightGreen: "#A8C957", // Lighter green for clickable items
  darkGreen: "#6D8A2B",  // Darker green for non-clickable
  
  teal: "#7ECDC4",       // Light teal/mint
  lightTeal: "#9EDDD6",  // Lighter teal for clickable items
  darkTeal: "#5BA89F",   // Darker teal for non-clickable/hover states
  
  blue: "#5BA3D0",       // Sky blue
  lightBlue: "#8BC4E8",  // Lighter blue for clickable items
  darkBlue: "#4A8AB8",   // Darker blue for non-clickable
  
  orange: "#E89B6C",     // Peachy orange
  lightOrange: "#F0B088", // Lighter orange for clickable items
  darkOrange: "#D67B4A", // Darker orange for non-clickable/hover states
  
  brown: "#9B7653",      // Warm brown
  
  // Neutral colors
  white: "#FFFFFF",
  black: "#000000",
  transparent: "transparent",
  
  // Legacy color mappings (for gradual migration)
  primary: "#5BA89F",      // Darker teal for header/non-clickable
  primaryLight: "#9EDDD6", // Lighter teal for clickable items
  primaryDark: "#4A8AB8",  // Darker blue for emphasis
  secondary: "#F0B088",    // Lighter orange for buttons
  accent: "#A8C957",       // Lighter green for accent
};

// Color variants for buttons and components
export type ColorVariant = "transparent" | "blue" | "orange" | "primary" | "green";
