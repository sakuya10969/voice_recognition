import axios from "axios";

const apiUrl = "http://127.0.0.1:8000";
// const apiUrl = "https://app-vr-dev-010-ajfwaffjh6gqchf0.eastasia-01.azurewebsites.net/transcribe";


export const handleSendAudio = async (project, projectDirectory, file) => {
    try {
        if (!file) {
            alert("ファイルを選択してください");
            return;
        }

        const formData = new FormData();
        formData.append("project_name", project.name);
        formData.append("project_directory", projectDirectory);
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

export const fetchSites = async () => {
    try{
        const response = await axios.get(`${apiUrl}/sites`);
        return response.data;
    } catch (error) {
        alert("サイトの取得に失敗しました");
        throw error;
    }
}

export const fetchDirectories = async (site) => {
    try {
        const response = await axios.get(`${apiUrl}/directories/${site.id}`);
        return response.data;
    } catch (error) {
        alert("ディレクトリの取得に失敗しました");
    }
}
