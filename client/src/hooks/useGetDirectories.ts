import useSWR from "swr";

import { fetcher } from "@/utils/fetcher";

export const useGetDirectories = (apiUrl: string, siteId: string | null) => {
  const { data, error } = useSWR(
    siteId
      ? `${apiUrl}/directories?site_id=${encodeURIComponent(siteId)}`
      : null,
    fetcher,
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );
  return { directoriesData: data?.value || [], directoriesError: error };
};
