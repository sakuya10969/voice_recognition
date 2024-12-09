import { Box } from '@mui/material';
import { useState } from 'react';

import Header from './components/Header';
import Footer from './components/Footer';
import FileUpload from './components/FileUpload';
import Note from './components/Note';
import { handleSendAudio, handleGetTranscription } from './api/Api';

function App() {
  const [ content, setContent ] = useState('');
  const handleSubmit = async () => {
    await handleSendAudio();
    const transcription = await handleGetTranscription();
    setContent(transcription);
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        alignItems: 'center',
        minHeight: '100vh'
      }}
    >
      <Header />
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-around',
          alignItems: 'center',
          width: '100%',
        }}
      >
        <FileUpload onClick={handleSubmit} />
        <Note content={content}/>
      </Box>
      <Footer />
    </Box>
  );
}

export default App;
