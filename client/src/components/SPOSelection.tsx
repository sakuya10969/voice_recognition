import React from "react";
import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
} from "@mui/material";
import { ThemeProvider } from "@mui/material/styles";
import { theme } from "../theme/theme";

interface Option {
  id: string;
  name: string;
}

interface SPOSelectionProps {
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

const SPOSelection: React.FC<SPOSelectionProps> = ({
  sites,
  directories,
  subDirectories,
  selectedSiteId,
  selectedDirectoryId,
  selectedSubDirectoryId,
  onSiteChange,
  onDirectoryChange,
  onSubDirectoryChange,
}) => (
  <>
    <ThemeProvider theme={theme}>
      <FormControl fullWidth sx={{ mb: 2 }} size="small">
        <InputLabel id="site-select-label">SPOサイト</InputLabel>
        <Select
          labelId="site-select-label"
          value={selectedSiteId}
          label="SPOサイト"
          MenuProps={{
            PaperProps: {
              style: { width: 400, maxHeight: 450, overflowX: "auto" },
            },
          }}
        >
          {sites.map((site) => (
            <MenuItem key={site.id} value={site.id} onClick={() => onSiteChange(site)}>
              {site.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl fullWidth sx={{ mb: 2 }} size="small">
        <InputLabel id="directory-select-label">ディレクトリ</InputLabel>
        <Select
          labelId="directory-select-label"
          value={selectedDirectoryId}
          label="ディレクトリ"
          MenuProps={{
            PaperProps: {
              style: { width: 400, maxHeight: 450, overflowX: "auto" },
            },
          }}
        >
          {directories.map((directory) => (
            <MenuItem key={directory.id} value={directory.id} onClick={() => onDirectoryChange(directory)}>
              {directory.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl fullWidth sx={{ mb: 2 }} size="small">
        <InputLabel id="subdirectory-select-label">サブディレクトリ</InputLabel>
        <Select
          labelId="subdirectory-select-label"
          value={selectedSubDirectoryId}
          label="サブディレクトリ"
          MenuProps={{
            PaperProps: {
              style: { width: 400, maxHeight: 450, overflowX: "auto" },
            },
          }}
        >
          {subDirectories.map((subDirectory) => (
            <MenuItem key={subDirectory.id} value={subDirectory.id} onClick={() => onSubDirectoryChange(subDirectory)}>
              {subDirectory.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </ThemeProvider>
  </>
);

export default SPOSelection;
