import axios from "axios";
import { apiUrl } from "../constants/api";

interface TranscriptionResponse {
    task_id: string;
    status: string;
    transcribed_text?: string;
    summarized_text?: string;
}

export const handleSendAudio = async (
  site: { id: string; name: string } | null,
  directory: { id: string; name: string } | null,
  subDirectory: { id: string; name: string } | null,
  file: File
): Promise<{ transcribed_text: string; summarized_text: string }> => {
  try {
    const formData = new FormData();
    if (!site && !directory && !subDirectory) {
      formData.append("file", file);
    } else {
      if (site && !directory) throw new Error("サイトを選択した場合、ディレクトリの選択が必要です");
      if (site) formData.append("site", site.id);
      formData.append("directory", subDirectory?.id || directory?.id || "");
      formData.append("file", file);
    }

    const response = await axios.post<{ task_id: string; message: string }>(`${apiUrl}/transcription`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    console.log(response.data.message);

    await new Promise((resolve) => setTimeout(resolve, 5000));
    return await pollTranscriptionStatus(response.data.task_id);
  } catch (error) {
    console.error("音声送信エラー:", error);
    throw new Error(error instanceof Error ? error.message : "Failed to send audio");
  }
};

const pollTranscriptionStatus = async (
  taskId: string
): Promise<{ transcribed_text: string; summarized_text: string }> => {
  const pollingInterval = 40000;
  return new Promise((resolve, reject) => {
    const interval = setInterval(async () => {
      try {
        const res = await axios.get<TranscriptionResponse>(`${apiUrl}/transcription/${taskId}`, {
          headers: { "Cache-Control": "no-cache, no-store, must-revalidate" },
        });

        const { status, transcribed_text, summarized_text } = res.data;
        if (status === "completed") {
          clearInterval(interval);
          if (transcribed_text && summarized_text) {
            resolve({ transcribed_text, summarized_text });
          } else {
            reject(new Error("Missing transcription or summary data"));
          }
        } else if (status === "failed") {
          clearInterval(interval);
          reject(new Error("Transcription process failed"));
        }
      } catch (err) {
        clearInterval(interval);
        reject(new Error(err instanceof Error ? err.message : "Failed to fetch transcription status"));
      }
    }, pollingInterval);
  });
};
