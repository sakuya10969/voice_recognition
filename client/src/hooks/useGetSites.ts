import useSWR from "swr";
import { fetcher } from "@/utils/fetcher";

export const useGetSites = (apiUrl: string) => {
  const { data, isLoading, error } = useSWR(`${apiUrl}/sites`, fetcher, {
    revalidateOnFocus: false,
    dedupingInterval: 60000,
  });
  return {
    sitesData: data?.value || [],
    sitesError: error,
    isSitesLoading: isLoading,
  };
};
