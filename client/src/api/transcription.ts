import axios from 'axios';

import { SPOData, TranscriptionResult, TranscriptionResponse } from '@/types';
import { apiUrl } from '@/constants';

const validateSPODatas = (site: SPOData | null, directory: SPOData | null): void => {
  if (site && !directory) {
    throw new Error('サイトを選択した場合、ディレクトリの選択が必要です');
  }
};

const createFormData = (
  site: SPOData | null,
  directory: SPOData | null,
  subDirectory: SPOData | null,
  file: File
): FormData => {
  const formData = new FormData();

  if (site) {
    formData.append('site', site.id);
  }

  const directoryId = subDirectory?.id || directory?.id || '';
  if (directoryId) {
    formData.append('directory', directoryId);
  }

  formData.append('file', file);
  return formData;
};

export const handleTranscription = async (
  site: SPOData | null,
  directory: SPOData | null,
  subDirectory: SPOData | null,
  file: File
): Promise<TranscriptionResult> => {
  try {
    validateSPODatas(site, directory);
    const formData = createFormData(site, directory, subDirectory, file);

    const response = await axios.post<{ task_id: string; message: string }>(
      `${apiUrl}/transcription`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    console.log(response.data.message);

    await new Promise((resolve) => setTimeout(resolve, 5000));
    return await pollTranscriptionStatus(response.data.task_id);
  } catch (error) {
    console.error('音声送信エラー:', error);
    throw new Error(error instanceof Error ? error.message : 'Failed to send audio');
  }
};

const pollTranscriptionStatus = async (
  taskId: string
): Promise<TranscriptionResult> => {
  const POLLING_INTERVAL = 40000;

  return new Promise((resolve, reject) => {
    const interval = setInterval(async () => {
      try {
        const res = await axios.get<TranscriptionResponse>(`${apiUrl}/transcription/${taskId}`, {
          headers: { 'Cache-Control': 'no-cache, no-store, must-revalidate' },
        });

        const { status, transcribed_text, summarized_text } = res.data;

        if (status === 'completed') {
          clearInterval(interval);
          if (transcribed_text && summarized_text) {
            resolve({ transcribed_text, summarized_text });
          } else {
            reject(new Error('Missing transcription or summary data'));
          }
        } else if (status === 'failed') {
          clearInterval(interval);
          reject(new Error('Transcription process failed'));
        }

        // statusが "processing" 等なら何もせず次回へ
      } catch (err) {
        clearInterval(interval);
        reject(
          new Error(err instanceof Error ? err.message : 'Failed to fetch transcription status')
        );
      }
    }, POLLING_INTERVAL);
  });
};
