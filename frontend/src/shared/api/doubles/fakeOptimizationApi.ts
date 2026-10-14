import {
  OptimizationApi,
} from '../httpClient';
import {
  OptimizationRequest,
  OptimizationStatusResponse,
  StartOptimizationResponse,
} from '../contracts';

export class FakeOptimizationApi implements OptimizationApi {
  public recordedRequests: OptimizationRequest[] = [];
  public recordedStatusQueries: string[] = [];

  constructor(
    private nextStartResponse: StartOptimizationResponse = {
      task_id: 'test-task-123',
      status: 'PROCESSING',
      message: 'Tarefa de otimização enfileirada com sucesso',
    },
    private nextStatusResponse: OptimizationStatusResponse = {
      task_id: 'test-task-123',
      status: 'PROCESSING',
      result: null,
    }
  ) {}

  setNextStartResponse(response: StartOptimizationResponse): void {
    this.nextStartResponse = response;
  }

  setNextStatusResponse(response: OptimizationStatusResponse): void {
    this.nextStatusResponse = response;
  }

  async start(request: OptimizationRequest): Promise<StartOptimizationResponse> {
    this.recordedRequests.push(request);
    return this.nextStartResponse;
  }

  async status(taskId: string): Promise<OptimizationStatusResponse> {
    this.recordedStatusQueries.push(taskId);
    return this.nextStatusResponse;
  }
}
