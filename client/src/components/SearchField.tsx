import React from 'react';
import TextField from '@mui/material/TextField';
import { ThemeProvider } from '@mui/material/styles';
import SearchIcon from '@mui/icons-material/Search';
import Box from '@mui/material/Box';

import { theme } from '@/theme/theme';
import { SearchFieldProps } from '@/types';

const SearchField = ({ value, onChange }: SearchFieldProps) => (
  <ThemeProvider theme={theme}>
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, width: '100%' }}>
      <SearchIcon sx={{ mr: 1 }} />
      <TextField
        label="SPOサイトキーワード"
        variant="outlined"
        size="small"
        fullWidth
        value={value}
        onChange={onChange}
        sx={{
          '& input': {
            backgroundColor: 'white',
          },
        }}
      />
    </Box>
  </ThemeProvider>
);

export default SearchField;
