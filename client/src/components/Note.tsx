import React from "react";
import { Paper, Box, Typography, IconButton } from "@mui/material";
import { Download as DownloadIcon } from "@mui/icons-material";
import { saveAs } from "file-saver";
import { Document, Packer, Paragraph, TextRun } from "docx";

interface NoteProps {
  summarizedText: string;
  transcribedText: string;
}

const Note: React.FC<NoteProps> = ({ summarizedText, transcribedText }) => {
  const handleDownload = async () => {
  const now = new Date();
  const formattedDate = now.toISOString().replace(/T/, "_").replace(/\..+/, "").replace(/:/g, "-"); 
  const fileName = `議事録_${formattedDate}.docx`;

    const createParagraphs = (text: string, title: string) => [
      new Paragraph({
        children: [new TextRun({ text: title, bold: true, size: 32 })],
        spacing: { after: 200 },
      }),
      ...text.split("\n").map(
        (line) =>
          new Paragraph({
            children: [new TextRun({ text: line, size: 24 })],
            spacing: { after: 100 },
          })
      ),
    ];

    const docContent = [
      ...createParagraphs(summarizedText, "[要約]"),
      new Paragraph({ spacing: { after: 200 } }),
      ...createParagraphs(transcribedText, "[文字起こし]"),
    ];

    const doc = new Document({
      sections: [
        {
          properties: {},
          children: docContent,
        },
      ],
    });

    const blob = await Packer.toBlob(doc);
    saveAs(blob, fileName);
  };

  return (
    <Paper
      elevation={3}
      sx={{
        width: "600px",
        height: "600px",
        padding: 2,
        border: "1px solid black",
      }}
    >
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          borderBottom: "1px solid black",
          pb: 1,
        }}
      >
        <Typography variant="h6" sx={{ fontWeight: "bold", textAlign: "center" }}>
          議事録
        </Typography>
        <IconButton
          sx={{
            transform: "translateX(50px)",
            ":disabled": {
              opacity: 0.5,
            },
          }}
          onClick={handleDownload}
          disabled={!summarizedText.trim() && !transcribedText.trim()}
        >
          <DownloadIcon sx={{ color: "black" }} />
        </IconButton>
      </Box>
      <Box
        sx={{
          overflowY: "auto",
          mt: 1,
          height: "90%",
        }}
      >
        {summarizedText && (
          <>
            <Typography variant="body1" sx={{ whiteSpace: "pre-wrap", fontWeight: "bold" }}>
              [要約結果]
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: "pre-wrap", mb: 2 }}>
              {summarizedText}
            </Typography>
          </>
        )}

        {transcribedText && (
          <>
            <Typography variant="body1" sx={{ whiteSpace: "pre-wrap", fontWeight: "bold" }}>
              [文字起こし結果]
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
              {transcribedText}
            </Typography>
          </>
        )}
      </Box>
    </Paper>
  );
};

export default Note;
