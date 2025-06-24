// components/FileUpload.tsx
import React, { useState, useEffect, useCallback } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Send from '@mui/icons-material/Send';
import { useAtom } from 'jotai';

import { searchValueAtom } from '@/store/atoms';
import SearchField from '@/components/SearchField';
import SPOSelection from '@/components/SPOSelection';
import FileDropZone from '@/components/FileDropZone';
import { SPOData, FileUploadProps } from '@/types';

const FileUploadField = ({
  sites,
  directories,
  subDirectories,
  onFileChange,
  onSubmit,
  onSiteChange,
  onDirectoryChange,
  onSubDirectoryChange,
  file,
  selectedSiteId,
  selectedDirectoryId,
  selectedSubDirectoryId,
}: FileUploadProps) => {
  const [errorFileType, setErrorFileType] = useState<boolean>(false);
  const [filteredSites, setFilteredSites] = useState<SPOData[]>(sites);
  const [searchValue, setSearchValue] = useAtom<string>(searchValueAtom);

  useEffect(() => {
    setFilteredSites(sites);
  }, [sites]);

  const handleSearch = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setSearchValue(value);
      setFilteredSites(
        value.trim() === '' ? sites : sites.filter((site) => (site.name || '').includes(value))
      );
    },
    [sites, setSearchValue]
  );

  return (
    <Box
      component="form"
      onSubmit={(e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        onSubmit();
      }}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        borderRadius: '5px',
        p: 3,
        width: '500px',
      }}
    >
      <Typography fontWeight="bold" align="left" sx={{ fontSize: 'x-large', mb: 2 }}>
        議事録ファイル出力先
      </Typography>

      <SearchField value={searchValue} onChange={handleSearch} />

      <SPOSelection
        sites={filteredSites}
        directories={directories}
        subDirectories={subDirectories}
        selectedSiteId={selectedSiteId}
        selectedDirectoryId={selectedDirectoryId}
        selectedSubDirectoryId={selectedSubDirectoryId}
        onSiteChange={onSiteChange}
        onDirectoryChange={onDirectoryChange}
        onSubDirectoryChange={onSubDirectoryChange}
      />

      <FileDropZone
        file={file}
        errorFileType={errorFileType}
        onFileChange={(f) => {
          if (!f) setErrorFileType(true);
          else {
            setErrorFileType(false);
            onFileChange(f);
          }
        }}
      />

      <Button
        type="submit"
        disabled={!file}
        endIcon={<Send />}
        sx={{
          color: 'white',
          backgroundColor: 'black',
          borderRadius: '5px',
          width: '120px',
          ':disabled': {
            backgroundColor: 'whitesmoke',
          },
          '&:hover': {
            backgroundColor: 'black',
          },
        }}
      >
        送信する
      </Button>
    </Box>
  );
};

export default FileUploadField;
