import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  components: {
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "black", // 通常時の枠線を黒に
          },
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: "black", // ホバー時の枠線を黒に
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: "black", // フォーカス時の枠線を黒に
          },
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: "black !important", // 通常時のラベルの色
          "&.Mui-focused": {
            color: "black !important", // フォーカス時のラベルの色を強制的に黒に
          },
        },
      },
    },
    MuiFormLabel: {
      styleOverrides: {
        root: {
          color: "black !important", // 通常時のラベル色
          "&.Mui-focused": {
            color: "black !important", // フォーカス時のラベル色を強制的に黒に
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          "&.Mui-focused": {
            color: "black !important", // フォーカス時の選択された値の色を黒に
          },
        },
        select: {
          "&.Mui-focused": {
            color: "black !important", // フォーカス時の選択した値の色
          },
        },
        icon: {
          color: "black !important", // ドロップダウンの矢印の色を黒に
        },
      },
    },
    MuiFormControl: {
      styleOverrides: {
        root: {
          "& .MuiInputLabel-root": {
            color: "black !important", // 通常時のラベルの色
          },
          "& .MuiInputLabel-root.Mui-focused, & .MuiFormLabel-root.Mui-focused":
            {
              color: "black !important", // フォーカス時のラベルの色を強制的に黒に
            },
        },
      },
    },
  },
});
