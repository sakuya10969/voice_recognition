import axios from "axios";
import useSWR from "swr";

// const apiUrl = "http://127.0.0.1:8000";
const apiUrl = "https://ca-vr-dev-010.graytree-f08985ca.koreacentral.azurecontainerapps.io";

const fetcher = (url: string) => axios.get(url).then((res) => res.data);

export const handleSendAudio = async (
    site: { id: string; name: string },
    directory: { id: string; name: string },
    subDirectory: { id: string, name: string } | null,
    file: File
): Promise<string> => {
    try {
        const formData = new FormData();
        formData.append("site", site.id);
        formData.append("directory", subDirectory ? subDirectory.id : directory.id);
        formData.append("file", file);

        // **1. タスクIDを取得（処理開始）**
        const response = await axios.post(`${apiUrl}/transcribe`, formData, {
            headers: { "Content-Type": "multipart/form-data" },
        });
        const taskId = response.data.task_id;  // タスクIDを取得
        console.log(response.data.message);

        await new Promise(resolve => setTimeout(resolve, 5000)); // 10秒待機

        // **2. タスクの完了をポーリングでチェック**
        return new Promise((resolve, reject) => {
            const interval = setInterval(async () => {
                try {
                    const statusResponse = await axios.get(`${apiUrl}/transcribe/${taskId}`, {
                        headers: {
                            "Cache-Control": "no-cache, no-store, must-revalidate",
                        }
                    });
                    console.log("APIレスポンス:", statusResponse.data);
                    const status = statusResponse.data.status;
                    console.log("現在のステータス:", status);

                    if (status === "completed") {
                        console.log("処理完了:", statusResponse.data.result);
                        clearInterval(interval); // **完了したらポーリング停止**
                        resolve(statusResponse.data.result);
                    } else if (status === "failed") {
                        console.error("処理失敗:", statusResponse.data.result);
                        clearInterval(interval); // **エラーの場合も停止**
                        reject(new Error(statusResponse.data.result));
                    } 
                } catch (error) {
                    console.error("ステータス取得エラー:", error);
                    clearInterval(interval); // **エラー発生時もポーリング停止**
                    reject(new Error("Failed to fetch transcription status"));
                }
            }, 60000);
        });
    } catch (error) {
        throw new Error(error as string);
    }
};

// **サイト一覧の取得**
export const useFetchSites = () => {
    const { data, error, isLoading } = useSWR(`${apiUrl}/sites`, fetcher, {
        revalidateOnFocus: false,  // **フォーカス時に再取得しない**
        dedupingInterval: 60000,   // **30秒間キャッシュを使う**
    });
    return { sitesData: data?.value || [], sitesError: error, isSitesLoading: isLoading };
};

// **ディレクトリ一覧の取得**
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

// **サブディレクトリ一覧の取得**
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
