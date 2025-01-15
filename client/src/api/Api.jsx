import axios from "axios";

// const apiUrl = "http://127.0.0.1:8000/transcribe";
const apiUrl = "https://20.78.45.241/transcribe";


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
