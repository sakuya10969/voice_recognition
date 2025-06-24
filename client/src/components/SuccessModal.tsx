import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Modal from '@mui/material/Modal';
import Button from '@mui/material/Button';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CloseIcon from '@mui/icons-material/Close';
import IconButton from '@mui/material/IconButton';

import { SuccessModalProps } from '@/types';

const SuccessModal = ({ open, onClose }: SuccessModalProps) => {
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
  }

  return (
    <Modal open={open} onClose={onClose}>
      <Box sx={modalStyle}>
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', width: '100%' }}>
          <IconButton onClick={onClose} sx={{ position: 'absolute', top: 10, right: 10 }}>
            <CloseIcon sx={{ color: 'success.main' }} />
          </IconButton>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Typography variant="h6" component="h2" textAlign="center">
            議事録作成に成功しました
          </Typography>
          <CheckCircleIcon fontSize="large" color="success" sx={{ ml: 1, mb: 0.5 }} />
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Button variant="contained" color="success" onClick={onClose} sx={{ fontSize: 15 }}>
            OK
          </Button>
        </Box>
      </Box>
    </Modal>
  );
};

export default SuccessModal;
