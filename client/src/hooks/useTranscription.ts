import { useMutation } from '@tanstack/react-query';

import { handleTranscription } from '@/api/transcription';
import type { TranscriptionResult, TranscriptionParams } from '@/types';

export const useTranscription = () => {
  const mutation = useMutation<TranscriptionResult, Error, TranscriptionParams>({
    mutationFn: ({ apiUrl, site, directory, subDirectory, file }) =>
      handleTranscription(apiUrl, site, directory, subDirectory, file),
  });

  // ローディング状況も返す
  return {
    ...mutation,
    isLoading: mutation.status === 'pending',
  };
};