import { describe, it, expect, vi, beforeEach } from 'vitest';
import { FetchOptimizationApi } from '../httpClient';
import { OptimizationRequest } from '../contracts';

describe('FetchOptimizationApi', () => {
  const baseUrl = 'http://api.test';
  let api: FetchOptimizationApi;

  beforeEach(() => {
    api = new FetchOptimizationApi(baseUrl);
    vi.restoreAllMocks();
  });

  it('inicia otimizacao via POST /api/v1/optimize com corpo serializado', async () => {
    const request: OptimizationRequest = {
      budget_limit: 1000.0,
      dataset_reference: 'default',
      ga_parameters: {
        population_size: 60,
        generations: 100,
        mutation_rate: 0.2,
      },
    };

    const mockResponse = {
      task_id: 'task-abc-123',
      status: 'PROCESSING',
      message: 'Tarefa enfileirada',
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await api.start(request);

    expect(global.fetch).toHaveBeenCalledWith('http://api.test/api/v1/optimize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    expect(result).toEqual(mockResponse);
  });

  it('lanca erro amigavel quando POST retorna status de erro', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 422,
      json: async () => ({
        error: { code: 'INVALID_BUDGET', message: 'Orçamento deve ser positivo' },
      }),
    });

    await expect(
      api.start({
        budget_limit: -50,
        dataset_reference: 'default',
        ga_parameters: { population_size: 60, generations: 100 },
      })
    ).rejects.toThrow('Orçamento deve ser positivo');
  });

  it('consulta status da tarefa via GET /api/v1/status/{taskId}', async () => {
    const mockStatus = {
      task_id: 'task-abc-123',
      status: 'COMPLETED',
      result: null,
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockStatus,
    });

    const result = await api.status('task-abc-123');

    expect(global.fetch).toHaveBeenCalledWith('http://api.test/api/v1/status/task-abc-123', {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });
    expect(result).toEqual(mockStatus);
  });
});
