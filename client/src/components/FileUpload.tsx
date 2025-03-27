import React, { useState, useEffect, useCallback } from "react";
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
import { useAtom } from "jotai";

import { theme } from "../theme/theme";
import { searchValueAtom } from "../store/atoms";

interface FileUploadProps {
  sites: { id: string; name: string }[];
  directories: { id: string; name: string }[];
  subDirectories: { id: string; name: string }[];
  onFileChange: (file: File | null) => void;
  onSubmit: () => void;
  onSiteChange: (site: { id: string; name: string }) => void;
  onDirectoryChange: (directory: { id: string; name: string }) => void;
  onSubDirectoryChange: (subDirectory: { id: string; name: string }) => void;
  file: File | null;
  selectedSiteId: string;
  selectedDirectoryId: string;
  selectedSubDirectoryId: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  sites,
  directories,
  subDirectories,
  onFileChange,
  onSubmit,
  onSiteChange,
  onDirectoryChange,
  onSubDirectoryChange,
  file,
  selectedSiteId,
  selectedDirectoryId,
  selectedSubDirectoryId,
}) => {
  const [errorFileType, setErrorFileType] = useState<boolean>(false);
  const [filteredSites, setFilteredSites] = useState(sites);
  const [searchValue, setSearchValue] = useAtom<string>(searchValueAtom);

  useEffect(() => {
    setFilteredSites(sites);
  }, [sites]);

  const handleSearch = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchValue(value);
    setFilteredSites(
      value.trim() === ""
        ? sites
        : sites.filter((site) => (site.name || "").includes(value))
    );
  }, [sites, setSearchValue]);

  const onDrop = useCallback((acceptedFiles: File[], fileRejections: FileRejection[]) => {
    if (fileRejections.length > 0) {
      setErrorFileType(true);
      return;
    }
    setErrorFileType(false);
    if (acceptedFiles.length > 0) {
      onFileChange(acceptedFiles[0]);
    }
  }, [onFileChange]);

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
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        borderRadius: "5px",
        p: 5,
        width: "500px",
      }}
    >
      <Typography fontWeight="bold" align="left" sx={{ fontSize: "x-large", mb: 2 }}>
        議事録ファイル出力先
      </Typography>
      <ThemeProvider theme={theme}>
        <TextField
          label="SPOサイトキーワード"
          variant="outlined"
          size="small"
          fullWidth
          value={searchValue}
          onChange={handleSearch}
          sx={{
            mb: 2,
            "& input": {
              backgroundColor: "white",
            },
          }}
        />
      </ThemeProvider>

      <FormControl fullWidth sx={{ mb: 2 }} size="small">
        <InputLabel id="site-select-label">SPOサイト</InputLabel>
        <ThemeProvider theme={theme}>
          <Select
            labelId="site-select-label"
            label="SPOサイト"
            value={selectedSiteId}
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
            {filteredSites.map((site) => (
              <MenuItem
                key={site.id}
                value={site.id}
                onClick={() => onSiteChange(site)}
              >
                {site.name}
              </MenuItem>
            ))}
          </Select>
        </ThemeProvider>
      </FormControl>

      <FormControl fullWidth sx={{ mb: 2 }} size="small">
        <InputLabel id="directory-select-label">ディレクトリ</InputLabel>
        <ThemeProvider theme={theme}>
          <Select
            labelId="directory-select-label"
            label="ディレクトリ"
            value={selectedDirectoryId}
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
            {directories.map((directory) => (
              <MenuItem
                key={directory.id}
                value={directory.id}
                onClick={() => onDirectoryChange(directory)}
              >
                {directory.name}
              </MenuItem>
            ))}
          </Select>
        </ThemeProvider>
      </FormControl>

      <FormControl fullWidth sx={{ mb: 2 }} size="small">
        <InputLabel id="subdirectory-select-label">サブディレクトリ</InputLabel>
        <ThemeProvider theme={theme}>
          <Select
            labelId="subdirectory-select-label"
            label="サブディレクトリ"
            value={selectedSubDirectoryId}
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
            {subDirectories.map((subDirectory) => (
              <MenuItem
                key={subDirectory.id}
                value={subDirectory.id}
                onClick={() => onSubDirectoryChange(subDirectory)}
              >
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
          mb: 2,
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
                backgroundColor: "black",
              },
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
        disabled={!file}
        endIcon={<Send />}
        sx={{
          color: "white",
          backgroundColor: "black",
          borderRadius: "5px",
          width: "110px",
          ":disabled": {
            backgroundColor: "whitesmoke",
          },
          "&:hover": {
            backgroundColor: "black",
          },
        }}
      >
        送信
      </Button>
    </Box>
  );
};

export default FileUpload;
