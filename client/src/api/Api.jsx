import axios from "axios";

const apiUrl = "http://localhost:7071/transcribe";

export const handleSendAudio = async (file) => {
    try {
        if (!file) {
            alert('ファイルを選択してください');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        const response = await axios.post(apiUrl, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return response.data
    } catch (error) {
        alert('ファイルのアップロードに失敗しました');
    }
}