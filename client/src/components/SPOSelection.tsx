import React from 'react';
import { FormControl, InputLabel, MenuItem, Select, Box } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import HomeWorkIcon from '@mui/icons-material/HomeWork';
import FolderIcon from '@mui/icons-material/Folder';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';

import { theme } from '@/theme/theme';
import { SPOSelectionProps } from '@/types';

const SPOSelection = ({
  sites,
  directories,
  subDirectories,
  selectedSiteId,
  selectedDirectoryId,
  selectedSubDirectoryId,
  onSiteChange,
  onDirectoryChange,
  onSubDirectoryChange,
}: SPOSelectionProps) => {
  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, width: '100%' }}>
        <HomeWorkIcon sx={{ mr: 1 }} />
        <FormControl fullWidth size="small">
          <InputLabel id="site-select-label">SPOサイト</InputLabel>
          <Select
            labelId="site-select-label"
            value={selectedSiteId}
            label="SPOサイト"
            MenuProps={{
              PaperProps: {
                style: { width: 400, maxHeight: 450, overflowX: 'auto' },
              },
            }}
          >
            {sites.map((site) => (
              <MenuItem key={site.id} value={site.id} onClick={() => onSiteChange(site)}>
                {site.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, width: '100%' }}>
        <FolderIcon sx={{ mr: 1 }} />
        <FormControl fullWidth size="small">
          <InputLabel id="directory-select-label">ディレクトリ</InputLabel>
          <Select
            labelId="directory-select-label"
            value={selectedDirectoryId}
            label="ディレクトリ"
            MenuProps={{
              PaperProps: {
                style: { width: 400, maxHeight: 450, overflowX: 'auto' },
              },
            }}
          >
            {directories.map((directory) => (
              <MenuItem
                key={directory.id}
                value={directory.id}
                onClick={() => onDirectoryChange(directory)}
              >
                {directory.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, width: '100%' }}>
        <FolderOpenIcon sx={{ mr: 1 }} />
        <FormControl fullWidth size="small">
          <InputLabel id="subdirectory-select-label">サブディレクトリ</InputLabel>
          <Select
            labelId="subdirectory-select-label"
            value={selectedSubDirectoryId}
            label="サブディレクトリ"
            MenuProps={{
              PaperProps: {
                style: { width: 400, maxHeight: 450, overflowX: 'auto' },
              },
            }}
          >
            {subDirectories.map((subDirectory) => (
              <MenuItem
                key={subDirectory.id}
                value={subDirectory.id}
                onClick={() => onSubDirectoryChange(subDirectory)}
              >
                {subDirectory.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
    </ThemeProvider>
  );
};

export default SPOSelection;
