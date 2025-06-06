import React, { useCallback } from 'react';
import { useDropzone, FileRejection } from 'react-dropzone';
import { Box, Button, Typography } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

import { FileDropZoneProps } from '@/types';

const FileDropZone = ({ file, onFileChange, errorFileType }: FileDropZoneProps) => {
  const onDrop = useCallback(
    (acceptedFiles: File[], fileRejections: FileRejection[]) => {
      if (fileRejections.length > 0) {
        onFileChange(null);
        return;
      }
      if (acceptedFiles.length > 0) {
        onFileChange(acceptedFiles[0]);
      }
    },
    [onFileChange]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: { 'video/mp4': [], 'audio/wav': [] },
  });

  return (
    <Box
      {...getRootProps()}
      sx={{
        border: '1px dashed black',
        borderRadius: '5px',
        p: 3,
        mb: 2,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        width: '450px',
        height: '250px',
        backgroundColor: isDragActive ? 'gainsboro' : 'transparent',
        '&:hover': {
          backgroundColor: 'whitesmoke',
        },
      }}
    >
      <input
        {...getInputProps()}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
          const file = e.target.files?.[0];
          if (file) onFileChange(file);
        }}
      />
      <label htmlFor="file-input">
        <Button
          variant="contained"
          component="span"
          startIcon={<CloudUploadIcon />}
          sx={{
            mb: 2,
            backgroundColor: 'black',
            width: '170px',
            '&:hover': { backgroundColor: 'black' },
          }}
        >
          ファイルの選択
        </Button>
      </label>

      {file && (
        <Typography variant="body1" sx={{ mb: 2, textAlign: 'center' }}>
          選択されたファイル: {file.name}
        </Typography>
      )}
      {errorFileType && (
        <Typography variant="body1" color="error" sx={{ mb: 2, textAlign: 'center' }}>
          mp4またはwav形式のファイルをアップロードしてください。
        </Typography>
      )}
    </Box>
  );
};

export default FileDropZone;
