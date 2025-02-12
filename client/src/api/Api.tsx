import axios from "axios";
import useSWR from "swr";
import { useCallback } from "react";

// const apiUrl = "http://127.0.0.1:8000";
const apiUrl = "https://ca-vr-dev-010.purplewave-4065561a.eastasia.azurecontainerapps.io";

export const handleSendAudio = async (
    site: { id: string; name: string },
    directory: { id: string; name: string },
    subDirectory: { id: string, name: string } | null,
    file: File): Promise<string> => {
    try {
        const formData = new FormData();
        formData.append("site", site.id);
        if (subDirectory) {
            formData.append("directory", subDirectory.id);
        } else {
            formData.append("directory", directory.id);
        }
        formData.append("file", file);
        // **1. タスクIDを取得（処理開始）**
        const response = await axios.post(`${apiUrl}/transcribe`, formData, {
            headers: { "Content-Type": "multipart/form-data" },
        });
        const taskId = response.data.task_id;  // タスクIDを取得
        console.log(response.data.message);
        
        await new Promise(resolve => setTimeout(resolve, 10000));
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
                }
            }, 10000);
        });
    } catch (error) {
        throw new Error(error as string);
    }
};

const fetcher = (url: string) => axios.get(url).then((res) => res.data);
export const useFetchSites = () => {
    const { data, error, isLoading } = useSWR(`${apiUrl}/sites`, fetcher);
    return { sitesData: data?.value || [], sitesError: error, isSitesLoading: isLoading };
}

export const useFetchDirectories = (siteId: string) => {
    // site が null の場合は SWR を発火させない
    const shouldFetch = !!siteId;
    const fetchDirectories = useCallback(() => {
        return shouldFetch ? `${apiUrl}/directories?site_id=${encodeURIComponent(siteId)}` : null;
    }, [siteId]);
    const { data, error } = useSWR(fetchDirectories(), fetcher);
    return { directoriesData: data?.value || [], directoriesError: error };
};

export const useFetchSubDirectories = (
    siteId: string,
    directoryId: string
) => {
    const shouldFetch = !!siteId && !!directoryId;
    const fetchSubDirectories = useCallback(() => {
        return shouldFetch
            ? `${apiUrl}/subdirectories?site_id=${encodeURIComponent(siteId)}&directory_id=${encodeURIComponent(directoryId)}`
            : null;
    }, [siteId, directoryId]);
    const { data, error } = useSWR(fetchSubDirectories(), fetcher);
    console.log(data)
    return { subDirectoriesData: shouldFetch ? data?.value || [] : [], subDirectoriesError: shouldFetch ? error : null };
};
