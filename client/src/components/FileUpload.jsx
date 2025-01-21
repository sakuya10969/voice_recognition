import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import Send from "@mui/icons-material/Send";
import CircularProgress from "@mui/material/CircularProgress";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import Modal from "@mui/material/Modal";
import { useDropzone } from "react-dropzone";
import { useState } from "react";
import { useForm } from "react-hook-form";

const FileUpload = ({
  sites, // プロジェクト一覧
  directories, // ディレクトリ一覧
  onFileChange, // ファイル選択処理
  onSubmit, // アップロード処理
  onProjectChange, // サイト選択処理
  onProjectDirectoryChange, // ディレクトリ選択処理
  file, // 選択されたファイル
  isUploading, // アップロード中フラグ
}) => {
  const [errorFileType, setErrorFileType] = useState(false);
  const { register, handleSubmit, formState: { errors, isValid } } = useForm({
    mode: "onBlur"
  });

  const onDrop = (acceptedFiles, fileRejections) => {
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
        border: "1px solid black",
        borderRadius: "5px",
        p: 7,
        width: "400px",
        height: "550px",
      }}
    >
      {/* プロジェクト名セレクトボックス */}
      <FormControl fullWidth sx={{ mb: 3 }} size="small" error={!!errors.project}>
        <InputLabel id="project-select-label">プロジェクト</InputLabel>
        <Select
          labelId="project-select-label"
          label="プロジェクト"
          defaultValue=""
          {...register("project", { required: "プロジェクトを選択してください" })}
          MenuProps={{
            PaperProps: {
              style: {
                maxHeight: 500,
                width: 400,
                overflowX: "auto"
              },
            },
        }}
        >
          {sites.map((site) => (
            <MenuItem key={site.id} value={site} onClick={() => onProjectChange(site)}>
              {site.name}
            </MenuItem>
          ))}
        </Select>
        {errors.project && (
          <Typography variant="body2" color="error">
            {errors.project.message}
          </Typography>
        )}
      </FormControl>

      {/* ディレクトリ名セレクトボックス */}
      <FormControl fullWidth sx={{ mb: 3 }} size="small" error={!!errors.directory}>
        <InputLabel id="directory-select-label">ディレクトリ</InputLabel>
        <Select
          labelId="directory-select-label"
          label="ディレクトリ名"
          defaultValue=""
          onChange={(e) => onProjectDirectoryChange(e.target.value)}
          {...register("directory", { required: "ディレクトリを選択してください" })}
          MenuProps={{
            PaperProps: {
              style: {
                maxHeight: 500,
                width: 400,
                overflowX: "auto",
              },
            },
        }}
        >
          {directories.map((directory) => (
            <MenuItem key={directory.id} value={directory.name}>
              {directory.name}
            </MenuItem>
          ))}
        </Select>
        {errors.directory && (
          <Typography variant="body2" color="error">
            {errors.directory.message}
          </Typography>
        )}
      </FormControl>

      {/* ファイルアップロードエリア */}
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
          width: "80%",
          height: "350px",
          backgroundColor: isDragActive ? "gainsboro" : "transparent",
          "&:hover": {
            backgroundColor: "whitesmoke",
          },
        }}
      >
        <input
          {...getInputProps()}
          onChange={(e) => onFileChange(e.target.files[0])}
        />
        <label htmlFor="file-input">
          <Button
            variant="contained"
            component="span"
            startIcon={<CloudUploadIcon />}
            sx={{
              mb: 2,
              backgroundColor: "black",
              width: "160px",
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

      {/* アップロード処理 */}
      {isUploading ? (
        <Modal open={isUploading}>
          <Box
            sx={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%)",
              width: 300,
              bgcolor: "background.paper",
              boxShadow: 24,
              p: 4,
              borderRadius: "8px",
              textAlign: "center",
            }}
          >
            <Typography variant="h6" sx={{ mb: 2 }}>
              処理中...
            </Typography>
            <CircularProgress />
          </Box>
        </Modal>
      ) : (
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
              backgroundColor: "whitesmoke",
            },
          }}
        >
          送信
        </Button>
      )}
    </Box>
  );
};

export default FileUpload;
