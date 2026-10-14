import { useMutation, UseMutationResult } from '@tanstack/react-query';
import {
  OptimizationRequest,
  StartOptimizationResponse,
} from '../../shared/api/contracts';
import {
  defaultOptimizationApi,
  OptimizationApi,
} from '../../shared/api/httpClient';

export function useStartOptimization(
  api: OptimizationApi = defaultOptimizationApi
): UseMutationResult<StartOptimizationResponse, Error, OptimizationRequest> {
  return useMutation<StartOptimizationResponse, Error, OptimizationRequest>({
    mutationFn: (request: OptimizationRequest) => api.start(request),
  });
}
