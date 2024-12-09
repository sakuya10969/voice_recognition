import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import SendIcon from '@mui/icons-material/Send';

const FileUpload = ({ onClick }) => {
  const [file, setFile] = useState(null);

    const handleFileChange = (event) => {
      const file = event.target.files[0];
    setFile(file);
  };

  return (
    <Box
        sx={{
            border: '1px dashed black',
            borderRadius: '5px',
            p: 3,
            textAlign: 'gray',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            width: '300px',
            height: '400px',
            '&:hover': {
            backgroundColor: 'whitesmoke',
            },
        }}
        >
          <Typography variant="h6" sx={{ mb: 2 }} gutterBottom>
            ファイルをアップロードしてください
        </Typography>

        <input
            type="file"
            style={{ display: 'none'}}
            id="file-input"
            onChange={handleFileChange}  
        />
        <label htmlFor="file-input">
            <Button
            variant="contained"
            component="span"
            startIcon={<CloudUploadIcon />}
            sx={{ mb: 2 }}
            >
            ファイルの選択
            </Button>
        </label>

        {file && (
            <Typography variant="body1" sx={{ mb: 2 }}>
            選択されたファイル: {file.name}
            </Typography>
        )}

        <IconButton
            color="primary"
            onClick={onClick}
            disabled={!file}
            sx={{
            border: '1px solid #ccc',
            borderRadius: '5px',
            ':disabled': {
                opacity: 0.5,
            },
            }}
        >
            <SendIcon />
        </IconButton>
    </Box>

  );
};

export default FileUpload;
