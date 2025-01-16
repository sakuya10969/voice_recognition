import { Box, Typography } from "@mui/material";
import { useState } from "react";

import FileUpload from "./FileUpload";
import Note from "./Note";
import { handleSendAudio } from "../api/Api";

const Main = () => {
  const [content, setContent] = useState(""); // 音声文字起こしの結果
  const [isUploading, setUploading] = useState(false); // アップロード状態
  const [error, setError] = useState(null); // エラーメッセージ

  // ファイルアップロード処理
  const handleFileUpload = async ({ projectName, file }) => {
    setUploading(true); // アップロード状態を開始
    setError(null); // エラーリセット

    try {
      const transcription = await handleSendAudio(projectName, file); // APIリクエスト
      setContent(transcription); // 結果を状態に保存
    } catch (err) {
      console.error("Error uploading file:", err);
      setError("ファイルのアップロード中にエラーが発生しました。");
    } finally {
      setUploading(false); // アップロード状態を終了
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "space-around",
        alignItems: "center",
        width: "100%",
        padding: 3,
      }}
    >
      {/* ファイルアップロードフォーム */}
      <FileUpload
        onSubmit={handleFileUpload} // アップロード処理を渡す
        isUploading={isUploading} // アップロード状態を渡す
      />

      {/* テキスト表示 */}
      <Box sx={{ width: "40%" }}>
        {error && (
          <Typography
            variant="body1"
            color="error"
            sx={{ mb: 2, textAlign: "center" }}
          >
            {error}
          </Typography>
        )}
        <Note content={content} />
      </Box>
    </Box>
  );
};

export default Main;
