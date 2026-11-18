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
    // staleTime so aceita numero nesta versao do TanStack (5.28.9); a forma de funcao
    // chegou na 5.42 e aqui era silenciosamente invalida. Infinity e o valor correto:
    // quem dispara as reconsultas enquanto processa e o refetchInterval acima, que nao
    // depende de staleness. Apos COMPLETED o resultado e imutavel e nao deve recarregar.
    staleTime: Infinity,
    retry: 2,
  });
}
