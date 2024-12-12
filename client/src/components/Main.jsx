import { Box } from "@mui/material";
import { useState } from "react";

import FileUpload from "./FileUpload";
import Note from "./Note";
import { handleSendAudio } from "../api/Api";

const Main = () => {
  const [file, setFile] = useState(null);
  const [content, setContent] = useState('');
  const [isUploading, setUploading] = useState(false);
  const handleFileChange = (e) => {
      setFile(e.target.files[0]);
  } 
  const handleUpload = async () => {
    setUploading(true);
    const transcription = await handleSendAudio(file);
    setContent(transcription);
    setFile(null);
    setUploading(false);
  }

  return (
      <Box
      sx={{
        display: 'flex',
        justifyContent: 'space-around',
        alignItems: 'center',
        width: '100%',
      }}
    >
      <FileUpload onChange={handleFileChange} onClick={handleUpload} file={file} isUploading={isUploading} />
      <Note content={content}/>
    </Box>
  );
}

export default Main;