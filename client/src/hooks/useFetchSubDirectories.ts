import useSWR from "swr";
import { fetcher } from "../utils/fetcher";
import { apiUrl } from "../constants/api";

export const useFetchSubDirectories = (
  siteId: string | null,
  directoryId: string | null
) => {
  const { data, error } = useSWR(
    siteId && directoryId
      ? `${apiUrl}/subdirectories?site_id=${encodeURIComponent(
          siteId
        )}&directory_id=${encodeURIComponent(directoryId)}`
      : null,
    fetcher,
    {
      revalidateOnFocus: false,
      dedupingInterval: 30000,
    }
  );
  return { subDirectoriesData: data?.value || [], subDirectoriesError: error };
};
