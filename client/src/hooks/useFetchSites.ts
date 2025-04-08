import useSWR from "swr";
import { fetcher } from "../utils/fetcher";
import { apiUrl } from "../constants/api";

export const useFetchSites = () => {
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
