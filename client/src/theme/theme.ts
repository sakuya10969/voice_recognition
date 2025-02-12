import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  components: {
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          backgroundColor: "white", // フィールドの背景を白にする
          "&:hover": {
            backgroundColor: "white",
          },
          "&.Mui-focused": {
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
          color: "black", // 通常時のラベルの色
          "&.Mui-focused": {
            color: "black", // フォーカス時のラベルの色を強制的に黒に
          },
        },
      },
    },
    MuiFormLabel: {
      styleOverrides: {
        root: {
          color: "black", // 通常時のラベル色
          "&.Mui-focused": {
            color: "black", // フォーカス時のラベル色を強制的に黒に
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          backgroundColor: "white", // 選択エリアの背景を白に
          "&.Mui-focused": {
            color: "black", // フォーカス時の選択された値の色を黒に
            backgroundColor: "white",
          },
        },
        select: {
          backgroundColor: "white",
          "&.Mui-focused": {
            color: "black", // フォーカス時の選択した値の色
            backgroundColor: "white",
          },
        },
        icon: {
          color: "black", // ドロップダウンの矢印の色を黒に
        },
      },
    },
    MuiFormControl: {
      styleOverrides: {
        root: {
          "& .MuiInputLabel-root": {
            color: "black", // 通常時のラベルの色
          },
          "& .MuiInputLabel-root.Mui-focused, & .MuiFormLabel-root.Mui-focused":
            {
              color: "black", // フォーカス時のラベルの色を強制的に黒に
            },
        },
      },
    },
  },
});
