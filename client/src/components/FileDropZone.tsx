import React, { useCallback } from 'react';
import { useDropzone, FileRejection } from 'react-dropzone';
import { Box, Button, Typography } from '@mui/material';
import AudioFileIcon from '@mui/icons-material/AudioFile';
import UploadFileIcon from '@mui/icons-material/UploadFile';

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
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, width: '100%' }}>
      <UploadFileIcon sx={{ mr: 1 }} />
      <Box
        {...getRootProps()}
        sx={{
          border: '1px dashed black',
          borderRadius: '5px',
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          width: '500px',
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
          startIcon={<AudioFileIcon />}
          sx={{
            mb: 2,
            backgroundColor: 'black',
            width: '190px',
            '&:hover': { backgroundColor: 'black' },
          }}
        >
          音声ファイルの選択
        </Button>
        </label>

        {file && (
          <Typography variant="body1" sx={{ mb: 2, textAlign: 'center' }}>
            選択された音声ファイル: {file.name}
          </Typography>
        )}
        {errorFileType && (
          <Typography variant="body1" color="error" sx={{ mb: 2, textAlign: 'center' }}>
            mp4またはwav形式のファイルをアップロードしてください。
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default FileDropZone;
