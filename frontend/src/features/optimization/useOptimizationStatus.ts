import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { OptimizationStatusResponse } from '../../shared/api/contracts';
import {
  defaultOptimizationApi,
  OptimizationApi,
} from '../../shared/api/httpClient';

export function useOptimizationStatus(
  taskId: string | null,
  api: OptimizationApi = defaultOptimizationApi
): UseQueryResult<OptimizationStatusResponse> {
  return useQuery<OptimizationStatusResponse>({
    queryKey: ['optimization-status', taskId],
    queryFn: () => {
      if (!taskId) {
        throw new Error('Task ID é obrigatório para consulta de status.');
      }
      return api.status(taskId);
    },
    enabled: Boolean(taskId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === 'PROCESSING') {
        return 2000;
      }
      return false;
    },
    // Sem isto, o TanStack pausa o intervalo quando a aba fica oculta; como o
    // QueryClient desliga refetchOnWindowFocus, a tela nunca se recuperaria ao
    // voltar e ficaria presa em "processando" com a tarefa ja concluida.
    refetchIntervalInBackground: true,
    staleTime: (query) => {
      const status = query.state.data?.status;
      if (status === 'COMPLETED' || status === 'FAILED') {
        return Infinity;
      }
      return 0;
    },
    retry: 2,
  });
}
