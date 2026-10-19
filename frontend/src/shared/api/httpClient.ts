import {
  OptimizationRequest,
  OptimizationStatusResponse,
  StartOptimizationResponse,
  DatasetListResponse,
  DatasetSummary,
} from './contracts';

export interface DatasetApi {
  list(): Promise<DatasetListResponse>;
  upload(file: File, reference?: string): Promise<DatasetSummary>;
}

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

export class FetchDatasetApi implements DatasetApi {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  async list(): Promise<DatasetListResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/datasets`, {
      headers: { Accept: 'application/json' },
    });
    if (!response.ok) {
      throw new Error(`Erro ao listar datasets (HTTP ${response.status})`);
    }
    return (await response.json()) as DatasetListResponse;
  }

  async upload(file: File, reference?: string): Promise<DatasetSummary> {
    const form = new FormData();
    form.append('file', file);
    if (reference) {
      form.append('reference', reference);
    }
    const response = await fetch(`${this.baseUrl}/api/v1/datasets`, {
      method: 'POST',
      body: form,
    });
    const body = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(
        body?.error?.message ?? `Falha ao enviar dataset (HTTP ${response.status})`
      );
    }
    return body as DatasetSummary;
  }
}

export function createDatasetApi(baseUrl: string): DatasetApi {
  return new FetchDatasetApi(baseUrl);
}

export function createOptimizationApi(baseUrl: string): OptimizationApi {
  return new FetchOptimizationApi(baseUrl);
}

const defaultApiBaseUrl =
  typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL
    ? import.meta.env.VITE_API_BASE_URL
    : 'http://localhost:8000';

export const defaultOptimizationApi = createOptimizationApi(defaultApiBaseUrl);
export const defaultDatasetApi = createDatasetApi(defaultApiBaseUrl);
