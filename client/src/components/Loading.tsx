import React from 'react';
import { CircularProgress, Box, Typography } from '@mui/material';

const Loading = () => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="60vh"
    >
      <Typography variant="h6" color="text.primary" mb={2}>
        サイトデータ取得中...
      </Typography>
      <CircularProgress />
    </Box>
  );
};

export default Loading;
