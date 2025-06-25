import useSWR from 'swr';

import { fetcher } from '@/utils/fetcher';
import { apiUrl } from '@/constants';

export const useGetSites = () => {
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
