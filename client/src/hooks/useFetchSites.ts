import useSWR from "swr";
import { fetcher } from "@/utils/fetcher";

const apiUrl = process.env.REACT_APP_API_URL;

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
