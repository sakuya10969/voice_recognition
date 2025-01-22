import React, { useState, useEffect } from "react";
import Box from "@mui/material/Box";
import FileUpload from "./FileUpload";
import Note from "./Note";
import { handleSendAudio, fetchSites, fetchDirectories } from "../api/Api";
import UploadingModal from "./UploadingModal";
import SuccessModal from "./SuccessModal";

const Main = () => {
  const [sites, setSites] = useState([]);
  const [directories, setDirectories] = useState([]);
  const [project, setProject] = useState("");
  const [projectDirectory, setProjectDirectory] = useState("");
  const [file, setFile] = useState(null);
  const [content, setContent] = useState("");
  const [isUploadingModalOpen, setIsUploadingModalOpen] = useState(false);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = useState(false);

  useEffect(() => {
    const loadSites = async () => {
      try {
        const data = await fetchSites();
        setSites(data.value || []);
      } catch (e) {
        console.error("Error fetching sites:", e);
      }
    };
    loadSites();
  }, []);

  const handleProjectChange = async (site) => {
    setProject(site);
    setProjectDirectory("");
    setDirectories([]);

    if (site) {
      try {
        const data = await fetchDirectories(site);
        setDirectories(data.value || []);
      } catch (error) {
        console.error("Error fetching directories:", error);
      }
    }
  };

  const handleProjectDirectoryChange = (directory) => {
    setProjectDirectory(directory);
  };

  const handleFileChange = (file) => {
    setFile(file);
  };

  const handleUpload = async () => {
    if (!project || !projectDirectory) {
      alert("プロジェクトとディレクトリを選択してください");
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
      setIsUploadingModalOpen(false);
      setIsSuccessModalOpen(true);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("ファイルのアップロード中にエラーが発生しました。");
      setIsUploadingModalOpen(false);
    } finally {
      setFile(null);
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
      <FileUpload
        sites={sites}
        directories={directories}
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
