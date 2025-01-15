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
        console.error("Error", {
            message: error.message,
            name: error.name,
            code: error.code,
            config: error.config,
            request: error.request,
            response: error.response ? {
                data: error.response.data,
                status: error.response.status,
                headers: error.response.headers
            } : null
        });
        alert("ファイルのアップロードに失敗しました");
        throw error;
    }
}
