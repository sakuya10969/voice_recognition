import { Box } from "@mui/material";
import { useState, useEffect } from "react";
import FileUpload from "./FileUpload";
import Note from "./Note";
import { handleSendAudio, fetchSites, fetchDirectories } from "../api/Api";

const Main = () => {
  const [sites, setSites] = useState([]); // サイト一覧
  const [directories, setDirectories] = useState([]); // ディレクトリ一覧
  const [project, setProject] = useState(""); // 選択されたプロジェクト名
  const [projectDirectory, setProjectDirectory] = useState(""); // 選択されたディレクトリ名
  const [file, setFile] = useState(null); // アップロードするファイル
  const [content, setContent] = useState(""); // アップロード結果
  const [isUploading, setIsUploading] = useState(false); // アップロード中フラグ

  // ページロード時にサイト一覧を取得
  useEffect(() => {
    const loadSites = async () => {
      try {
        const data = await fetchSites(); // サイト一覧を取得
        setSites(data.value || []); // サイト一覧を保存
      } catch (e) {
        console.error("Error fetching sites:", e);
      }
    };
    loadSites();
  }, []);

  // サイト選択時にディレクトリ一覧を取得
  const handleProjectChange = async (site) => {
    setProject(site); // 選択されたサイトを保存
    setProjectDirectory(""); // ディレクトリ選択をリセット
    setDirectories([]); // ディレクトリ一覧をリセット

    if (site) {
      try {
        const data = await fetchDirectories(site); // サーバーからディレクトリ取得
        console.log(data.value)
        setDirectories(data.value || []); // ディレクトリ一覧を保存
      } catch (error) {
        console.error("Error fetching directories:", error);
      }
    }
  };

  // ディレクトリ選択時
  const handleProjectDirectoryChange = (directory) => {
    setProjectDirectory(directory); // 選択されたディレクトリ名を保存
  };

  // ファイル選択時
  const handleFileChange = (file) => {
    setFile(file);
  };

  // アップロード処理
  const handleUpload = async () => {
    if (!project || !projectDirectory) {
      alert("プロジェクトとディレクトリを選択してください");
      return;
    }
    if (!file) {
      alert("ファイルを選択してください");
      return;
    }

    setIsUploading(true);
    try {
      const transcription = await handleSendAudio(project, projectDirectory, file);
      setContent(transcription); // アップロード結果を保存
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("ファイルのアップロード中にエラーが発生しました。");
    } finally {
      setIsUploading(false);
      setFile(null); // ファイルをリセット
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "space-around",
        alignItems: "center",
        width: "100%",
        padding: 3, // 修正: "paddng" -> "padding"
      }}
    >
      <FileUpload
        sites={sites} // サイト一覧を渡す
        directories={directories} // ディレクトリ一覧を渡す
        onFileChange={handleFileChange} // ファイル選択処理
        onSubmit={handleUpload} // アップロード処理
        onProjectChange={handleProjectChange} // サイト選択処理
        onProjectDirectoryChange={handleProjectDirectoryChange} // ディレクトリ選択処理
        file={file} // 選択されたファイル
        isUploading={isUploading} // アップロード中状態
      />
      <Note content={content} />
    </Box>
  );
};

export default Main;
