import React from 'react';
import { Box, Typography } from '@mui/material';

const Error = () => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="60vh"
    >
      <Typography variant="h6" color="error" gutterBottom>
        エラーが発生しました
      </Typography>
      <Typography color="error">サイトデータの取得に失敗しました</Typography>
    </Box>
  );
};

export default Error;
