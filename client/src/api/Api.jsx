import axios from "axios";
import useSWR from "swr";

const apiUrl = "http://127.0.0.1:8000";
// const apiUrl = "https://app-vr-dev-010-ajfwaffjh6gqchf0.eastasia-01.azurewebsites.net/transcribe";

const fetcher = (url) => axios.get(url).then((res) => res.data);

export const handleSendAudio = async (file) => {
    try {
        const formData = new FormData();
        // formData.append("project", project.name);
        // formData.append("project_directory", projectDirectory);
        formData.append("file", file);

        const response = await axios.post(`${apiUrl}/transcribe`, formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });

        return response.data
    } catch (error) {
        alert("ファイルのアップロードに失敗しました");
        throw error;
    }
}

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
