export interface FileDropZoneProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  errorFileType: boolean;
}

export interface Option {
  id: string;
  name: string;
}

export interface FileUploadProps {
  sites: Option[];
  directories: Option[];
  subDirectories: Option[];
  onFileChange: (file: File | null) => void;
  onSubmit: () => void;
  onSiteChange: (site: Option) => void;
  onDirectoryChange: (directory: Option) => void;
  onSubDirectoryChange: (subDirectory: Option) => void;
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
  sites: Option[];
  directories: Option[];
  subDirectories: Option[];
  selectedSiteId: string;
  selectedDirectoryId: string;
  selectedSubDirectoryId: string;
  onSiteChange: (site: Option) => void;
  onDirectoryChange: (directory: Option) => void;
  onSubDirectoryChange: (subDirectory: Option) => void;
}

export interface SuccessModalProps {
  open: boolean;
  onClose: () => void;
}

export interface TranscriptionParams {
  apiUrl: string;
  site: LocationData | null;
  directory: LocationData | null;
  subDirectory: LocationData | null;
  file: File;
};

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

export interface LocationData {
  id: string;
  name: string;
}
