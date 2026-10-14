import {
  OptimizationRequest,
  OptimizationStatusResponse,
  StartOptimizationResponse,
} from './contracts';

export interface OptimizationApi {
  start(request: OptimizationRequest): Promise<StartOptimizationResponse>;
  status(taskId: string): Promise<OptimizationStatusResponse>;
}

export class FetchOptimizationApi implements OptimizationApi {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  async start(request: OptimizationRequest): Promise<StartOptimizationResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/optimize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => null);
      const message =
        errorBody?.error?.message ||
        errorBody?.detail?.[0]?.msg ||
        errorBody?.detail ||
        `Erro ao iniciar otimização (HTTP ${response.status})`;
      throw new Error(message);
    }

    return (await response.json()) as StartOptimizationResponse;
  }

  async status(taskId: string): Promise<OptimizationStatusResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/status/${taskId}`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => null);
      const message =
        errorBody?.error?.message ||
        `Erro ao consultar status da tarefa ${taskId} (HTTP ${response.status})`;
      throw new Error(message);
    }

    return (await response.json()) as OptimizationStatusResponse;
  }
}

export function createOptimizationApi(baseUrl: string): OptimizationApi {
  return new FetchOptimizationApi(baseUrl);
}

const defaultApiBaseUrl =
  typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL
    ? import.meta.env.VITE_API_BASE_URL
    : 'http://localhost:8000';

export const defaultOptimizationApi = createOptimizationApi(defaultApiBaseUrl);
