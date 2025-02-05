import React, { useState } from "react";
import Box from "@mui/material/Box";

import FileUpload from "./FileUpload";
import Note from "./Note";
import { handleSendAudio, useFetchSites, useFetchDirectories } from "../api/Api";
import UploadingModal from "./UploadingModal";
import SuccessModal from "./SuccessModal";

const Main: React.FC = () => {
  const [project, setProject] = useState<{ id: string; name: string } | null>(null);
  const [projectDirectory, setProjectDirectory] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [content, setContent] = useState<string>("");
  const [isUploadingModalOpen, setIsUploadingModalOpen] = useState<boolean>(false);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = useState<boolean>(false);

  const { sitesData, sitesError, isSitesLoading } = useFetchSites();
  const { directoriesData, directoriesError } = useFetchDirectories(project);

  // プロジェクト変更処理
  const handleProjectChange = (site: { id: string; name: string } | null): void => {
    setProject(site);
  };

  // プロジェクトディレクトリ変更処理
  const handleProjectDirectoryChange = (directory: string): void => {
    setProjectDirectory(directory);
  };

  // ファイル変更処理
  const handleFileChange = (file: File | null): void => {
    setFile(file);
  };

  // アップロード処理
  const handleUpload = async (): Promise<void> => {
    if (!project) {
      alert("プロジェクトを選択してください");
      return;
    }
    if (!projectDirectory) {
      alert("プロジェクトディレクトリを選択してください");
      return;
    }
    if (!file) {
      alert("ファイルを選択してください");
      return;
    }

    setIsUploadingModalOpen(true);
    try {
      const transcription = await handleSendAudio(project, projectDirectory, file);
      setContent(transcription);
      setIsSuccessModalOpen(true);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("ファイルのアップロード中にエラーが発生しました。");
    } finally {
      setIsUploadingModalOpen(false);
      setProject(null);
      setProjectDirectory("");
      setFile(null);
    }
  };

  if (sitesError) {
    return <p style={{ color: "red" }}>サイトデータの取得中にエラーが発生しました。</p>;
  }
  if (directoriesError) {
    return <p style={{ color: "red" }}>ディレクトリデータの取得中にエラーが発生しました。</p>;
  }
  if (isSitesLoading) {
    return <p>プロジェクトを読み込んでいます...</p>;
  }

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
      <FileUpload
        sites={sitesData}
        directories={directoriesData}
        onFileChange={handleFileChange}
        onSubmit={handleUpload}
        onProjectChange={handleProjectChange}
        onProjectDirectoryChange={handleProjectDirectoryChange}
        file={file}
      />
      <Note content={content} />
      <UploadingModal open={isUploadingModalOpen} />
      <SuccessModal open={isSuccessModalOpen} onClose={() => setIsSuccessModalOpen(false)} />
    </Box>
  );
};

export default Main;
