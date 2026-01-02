import React, { ReactElement } from "react";
import {
  TextField as MuiTextField,
  TextFieldProps as MuiTextFieldProps,
} from "@mui/material";
import { colors } from "../theme/colors";

interface TextFieldProps extends Omit<MuiTextFieldProps, "inputProps"> {
  code?: boolean;
  readOnly?: boolean;
}

const COLOR = colors.primaryLight; // Lighter color for input fields

const TextField = ({
  code = false,
  readOnly = false,
  className = "text-field",
  label,
  variant = "outlined",
  rows = 2,
  value,
  placeholder = "",
  onChange,
  sx,
  ...props
}: TextFieldProps): ReactElement => {
  return (
    <MuiTextField
      className={className}
      label={label}
      multiline
      variant={variant}
      rows={rows}
      value={value}
      placeholder={placeholder}
      onChange={onChange}
      inputProps={
        code
          ? { readOnly: readOnly, style: { fontFamily: "monospace" } }
          : undefined
      }
      sx={{
        width: "100%",
        backgroundColor: "white",
        "& .MuiOutlinedInput-root": {
          "&.Mui-focused fieldset": {
            borderColor: colors.primaryDark,
            borderRadius: 0,
          },
          "&:hover fieldset": {
            borderColor: COLOR,
            borderRadius: 0,
          },
        },
        "& .MuiInputLabel-root": {
          color: COLOR,
        },
        "& .MuiInputLabel-root.Mui-focused": {
          color: colors.primaryDark,
        },
        ...sx,
      }}
      {...props}
    />
  );
};

export default TextField;
