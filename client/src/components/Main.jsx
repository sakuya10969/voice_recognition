import { Box } from "@mui/material";
import { useState } from "react";

import FileUpload from "./FileUpload";
import Note from "./Note";
import { handleSendAudio } from "../api/Api";

const Main = () => {
  const [content, setContent] = useState(""); // 音声文字起こしの結果
  const [isUploading, setIsUploading] = useState(false); // アップロード状態

  // ファイルアップロード処理
  const handleFileUpload = async ({ projectName, file }) => {
    setIsUploading(true); // アップロード状態を開始

    try {
      const transcription = await handleSendAudio(projectName, file); // APIリクエスト
      setContent(transcription); // 結果を状態に保存
    } catch (err) {
      console.error("Error uploading file:", err);
      alert("ファイルのアップロードに失敗しました");
    } finally {
      setIsUploading(false); // アップロード状態を終了
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
      <Note content={content} />
    </Box>
  );
};

export default Main;
