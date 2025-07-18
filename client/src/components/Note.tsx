import React from 'react';
import { Paper, Box, Typography, IconButton } from '@mui/material';
import { Download as DownloadIcon } from '@mui/icons-material';
import DescriptionIcon from '@mui/icons-material/Description';

import { exportMeetingDocx } from '@/utils/exportDocx';
import { NoteProps } from '@/types';

const Note = ({ summarizedText, transcribedText }: NoteProps) => {
  const handleDownload = async () => {
    await exportMeetingDocx(summarizedText, transcribedText);
  };

  return (
    <Paper
      elevation={3}
      sx={{
        width: '600px',
        height: '600px',
        p: 2,
        mt: 1,
        border: '1px solid black',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          borderBottom: '1px solid black',
          pb: 1,
        }}
      >
      <Typography
        variant="h6"
        sx={{
          fontWeight: 'bold',
          textAlign: 'center',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 1,
        }}
      >
        <DescriptionIcon />
        議事録
      </Typography>
        <IconButton
          sx={{
            transform: 'translateX(50px)',
            ':disabled': {
              opacity: 0.5,
            },
          }}
          onClick={handleDownload}
          disabled={!summarizedText.trim() && !transcribedText.trim()}
        >
          <DownloadIcon sx={{ color: 'black' }} />
        </IconButton>
      </Box>
      <Box
        sx={{
          overflowY: 'auto',
          mt: 1,
          height: '90%',
        }}
      >
        {summarizedText && (
          <>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', fontWeight: 'bold' }}>
              [要約結果]
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', mb: 2 }}>
              {summarizedText}
            </Typography>
          </>
        )}

        {transcribedText && (
          <>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', fontWeight: 'bold' }}>
              [文字起こし結果]
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
              {transcribedText}
            </Typography>
          </>
        )}
      </Box>
    </Paper>
  );
};

export default Note;
