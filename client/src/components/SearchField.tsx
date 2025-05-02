import React from "react";
import TextField from "@mui/material/TextField";
import { ThemeProvider } from "@mui/material/styles";
import { theme } from "../theme/theme";

interface SearchFieldProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const SearchField: React.FC<SearchFieldProps> = ({ value, onChange }) => (
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
