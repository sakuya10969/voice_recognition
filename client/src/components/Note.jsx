import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';

const Note = ({ content }) => {
  return (
    <Paper
      elevation={3}
      sx={{
        width: '700px',
        height: '600px',
        padding: 2,
        margin: 2,
        borderRadius: '5px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        border: '1px solid black',
      }}
    >
      <Typography
        variant="h6"
        sx={{ fontWeight: 'bold', borderBottom: '1px solid black', pb: 1, textAlign: 'center' }}
      >
        議事録
      </Typography>
      <Box
        sx={{
          overflowY: 'auto',
          mt: 2,
        }}
      >
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
          {content}
        </Typography>
      </Box>
    </Paper>
  );
};

export default Note;
