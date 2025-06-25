import { useMutation } from '@tanstack/react-query';

import { handleTranscription } from '@/api/transcription';
import type { TranscriptionResult, TranscriptionParams } from '@/types';

export const useTranscription = () => {
  const mutation = useMutation<TranscriptionResult, Error, TranscriptionParams>({
    mutationFn: ({ site, directory, subDirectory, file }) =>
      handleTranscription(site, directory, subDirectory, file),
  });

  return {
    mutateAsync: mutation.mutateAsync,
    isPending: mutation.isPending,
    reset: mutation.reset,
  };
};
