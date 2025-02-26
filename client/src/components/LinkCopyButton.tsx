import React, { useState } from "react";
import Button from "@mui/material/Button";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";
import Box from "@mui/material/Box";

const Alert = React.forwardRef<HTMLDivElement, any>((props, ref) => (
  <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />
));

const LinkCopyButton: React.FC = () => {
  const [open, setOpen] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setOpen(true);
    } catch (err) {
      console.error("コピー失敗:", err);
    }
  };

  const handleClose = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    if (reason === "clickaway") return;
    setOpen(false);
  };

  return (
    <Box sx={{ position: "relative", display: "inline-block" }}>
      <Button
        onClick={handleCopy}
        startIcon={<ContentCopyIcon />}
        sx={{
          color: "white",
          backgroundColor: "black",
          borderRadius: "5px",
          width: "150px",
          "&:hover": {
            backgroundColor: "black",
          },
        }}
      >
        URLのコピー
      </Button>
      <Snackbar
        open={open}
        autoHideDuration={2000}
        onClose={handleClose}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert onClose={handleClose} severity="success" sx={{ width: "100%" }}>
          URLをコピーしました
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default LinkCopyButton;
