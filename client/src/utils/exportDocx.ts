import { Document, Packer, Paragraph, TextRun } from 'docx';
import { saveAs } from 'file-saver';

// 議事録データを.docx形式で保存するユーティリティ
export const exportMeetingDocx = async (
  summarizedText: string,
  transcribedText: string
) => {
  const now = new Date();
  const formattedDate = now
    .toISOString()
    .replace(/T/, '_')
    .replace(/\..+/, '')
    .replace(/:/g, '-');
  const fileName = `議事録_${formattedDate}.docx`;

  const createParagraphs = (text: string, title: string): Paragraph[] => [
    new Paragraph({
      children: [new TextRun({ text: title, bold: true, size: 32 })],
      spacing: { after: 200 },
    }),
    ...text.split('\n').map(
      (line) =>
        new Paragraph({
          children: [new TextRun({ text: line, size: 24 })],
          spacing: { after: 100 },
        })
    ),
  ];

  const docContent = [
    ...createParagraphs(summarizedText, '[要約]'),
    new Paragraph({ spacing: { after: 200 } }),
    ...createParagraphs(transcribedText, '[文字起こし]'),
  ];

  const doc = new Document({
    sections: [{ properties: {}, children: docContent }],
  });

  const blob = await Packer.toBlob(doc);
  saveAs(blob, fileName);
};
