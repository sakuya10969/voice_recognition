import useSWR from "swr";
import { fetcher } from "@/utils/fetcher";

export const useFetchSites = (apiUrl: string) => {
  const { data, error, isLoading } = useSWR(`${apiUrl}/sites`, fetcher, {
    revalidateOnFocus: false,
    dedupingInterval: 60000,
  });
  return {
    sitesData: data?.value || [],
    sitesError: error,
    isSitesLoading: isLoading,
  };
};
