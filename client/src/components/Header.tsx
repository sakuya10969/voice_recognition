import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MicIcon from '@mui/icons-material/Mic';
import Box from '@mui/material/Box';

import intelligentforce from '../assets/intelligentforce.png';

const Header = () => {
  return (
    <AppBar position="static" sx={{ backgroundColor: 'white', color: 'black' }}>
      <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton edge="start" color="inherit" size="large">
            <MicIcon />
          </IconButton>
          <Typography variant="h5" component="div" sx={{ fontWeight: 'bold' }}>
            議事録作成ツール
          </Typography>
        </Box>
        <Box>
          <img src={intelligentforce} alt="Intelligent Force" style={{ height: 40 }} />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
