import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import SendIcon from "@mui/icons-material/Send";
import CircularProgress from "@mui/material/CircularProgress";
import { useDropzone } from "react-dropzone";
import { useState } from "react";

const FileUpload = ({ onChange, onClick, file, isUploading }) => {
  const [errorFileType, setErrorFileType] = useState(false);
  const onDrop = (acceptedFiles, fileRejections) => {
    if (fileRejections.length > 0) {
      setErrorFileType(true);
      return;
    }
    setErrorFileType(false);
    if (acceptedFiles.length > 0) {
      onChange(acceptedFiles[0]);
    }
  };
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: {
      "video/mp4": [],
      "audio/wav": [],
    },
  });

  return (
    <Box
      {...getRootProps()}
      sx={{
        border: "1px dashed black",
        borderRadius: "5px",
        p: 3,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        width: "300px",
        height: "400px",
        backgroundColor: isDragActive ? "gainsboro" : "transparent",
        "&:hover": {
          backgroundColor: "whitesmoke",
        },
      }}
    >
      <Typography variant="h6" sx={{ mb: 2, textAlign: "center" }} gutterBottom>
        ファイルをアップロードしてください
      </Typography>

      <input
        {...getInputProps()}
        onChange={(e) => onChange(e.target.files[0])}
      />
      <label htmlFor="file-input">
        <Button
          variant="contained"
          component="span"
          startIcon={<CloudUploadIcon />}
          sx={{ mb: 2, backgroundColor: "black" }}
        >
          ファイルの選択
        </Button>
      </label>

      {file && (
        <Typography variant="body1" sx={{ mb: 2, textAlign: "center" }}>
          選択されたファイル: {file.name}
        </Typography>
      )}
      {errorFileType &&
        <Typography variant="body1" color="error" sx={{ mb: 2, textAlign: "center" }}>
          mp4またはwav形式のファイルをアップロードしてください。
        </Typography>
      }
      {isUploading ? (
        <>
          <Typography variant="body1" sx={{ mb: 2, textAlign: "center" }}> 処理中... </Typography>
          <CircularProgress />
        </>
      ) : (
        <IconButton
          onClick={(e) => {
            e.stopPropagation();
            onClick();
          }}
          disabled={!file}
          sx={{
            borderRadius: "5px",
            ":disabled": {
              opacity: 0.5,
            },
          }}
        >
          <SendIcon sx={{ color: "black" }} />
        </IconButton>
      )}
    </Box>
  );
};

export default FileUpload;
