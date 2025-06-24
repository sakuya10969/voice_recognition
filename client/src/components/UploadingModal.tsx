import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Modal from '@mui/material/Modal';
import CircularProgress from '@mui/material/CircularProgress';
import IconButton from '@mui/material/IconButton';
import GraphicEqIcon from '@mui/icons-material/GraphicEq';
import CloseIcon from '@mui/icons-material/Close';

const UploadingModal = ({ open, onClose }: { open: boolean; onClose: () => void }) => {
  const modalStyle = {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 400,
    height: 250,
    bgcolor: 'background.paper',
    boxShadow: 24,
    p: 4,
  };

  return (
    <Modal 
      open={open} 
      onClose={() => {}}
      disableEscapeKeyDown
    >
      <Box sx={modalStyle}>
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', width: '100%' }}>
          <IconButton onClick={onClose} sx={{ position: 'absolute', top: 10, right: 10 }}>
            <CloseIcon sx={{ color: 'black' }} />
          </IconButton>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Typography variant="h5" component="h2" textAlign="center">
            議事録を作成中...
          </Typography>
          <GraphicEqIcon color="inherit" fontSize="large" sx={{ ml: 1, mb: 0.6 }} />
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <CircularProgress size={50} sx={{ color: 'black' }} />
        </Box>
      </Box>
    </Modal>
  );
};

export default UploadingModal;
