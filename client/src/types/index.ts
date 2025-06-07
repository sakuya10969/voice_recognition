export interface FileDropZoneProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  errorFileType: boolean;
}

export interface FileUploadProps {
  sites: SPOData[];
  directories: SPOData[];
  subDirectories: SPOData[];
  onFileChange: (file: File | null) => void;
  onSubmit: () => void;
  onSiteChange: (site: SPOData) => void;
  onDirectoryChange: (directory: SPOData) => void;
  onSubDirectoryChange: (subDirectory: SPOData) => void;
  file: File | null;
  selectedSiteId: string;
  selectedDirectoryId: string;
  selectedSubDirectoryId: string;
}

export interface NoteProps {
  summarizedText: string;
  transcribedText: string;
}

export interface SearchFieldProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export interface SPOSelectionProps {
  sites: SPOData[];
  directories: SPOData[];
  subDirectories: SPOData[];
  selectedSiteId: string;
  selectedDirectoryId: string;
  selectedSubDirectoryId: string;
  onSiteChange: (site: SPOData) => void;
  onDirectoryChange: (directory: SPOData) => void;
  onSubDirectoryChange: (subDirectory: SPOData) => void;
}

export interface SuccessModalProps {
  open: boolean;
  onClose: () => void;
}

export interface TranscriptionParams {
  apiUrl: string;
  site: SPOData | null;
  directory: SPOData | null;
  subDirectory: SPOData | null;
  file: File;
}

export interface TranscriptionResponse {
  task_id: string;
  status: string;
  transcribed_text?: string;
  summarized_text?: string;
}

export interface TranscriptionResult {
  transcribed_text: string;
  summarized_text: string;
}

export interface SPOData {
  id: string;
  name: string;
}
