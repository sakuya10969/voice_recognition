import React, { useState, useEffect } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import Send from "@mui/icons-material/Send";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import TextField from "@mui/material/TextField";
import { ThemeProvider } from "@mui/material/styles";
import { useDropzone, FileRejection } from "react-dropzone";
import { useForm, FieldError } from "react-hook-form";

import { theme } from "../theme/theme";

interface FileUploadProps {
  sites: { id: string; name: string }[];
  directories: { id: string, name: string }[];
  subDirectories: { id: string, name: string }[];
  onFileChange: (file: File | null) => void;
  onSubmit: () => void;
  onSiteChange: (site: { id: string; name: string }) => void;
  onDirectoryChange: (directory: { id: string; name: string }) => void;
  onSubDirectoryChange: (subDirectory: { id: string, name: string }) => void;
  file: File | null;
}

const FileUpload: React.FC<FileUploadProps> = ({
  sites, // プロジェクト一覧
  directories, // ディレクトリ一覧
  subDirectories, // サブディレクトリ一覧
  onFileChange, // ファイル選択処理
  onSubmit, // アップロード処理
  onSiteChange, // サイト選択処理
  onDirectoryChange, // ディレクトリ選択処理
  onSubDirectoryChange,
  file, // 選択されたファイル
}) => {
  const [errorFileType, setErrorFileType] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredSites, setFilteredSites] = useState(sites);
  const [selectedSite, setSelectedSite] = useState<string>("");
  const [selectedDirectory, setSelectedDirectory] = useState<string>("");
  const [selectedSubDirectory, setSelectedSubDirectory] = useState<string>("");

  // ページの初期レンダリング時にデータを取得、格納する
  useEffect(() => {
    setFilteredSites(sites);
  }, [sites]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    setFilteredSites(
        value.trim() === "" ? sites : sites.filter((site) => site.name && site.name.includes(value))
      );
  };

  const { register, handleSubmit, formState: { errors, isValid } } = useForm({
    mode: "onBlur"
  });

  const onDrop = (acceptedFiles: File[], fileRejections: FileRejection[]) => {
    if (fileRejections.length > 0) {
      setErrorFileType(true);
      return;
    }
    setErrorFileType(false);
    if (acceptedFiles.length > 0) {
      onFileChange(acceptedFiles[0]);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: {
      "video/mp4": [],
      "audio/wav": [],
    },
  });

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(onSubmit)}
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        borderRadius: "5px",
        p: 5,
        width: "500px",
      }}
    >
      <ThemeProvider theme={theme}>
        <TextField
        label="検索"
        placeholder="サイトの検索"
        variant="outlined"
        size="small"
        fullWidth
        value={searchTerm}
        onChange={handleSearch}
        sx={{
          mb: 3,
        }}
      />
      </ThemeProvider>

      <FormControl fullWidth sx={{ mb: 3 }} size="small" error={!!errors.site}>
        <InputLabel id="site-select-label">サイト</InputLabel>
        <ThemeProvider theme={theme}>
          <Select
            labelId="site-select-label"
            label="サイト"
            value={selectedSite}
            {...register("site", { required: "サイトを選択してください" })}
            MenuProps={{
              PaperProps: {
                style: {
                  width: 400,
                  maxHeight: 450,
                  overflowX: "auto"
                },
              },
            }}
          >
            {filteredSites.map((site: { id: string; name: string; }) => (
              <MenuItem
                key={site.id}
                value={site.id || ""}
                onClick={() => {
                setSelectedSite(site.id || "");
                onSiteChange(site);
              }}>
                {site.name}
              </MenuItem>
            ))}
          </Select>
        </ThemeProvider>
        {errors.site?.message && (
          <Typography variant="body2" color="error">
            {(errors.site as FieldError | undefined)?.message ?? ""}
          </Typography>
        )}
      </FormControl>
      <FormControl fullWidth sx={{ mb: 3 }} size="small" error={!!errors.directory}>
        <InputLabel id="directory-select-label">ディレクトリ</InputLabel>
        <ThemeProvider theme={theme}>
          <Select
          labelId="directory-select-label"
          label="ディレクトリ"
          value={selectedDirectory}
          {...register("directory", { required: "ディレクトリを選択してください" })}
          MenuProps={{
            PaperProps: {
              style: {
                width: 400,
                maxHeight: 450,
                overflowX: "auto",
              },
            },
          }}
          >
            {directories.map((directory: { id: string; name: string }) => (
              <MenuItem
                key={directory.id}
                value={directory.id || ""}
                onClick={() => {
                  setSelectedDirectory(directory.id || "");
                  onDirectoryChange(directory);
                }}>
                {directory.name}
              </MenuItem>
            ))}
          </Select>
        </ThemeProvider>
        {errors.directory?.message && (
          <Typography variant="body2" color="error">
            {(errors.directory as FieldError | undefined)?.message ?? ""}
          </Typography>
        )}
      </FormControl>
      <FormControl fullWidth sx={{ mb: 3 }} size="small">
        <InputLabel id="directory-select-label">サブディレクトリ</InputLabel>
        <ThemeProvider theme={theme}>
          <Select
          labelId="directory-select-label"
          label="サブディレクトリ"
          value={selectedSubDirectory}
          {...register("subDirectory")}
          MenuProps={{
            PaperProps: {
              style: {
                width: 400,
                maxHeight: 450,
                overflowX: "auto",
              },
            },
          }}
          >
            {subDirectories.map((subDirectory: { id: string; name: string }) => (
              <MenuItem
                key={subDirectory.id}
                value={subDirectory.id || ""}
                onClick={() => {
                  setSelectedSubDirectory(subDirectory.id)
                  onSubDirectoryChange(subDirectory);
                }}>
                {subDirectory.name}
              </MenuItem>
            ))}
          </Select>
        </ThemeProvider>
      </FormControl>

      <Box
        {...getRootProps()}
        sx={{
          border: "1px dashed black",
          borderRadius: "5px",
          p: 3,
          mb: 3,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          width: "430px",
          height: "250px",
          backgroundColor: isDragActive ? "gainsboro" : "transparent",
          "&:hover": {
            backgroundColor: "whitesmoke",
          },
        }}
      >
        <input
          {...getInputProps()}
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              onFileChange(e.target.files[0]);
            }
          }}
        />
        <label htmlFor="file-input">
          <Button
            variant="contained"
            component="span"
            startIcon={<CloudUploadIcon />}
            sx={{
              mb: 2,
              backgroundColor: "black",
              width: "170px",
              "&:hover": {
                backgroundColor: "black"
              }
            }}
          >
            ファイルの選択
          </Button>
        </label>

        {file && (
          <Typography variant="body1" sx={{ mb: 2, textAlign: "center" }}>
            選択されたファイル: {file.name}
          </Typography>
        )}
        {errorFileType && (
          <Typography variant="body1" color="error" sx={{ mb: 2, textAlign: "center" }}>
            mp4またはwav形式のファイルをアップロードしてください。
          </Typography>
        )}
      </Box>
      <Button
        type="submit"
        disabled={!file || !isValid}
        endIcon={<Send />}
        sx={{
          color: "white",
          backgroundColor: "black",
          borderRadius: "5px",
          width: "110px",
          ":disabled": {
            backgroundColor: "whitesmoke"
          },
          "&:hover": {
                backgroundColor: "black"
              }
        }}
      >
        送信
      </Button>
    </Box>
  );
};

export default FileUpload;
