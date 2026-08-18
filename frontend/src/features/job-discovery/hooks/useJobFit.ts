import { useMutation } from '@tanstack/react-query';

import { jobDiscoveryApi } from '../services/jobDiscoveryApi';

export function useJobFit() {
  return useMutation({
    mutationFn: (jobId: string) => jobDiscoveryApi.checkFit(jobId),
  });
}
