import axios from "axios";
import useSWR from "swr";

interface TranscriptionResponse {
    task_id: string;
    status: string;
    transcribed_text?: string;
    summarized_text?: string;
}

// const apiUrl = "http://127.0.0.1:8000";
const apiUrl = "https://ca-vr-dev-010.politecoast-4904dd91.eastasia.azurecontainerapps.io";

const fetcher = async (url: string) => {
    const response = await axios.get(url);
    return response.data;
};

export const handleSendAudio = async (
    site: { id: string; name: string } | null,
    directory: { id: string; name: string } | null,
    subDirectory: { id: string; name: string } | null,
    file: File
): Promise<{ transcribed_text: string; summarized_text: string }> => {
    try {
        const formData = new FormData();
        // すべてがnullの場合は送信する
        if (!site && !directory && !subDirectory) {
            formData.append("file", file);
        } else {
            // siteがある場合、directoryも必須
            if (site && !directory) {
                throw new Error("サイトを選択した場合、ディレクトリの選択が必要です");
            }
            // siteがある場合は送信
            if (site) {
                formData.append("site", site.id);
            }
            // subDirectoryがあればそれを送信、なければdirectoryを送信
            if (subDirectory) {
                formData.append("directory", subDirectory.id);
            } else if (directory) {
                formData.append("directory", directory.id);
            }
            formData.append("file", file);
        }
        // タスクIDを取得
        const response = await axios.post<{ task_id: string; message: string }>(`${apiUrl}/transcribe`, formData, {
            headers: { "Content-Type": "multipart/form-data" },
        });
        const taskId = response.data.task_id;
        console.log(response.data.message);
        // 5秒待機（初期処理の安定化）
        await new Promise(resolve => setTimeout(resolve, 5000));
        // **2. タスクの完了をポーリングでチェック**
        return await pollTranscriptionStatus(taskId);
    } catch (error) {
        console.error("音声送信エラー:", error);
        throw new Error(error instanceof Error ? error.message : "Failed to send audio");
    }
};
// ポーリング処理
const pollTranscriptionStatus = async (taskId: string): Promise<{ transcribed_text: string; summarized_text: string }> => {
    const pollingInterval = 40000;

    return new Promise((resolve, reject) => {
        const interval = setInterval(async () => {
            try {
                const statusResponse = await axios.get<TranscriptionResponse>(`${apiUrl}/transcribe/${taskId}`, {
                    headers: { "Cache-Control": "no-cache, no-store, must-revalidate" }
                });
                console.log("APIレスポンス:", statusResponse.data);

                const { status, transcribed_text, summarized_text } = statusResponse.data;
                console.log("現在のステータス:", status);

                if (status === "completed") {
                    clearInterval(interval);
                    if (transcribed_text && summarized_text) {
                        console.log("処理完了:", { transcribed_text, summarized_text });
                        resolve({ transcribed_text, summarized_text });
                    } else {
                        console.warn("処理は完了したが、データが不足している可能性あり。");
                        reject(new Error("Missing transcription or summary data"));
                    }
                } else if (status === "failed") {
                    clearInterval(interval);
                    console.error("処理失敗:", statusResponse.data);
                    reject(new Error("Transcription process failed"));
                }
            } catch (error) {
                clearInterval(interval);
                console.error("ステータス取得エラー:", error);
                reject(new Error(error instanceof Error ? error.message : "Failed to fetch transcription status"));
            }
        }, pollingInterval);
    });
};

// サイト一覧の取得
export const useFetchSites = () => {
    const { data, error, isLoading } = useSWR(`${apiUrl}/sites`, fetcher, {
        revalidateOnFocus: false,  // フォーカス時に再取得しない
        dedupingInterval: 60000,   // 60秒間キャッシュを使う
    });
    return { sitesData: data?.value || [], sitesError: error, isSitesLoading: isLoading };
};

// ディレクトリ一覧の取得
export const useFetchDirectories = (siteId: string | null) => {
    const { data, error } = useSWR(
        siteId ? `${apiUrl}/directories?site_id=${encodeURIComponent(siteId)}` : null,
        fetcher,
        {
            revalidateOnFocus: false,
            dedupingInterval: 60000,
        }
    );
    return { directoriesData: data?.value || [], directoriesError: error };
};

// サブディレクトリ一覧の取得
export const useFetchSubDirectories = (siteId: string | null, directoryId: string | null) => {
    const { data, error } = useSWR(
        siteId && directoryId
            ? `${apiUrl}/subdirectories?site_id=${encodeURIComponent(siteId)}&directory_id=${encodeURIComponent(directoryId)}`
            : null,
        fetcher,
        {
            revalidateOnFocus: false,
            dedupingInterval: 30000,
        }
    );
    return { subDirectoriesData: data?.value || [], subDirectoriesError: error };
};
