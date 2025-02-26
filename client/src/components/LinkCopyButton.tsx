import React from "react";
import Button from "@mui/material/Button";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";

const LinkCopyButton: React.FC = () => {
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      alert("URLをコピーしました");
    } catch (err) {
      console.error("コピー失敗:", err);
    }
  };

  return (
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
  );
};

export default LinkCopyButton;
