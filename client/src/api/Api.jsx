import axios from "axios";

// const apiUrl = "http://127.0.0.1:8000/transcribe";
const apiUrl = "http://app-vr-dev-010-ajfwaffjh6gqchf0.eastasia-01.azurewebsites.net/transcribe";


export const handleSendAudio = async (file) => {
    try {
        if (!file) {
            alert("ファイルを選択してください");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        const response = await axios.post(apiUrl, formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
            timeout: 3600000
        });

        return response.data
    } catch (error) {
        alert("ファイルのアップロードに失敗しました");
        throw error;
    }
}
