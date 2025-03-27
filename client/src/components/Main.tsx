import React, { useState, useMemo, useEffect } from "react";
import Box from "@mui/material/Box";
import { useAtom } from "jotai";
import { useSearchParams } from "react-router-dom";
import CssBaseline from "@mui/material/CssBaseline"

import FileUpload from "./FileUpload";
import Note from "./Note";
import { handleSendAudio, useFetchSites, useFetchDirectories, useFetchSubDirectories } from "../api/Api";
import UploadingModal from "./UploadingModal";
import SuccessModal from "./SuccessModal";
import { searchValueAtom } from "../store/atoms";
import LinkCopyButton from "./LinkCopyButton";

const Main: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { sitesData, sitesError, isSitesLoading } = useFetchSites();

  const selectedSite = useMemo(() => {
    if (!sitesData) return null;
    const siteParam = decodeURIComponent(searchParams.get("site") ?? "").trim();
    return sitesData.find((s: { id: string; name: string }) => s.id.trim() === siteParam) || null;
  }, [searchParams, sitesData]);

  const { directoriesData } = useFetchDirectories(selectedSite?.id ?? "");

  const selectedDirectory = useMemo(() => {
    if (!directoriesData) return null;
    const dirParam = decodeURIComponent(searchParams.get("directory") ?? "").trim();
    return directoriesData.find((d: { id: string; name: string }) => d.id.trim() === dirParam) || null;
  }, [searchParams, directoriesData]);

  const { subDirectoriesData } = useFetchSubDirectories(selectedSite?.id ?? "", selectedDirectory?.id ?? "");

  const selectedSubDirectory = useMemo(() => {
    if (!subDirectoriesData) return null;
    const subDirParam = decodeURIComponent(searchParams.get("subdirectory") ?? "").trim();
    return subDirectoriesData.find((sd: { id: string; name: string }) => sd.id.trim() === subDirParam) || null;
  }, [searchParams, subDirectoriesData]);

  const [file, setFile] = useState<File | null>(null);
  const [summarizedText, setSummarizedText] = useState<string>("");
  const [transcribedText, setTranscribedText] = useState<string>("");
  const [isUploadingModalOpen, setIsUploadingModalOpen] = useState<boolean>(false);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = useState<boolean>(false);
  const [, setSearchValue] = useAtom<string>(searchValueAtom);

  const updateQueryParams = (updates: Record<string, string | null>) => {
    setSearchParams(prevParams => {
      const newParams = new URLSearchParams(prevParams);
      Object.entries(updates).forEach(([key, value]) => {
        if (value) {
          newParams.set(key, value);
        } else {
          newParams.delete(key);
        }
      });
      return newParams;
    }, { replace: true });
  };

  useEffect(() => {
  const navEntries = performance.getEntriesByType("navigation");
  if (navEntries.length > 0 && navEntries[0].type === "reload") {
    updateQueryParams({ site: null, directory: null, subdirectory: null });
  }
}, []);


  const handleSiteChange = (site: { id: string; name: string } | null) => {
    updateQueryParams({ site: site?.id ?? "", directory: "", subdirectory: "" });
  };

  const handleDirectoryChange = (directory: { id: string; name: string } | null) => {
    updateQueryParams({ directory: directory?.id ?? "", subdirectory: "" });
  };

  const handleSubDirectoryChange = (subDirectory: { id: string; name: string } | null) => {
    updateQueryParams({ subdirectory: subDirectory?.id ?? "" });
  };

  const handleFileChange = (file: File | null) => setFile(file);

  const handleUpload = async () => {
    if (!file) {
      alert("ファイルを選択してください");
      return;
    }
    setIsUploadingModalOpen(true);
    try {
      const transcription = await handleSendAudio(selectedSite, selectedDirectory, selectedSubDirectory, file);
      setTranscribedText(transcription.transcribed_text);
      setSummarizedText(transcription.summarized_text);
      setIsSuccessModalOpen(true);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("ファイルのアップロード中にエラーが発生しました");
    } finally {
      setIsUploadingModalOpen(false);
      setSearchValue("");
      updateQueryParams({ site: null, directory: null, subdirectory: null });
      setFile(null);
    }
  };

  if (sitesError) return <p style={{ color: "red" }}>サイトデータの取得中にエラーが発生しました</p>;
  if (isSitesLoading) return <p>サイトを読み込んでいます...</p>;

  return (
    <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", width: "100%", padding: 3, gap: 2 }}>
      <CssBaseline />
      {selectedDirectory && (
        <Box>
          <LinkCopyButton />
        </Box>
      )}
      <Box sx={{ display: "flex", justifyContent: "space-around", alignItems: "center", width: "100%" }}>
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
          selectedSiteId={selectedSite?.id || ""}
          selectedDirectoryId={selectedDirectory?.id || ""}
          selectedSubDirectoryId={selectedSubDirectory?.id || ""}
        />
        <Note transcribedText={transcribedText} summarizedText={summarizedText} />
      </Box>
      <UploadingModal open={isUploadingModalOpen} />
      <SuccessModal open={isSuccessModalOpen} onClose={() => setIsSuccessModalOpen(false)} />
    </Box>
  );
};

export default Main;
