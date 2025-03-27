import { createTheme } from "@mui/material/styles";

const commonStyles = {
  backgroundColor: "white",
  "&.Mui-focused": {
    backgroundColor: "white",
  },
};

const commonLabelStyles = {
  color: "black",
  "&.Mui-focused": {
    color: "black",
  },
};

export const theme = createTheme({
  components: {
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          ...commonStyles,
          "&:hover": {
            backgroundColor: "white",
          },
          "& input": {
            backgroundColor: "white",
          },
          "& input:-webkit-autofill": {
            backgroundColor: "white !important",
            WebkitBoxShadow: "0 0 0px 1000px white inset !important",
          },
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "black",
          },
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: "black",
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: "black",
          },
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          ...commonLabelStyles,
        },
      },
    },
    MuiFormLabel: {
      styleOverrides: {
        root: {
          ...commonLabelStyles,
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          ...commonStyles,
          "&.Mui-focused": {
            color: "black",
          },
        },
        select: {
          ...commonStyles,
          "&.Mui-focused": {
            color: "black",
          },
        },
        icon: {
          color: "black",
        },
      },
    },
    MuiFormControl: {
      styleOverrides: {
        root: {
          "& .MuiInputLabel-root": {
            color: "black",
          },
          "& .MuiInputLabel-root.Mui-focused, & .MuiFormLabel-root.Mui-focused": {
            color: "black",
          },
        },
      },
    },
  },
});
