import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Modal from "@mui/material/Modal";
import CircularProgress from "@mui/material/CircularProgress";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import GraphicEqIcon from "@mui/icons-material/GraphicEq";

const UploadingModal = ({ open, onClose }) => {
    const modalStyle = {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    width: 350,
    height: 200,
    bgcolor: "background.paper",
    boxShadow: 24,
    p: 4,
    position: "relative",
  };

  const closeButtonStyle = {
    position: "absolute",
    top: 8,
    right: 8,
    color: "black"
  };

  return (
    <Modal open={open} onClose={onClose}>
      <Box sx={modalStyle}>
        <IconButton
          aria-label="close"
          sx={closeButtonStyle}
          onClick={onClose}
        >
          <CloseIcon />
        </IconButton>
        <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
            <Typography
                variant="h5"
                component="h2"
                textAlign="center"
                  >
                処理中
            </Typography>
            <GraphicEqIcon edge="end" color="inherit" size="large" sx={{ ml: 1, mb: 0.6 }} />
        </Box>
        <Box sx={{ display: "flex", justifyContent: "center", mt: 2 }}>
        <CircularProgress size={50} sx={{ color: "black" }} />
        </Box>
      </Box>
    </Modal>
  );
};

export default UploadingModal;
