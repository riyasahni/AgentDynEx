import React, { ReactElement, ReactNode } from "react";
import {
  Button as MuiButton,
  ButtonProps as MuiButtonProps,
} from "@mui/material";
import { colors, ColorVariant } from "../theme/colors";

interface ButtonProps extends MuiButtonProps {
  children: ReactNode;
  colorVariant?: ColorVariant;
}

const Button = ({
  children,
  variant = "contained",
  onClick,
  sx,
  disabled = false,
  colorVariant = "primary",
  ...props
}: ButtonProps): ReactElement => {
  let color = colors.secondary; // Light orange for clickable buttons
  if (colorVariant === "orange") color = colors.lightOrange;
  if (colorVariant === "blue") color = colors.lightBlue;
  if (colorVariant === "green") color = colors.lightGreen;
  if (colorVariant === "transparent") color = colors.transparent;

  let hoverColor = colors.darkOrange;
  if (colorVariant === "orange") hoverColor = colors.darkOrange;
  if (colorVariant === "blue") hoverColor = colors.darkBlue;
  if (colorVariant === "green") hoverColor = colors.darkGreen;
  if (colorVariant === "transparent") hoverColor = "rgba(0, 0, 0, 0.1)";

  return (
    <MuiButton
      variant={variant}
      onClick={onClick}
      disabled={disabled}
      sx={{
        backgroundColor: color,
        borderRadius: 0,
        boxShadow: "none",
        "&:hover": {
          backgroundColor: hoverColor,
          color: "white",
        },
        ...sx,
      }}
      {...props}
    >
      {children}
    </MuiButton>
  );
};

export default Button;
