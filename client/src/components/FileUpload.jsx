import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import SendIcon from "@mui/icons-material/Send";
import CircularProgress from "@mui/material/CircularProgress";
import { useDropzone } from "react-dropzone";
import { useForm, Controller } from "react-hook-form";

const FileUpload = ({ onSubmit, isUploading }) => {
  const {
    control,
    handleSubmit,
    formState: { errors, isValid },
    setValue,
    watch,
  } = useForm({
    mode: "onBlur", // フォームの即時バリデーション
    defaultValues: {
      projectName: "",
      file: null,
    },
  });

  const projectName = watch("projectName"); // プロジェクト名の監視
  const file = watch("file"); // ファイルの監視

  const onDrop = (acceptedFiles, fileRejections) => {
    if (fileRejections.length > 0) {
      alert("mp4またはwav形式のファイルをアップロードしてください。");
      return;
    }
    if (acceptedFiles.length > 0) {
      setValue("file", acceptedFiles[0], { shouldValidate: true }); // ファイルをセットしてバリデーション実行
    }
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    multiple: false,
    accept: {
      "video/mp4": [],
      "audio/wav": [],
    },
  });

  const handleFormSubmit = (data) => {
    onSubmit(data); // file含む全データを送信
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(handleFormSubmit)}
      sx={{
        border: "1px solid black",
        borderRadius: "5px",
        p: 3,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        width: "450px",
        height: "500px",
      }}
    >
      {/* プロジェクト名入力フィールド */}
      <Controller
        name="projectName"
        control={control}
        rules={{ required: "プロジェクト名を入力してください。" }}
        render={({ field }) => (
          <TextField
            {...field}
            label="プロジェクト名"
            variant="outlined"
            error={!!errors.projectName}
            helperText={errors.projectName ? errors.projectName.message : ""}
            sx={{ mb: 3, width: "80%" }}
          />
        )}
      />

      {/* ドラッグ＆ドロップエリア */}
      <Box
        {...getRootProps()}
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          border: "1px dashed black",
          borderRadius: "10px",
          p: 2,
          width: "80%",
          height: "300px",
          textAlign: "center",
          "&:hover": {
            backgroundColor: "whitesmoke",
          },
          mb: 3,
        }}
      >
        <input {...getInputProps()} />
        {!file && (
          <Button
            variant="contained"
            component="span"
            startIcon={<CloudUploadIcon />}
            sx={{ mb: 2, backgroundColor: "black" }}
          >
            ファイルの選択
          </Button>
        )}
        {file && (
          <Typography
            variant="body1"
            sx={{ mt: 2, wordBreak: "break-word" }}
          >
            選択されたファイル: {file.name}
          </Typography>
        )}
      </Box>

      {isUploading ? (
        <>
          <Typography variant="body1" sx={{ mb: 2, textAlign: "center" }}>
            処理中...
          </Typography>
          <CircularProgress />
        </>
      ) : (
        <Button
          type="submit"
          variant="contained"
          endIcon={<SendIcon />}
          sx={{
            backgroundColor: "black",
            width: "100px",
            ":disabled": {
              opacity: 0.5,
            },
          }}
          disabled={!isValid} // バリデーションとファイル選択の両方を確認
        >
          送信
        </Button>
      )}
    </Box>
  );
};

export default FileUpload;
