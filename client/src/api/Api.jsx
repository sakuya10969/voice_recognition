import axios from 'axios';

const apiUrl = 'http:127.0.0.1:8000/transcribe';

export const handleSendAudio = async () => {
    try {
        const fileInput = document.getElementById('file-input');

        if (!fileInput.files.length) {
            alert('ファイルを選択してください');
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        await axios.post(apiUrl, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    } catch (error) {
        alert('ファイルのアップロードに失敗しました');
    }
}

export const handleGetTranscription = async () => {
    try {
        const response = await axios.get(apiUrl);
        return response.data
    } catch (error) {
        alert('テキストの取得に失敗しました');
    }
}