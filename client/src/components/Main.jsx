import React, { useState } from "react";
import Box from "@mui/material/Box";

import FileUpload from "./FileUpload";
import Note from "./Note";
import { handleSendAudio,useFetchSites, useFetchDirectories } from "../api/Api";
import UploadingModal from "./UploadingModal";
import SuccessModal from "./SuccessModal";

const Main = () => {
  const [project, setProject] = useState("");
  const [projectDirectory, setProjectDirectory] = useState("");
  const [file, setFile] = useState(null);
  const [content, setContent] = useState("");
  const [isUploadingModalOpen, setIsUploadingModalOpen] = useState(false);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = useState(false);
  const { sitesData, sitesError, isSitesLoading } = useFetchSites();
  const { directoriesData, directoriesError, isDirectoriesLoading } = useFetchDirectories(project);

  const handleProjectChange = async (site) => {
    setProject(site);
  };

  const handleProjectDirectoryChange = (directory) => {
    setProjectDirectory(directory);
  };

  const handleFileChange = (file) => {
    setFile(file);
  };

  const handleUpload = async () => {
    if (!project) {
      alert("プロジェクトを選択してください");
      return;
    }
    if (!projectDirectory) {
      alert("プロジェクトディレクトリを選択してください");
    }
    if (!file) {
      alert("ファイルを選択してください");
    }
    setIsUploadingModalOpen(true);
    try {
      const transcription = await handleSendAudio(project, projectDirectory, file);
      setContent(transcription);
      setIsUploadingModalOpen(false);
      setIsSuccessModalOpen(true);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("ファイルのアップロード中にエラーが発生しました。");
      setIsUploadingModalOpen(false);
    } finally {
      setProject("");
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
  if (isSitesLoading || isDirectoriesLoading) {
    return <p>データを読み込んでいます...</p>;
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
      <UploadingModal open={isUploadingModalOpen} onClose={() => setIsUploadingModalOpen(false)} />
      <SuccessModal open={isSuccessModalOpen} onClose={() => setIsSuccessModalOpen(false)} />
    </Box>
  );
};

export default Main;
