import React, { useState } from "react";
import Box from "@mui/material/Box";

import FileUpload from "./FileUpload";
import Note from "./Note";
import { handleSendAudio, useFetchSites, useFetchDirectories, useFetchSubDirectories } from "../api/Api";
import UploadingModal from "./UploadingModal";
import SuccessModal from "./SuccessModal";

const Main: React.FC = () => {
  const [site, setSite] = useState<{ id: string; name: string } | null>(null);
  const [directory, setDirectory] = useState<{ id: string; name: string } | null>(null);
  const [subDirectory, setSubDirectory] = useState<{ id: string; name: string } | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [summarizedText, setSummarizedText] = useState<string>("");
  const [transcribedText, setTranscribedText] = useState<string>("");
  const [isUploadingModalOpen, setIsUploadingModalOpen] = useState<boolean>(false);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = useState<boolean>(false);

  const { sitesData, sitesError, isSitesLoading } = useFetchSites();
  const { directoriesData, directoriesError } = useFetchDirectories(site?.id ?? "");
  const { subDirectoriesData, subDirectoriesError } = useFetchSubDirectories(site?.id ?? "", directory?.id ?? "");

  // プロジェクト変更処理
  const handleSiteChange = (site: { id: string; name: string } | null): void => {
    setSite(site);
  };

  // プロジェクトディレクトリ変更処理
  const handleDirectoryChange = (directory: { id: string; name: string } | null): void => {
    setDirectory(directory);
  };

  // プロジェクトサブディレクトリ変更処理
  const handleSubDirectoryChange = (subDirectory: { id: string, name: string } | null): void => {
    setSubDirectory(subDirectory);
  }

  // ファイル変更処理
  const handleFileChange = (file: File | null): void => {
    setFile(file);
  };

  // アップロード処理
  const handleUpload = async (): Promise<void> => {
    if (!site) {
      alert("プロジェクトを選択してください");
      return;
    }
    if (!directory) {
      alert("ディレクトリを選択してください");
      return;
    }
    if (!file) {
      alert("ファイルを選択してください");
      return;
    }

    setIsUploadingModalOpen(true);
    try {
      const transcription = await handleSendAudio(site, directory, subDirectory, file);
      setTranscribedText(transcription.transcribed_text);
      setSummarizedText(transcription.summarized_text);
      setIsSuccessModalOpen(true);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("ファイルのアップロード中にエラーが発生しました。");
    } finally {
      setIsUploadingModalOpen(false);
      setSite(null);
      setDirectory(null);
      setFile(null);
    }
  };

  if (sitesError) {
    return <p style={{ color: "red" }}>サイトデータの取得中にエラーが発生しました。</p>;
  }
  if (isSitesLoading) {
    return <p>サイトを読み込んでいます...</p>;
  }
  if (directoriesError) {
    return <p style={{ color: "red" }}>ディレクトリデータの取得中にエラーが発生しました。</p>;
  }
  if (subDirectoriesError) {
    return <p style={{ color: "red" }}>サブディレクトリデータの取得中にエラーが発生しました。</p>;
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
        subDirectories={subDirectoriesData}
        onFileChange={handleFileChange}
        onSubmit={handleUpload}
        onSiteChange={handleSiteChange}
        onDirectoryChange={handleDirectoryChange}
        onSubDirectoryChange={handleSubDirectoryChange}
        file={file}
      />
      <Note transcribedText={transcribedText} summarizedText={summarizedText} />
      <UploadingModal open={isUploadingModalOpen} />
      <SuccessModal open={isSuccessModalOpen} onClose={() => setIsSuccessModalOpen(false)} />
    </Box>
  );
};

export default Main;
