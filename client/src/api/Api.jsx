import axios from "axios";
import useSWR from "swr";
import { v4 as uuidv4 } from "uuid";

// const apiUrl = "http://127.0.0.1:8000";
// const apiUrl = "http://localhost:8000";
const apiUrl = "https://ca-vr-dev-010--wnjhfc8.graypond-9888a1dd.japaneast.azurecontainerapps.io/";

const getClientId = () => {
    let clientId = localStorage.getItem("client_id");
    if (!clientId) {
        clientId = uuidv4();
        localStorage.setItem("client_id", clientId);
    }
    return clientId;
}

export const handleSendAudio = async (file) => {
    // Promiseでラップして非同期にデータを取得
    return new Promise((resolve, reject) => {
        try {
            const clientId = getClientId();
            let formData = new FormData();
            // formData.append("project", project.name);
            // formData.append("project_directory", projectDirectory);
            formData.append("file", file);
            formData.append("client_id", clientId);

            // WebSocket接続
            const wsUrl = apiUrl.replace("http", "ws") + `/ws/${clientId}`;
            const socket = new WebSocket(wsUrl);


            socket.onmessage = (e) => {
                resolve(e.data); // 受信データを返す
                socket.close();  // 受信後すぐに切断
            };

            socket.onerror = (error) => {
                reject(new Error(error));
                socket.close();
            };

            axios.post(`${apiUrl}/transcribe`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
            }).catch((error) => reject(new Error(error)));
;

        } catch (error) {
            reject(new Error(error));
        }
    });
};

const fetcher = (url) => axios.get(url).then((res) => res.data);
export const useFetchSites = () => {
    const { data, error, isLoading } = useSWR(`${apiUrl}/sites`, fetcher);
    return { sitesData: data?.value || [], sitesError: error, isSitesLoading: isLoading };
}

export const useFetchDirectories = (site) => {
    const { data, error, isloading } = useSWR(`${apiUrl}/directories/${site.id}`, fetcher, {
        refreshInterval: 10000
    });
    return { directoriesData: data?.value || [], directoriesError: error, IsDirectoriesLoading: isloading };
}
