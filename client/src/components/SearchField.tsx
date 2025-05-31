import React from "react";
import TextField from "@mui/material/TextField";
import { ThemeProvider } from "@mui/material/styles";

import { theme } from "@/theme/theme";
import { SearchFieldProps } from "@/types";

const SearchField = ({ value, onChange }: SearchFieldProps) => (
  <ThemeProvider theme={theme}>
    <TextField
      label="SPOサイトキーワード"
      variant="outlined"
      size="small"
      fullWidth
      value={value}
      onChange={onChange}
      sx={{
        mb: 2,
        "& input": {
          backgroundColor: "white",
        },
      }}
    />
  </ThemeProvider>
);

export default SearchField;
