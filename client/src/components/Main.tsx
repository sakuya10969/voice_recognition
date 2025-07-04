import React, { useState, useMemo, useEffect } from 'react';
import Box from '@mui/material/Box';
import { useAtom } from 'jotai';
import { useSearchParams } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';

import FileUploadField from '@/components/FileUploadField';
import Note from '@/components/Note';
import { useGetSites } from '@/hooks/useGetSites';
import { useGetDirectories } from '@/hooks/useGetDirectories';
import { useGetSubDirectories } from '@/hooks/useGetSubDirectories';
import UploadingModal from '@/components/UploadingModal';
import SuccessModal from '@/components/SuccessModal';
import { searchValueAtom } from '@/store/atoms';
import LinkCopyButton from '@/components/LinkCopyButton';
import Loading from '@/components/Loading';
import Error from '@/components/Error';
import { useTranscription } from '@/hooks/useTranscription';
import { SPOData } from '@/types';

const Main = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { sitesData, isSitesLoading, sitesError } = useGetSites();

  const selectedSite = useMemo(() => {
    if (!sitesData) return null;
    const siteParam = decodeURIComponent(searchParams.get('site') ?? '').trim();
    return sitesData.find((s: SPOData) => s.id.trim() === siteParam) || null;
  }, [searchParams, sitesData]);

  const { directoriesData } = useGetDirectories(selectedSite?.id ?? '');

  const selectedDirectory = useMemo(() => {
    if (!directoriesData) return null;
    const dirParam = decodeURIComponent(searchParams.get('directory') ?? '').trim();
    return (
      directoriesData.find((d: SPOData) => d.id.trim() === dirParam) || null
    );
  }, [searchParams, directoriesData]);

  const { subDirectoriesData } = useGetSubDirectories(
    selectedSite?.id ?? '',
    selectedDirectory?.id ?? ''
  );

  const selectedSubDirectory = useMemo(() => {
    if (!subDirectoriesData) return null;
    const subDirParam = decodeURIComponent(searchParams.get('subdirectory') ?? '').trim();
    return (
      subDirectoriesData.find((sd: SPOData) => sd.id.trim() === subDirParam) || null
    );
  }, [searchParams, subDirectoriesData]);

  const [file, setFile] = useState<File | null>(null);
  const [summarizedText, setSummarizedText] = useState<string>('');
  const [transcribedText, setTranscribedText] = useState<string>('');
  const [isSuccessModalOpen, setIsSuccessModalOpen] = useState<boolean>(false);
  const [, setSearchValue] = useAtom(searchValueAtom);

  const { mutateAsync: handleTranscription, isPending: isTranscribing, reset } = useTranscription();

  const updateQueryParams = (updates: Record<string, string | null>) => {
    setSearchParams(
      (prevParams) => {
        const newParams = new URLSearchParams(prevParams);
        Object.entries(updates).forEach(([key, value]) => {
          if (value) {
            newParams.set(key, value);
          } else {
            newParams.delete(key);
          }
        });
        return newParams;
      },
      { replace: true }
    );
  };

  useEffect(() => {
    const navEntries = performance.getEntriesByType('navigation');
    if (navEntries.length > 0 && navEntries[0].type === 'reload') {
      updateQueryParams({ site: null, directory: null, subdirectory: null });
    }
  }, []);

  const handleSiteChange = (site: SPOData | null) => {
    updateQueryParams({ site: site?.id ?? '', directory: '', subdirectory: '' });
  };

  const handleDirectoryChange = (directory: SPOData | null) => {
    updateQueryParams({ directory: directory?.id ?? '', subdirectory: '' });
  };

  const handleSubDirectoryChange = (subDirectory: SPOData | null) => {
    updateQueryParams({ subdirectory: subDirectory?.id ?? '' });
  };

  const handleFileChange = (file: File | null) => setFile(file);

  const handleUpload = async () => {
    if (!file) {
      alert('ファイルを選択してください');
      return;
    }
    try {
      const transcription = await handleTranscription({
        site: selectedSite,
        directory: selectedDirectory,
        subDirectory: selectedSubDirectory,
        file,
      });
  
      setTranscribedText(transcription.transcribed_text);
      setSummarizedText(transcription.summarized_text);
  
      setIsSuccessModalOpen(true);
  
      setSearchValue('');
      updateQueryParams({ site: null, directory: null, subdirectory: null });
      setFile(null);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '100%',
        overflowY: 'auto',
      }}
    >
      <CssBaseline />
      {sitesError && <Error />}
      {isSitesLoading && <Loading />}
      {!sitesError && !isSitesLoading && (
        <>
          {selectedDirectory && (
            <Box mt={2}>
              <LinkCopyButton />
            </Box>
          )}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-around',
              alignItems: 'center',
              width: '100%',
            }}
          >
            <FileUploadField
              sites={sitesData}
              directories={directoriesData}
              subDirectories={subDirectoriesData}
              onFileChange={handleFileChange}
              onSubmit={handleUpload}
              onSiteChange={handleSiteChange}
              onDirectoryChange={handleDirectoryChange}
              onSubDirectoryChange={handleSubDirectoryChange}
              file={file}
              selectedSiteId={selectedSite?.id || ''}
              selectedDirectoryId={selectedDirectory?.id || ''}
              selectedSubDirectoryId={selectedSubDirectory?.id || ''}
            />
            <Note transcribedText={transcribedText} summarizedText={summarizedText} />
          </Box>
        </>
      )}
      <UploadingModal open={isTranscribing} onClose={() => reset()} />
      <SuccessModal open={isSuccessModalOpen} onClose={() => setIsSuccessModalOpen(false)} />
    </Box>
  );
};

export default Main;
