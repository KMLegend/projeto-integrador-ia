import { ProgressMessage } from './contracts';

export interface ProgressChannel {
  subscribe(
    taskId: string,
    onMessage: (message: ProgressMessage) => void,
    onError?: (event: Event) => void
  ): () => void;
}

export class NativeProgressChannel implements ProgressChannel {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  subscribe(
    taskId: string,
    onMessage: (message: ProgressMessage) => void,
    onError?: (event: Event) => void
  ): () => void;
  subscribe(
    taskId: string,
    onMessage: (message: ProgressMessage) => void,
    onError?: (event: Event) => void
  ): () => void {
    const wsUrl = `${this.baseUrl}/ws/v1/progress/${taskId}`;
    let socket: WebSocket | null = null;
    let isTerminated = false;
    let reconnectTimeoutId: ReturnType<typeof setTimeout> | null = null;
    let retryCount = 0;
    const maxRetries = 3;

    const connect = () => {
      if (isTerminated) return;

      try {
        socket = new WebSocket(wsUrl);

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data) as ProgressMessage;
            onMessage(data);
            if (data.status === 'completed' || data.status === 'failed') {
              isTerminated = true;
              socket?.close();
            }
          } catch (e) {
            console.error('Falha ao decodificar mensagem do WebSocket:', e);
          }
        };

        socket.onerror = (event) => {
          if (onError) onError(event);
        };

        socket.onclose = (event) => {
          // 1000 is normal closure; 4404 is task not found
          if (!isTerminated && event.code !== 1000 && event.code !== 4404 && retryCount < maxRetries) {
            retryCount += 1;
            reconnectTimeoutId = setTimeout(connect, 1000 * retryCount);
          }
        };
      } catch (err) {
        if (onError && err instanceof Event) onError(err);
      }
    };

    connect();

    return () => {
      isTerminated = true;
      if (reconnectTimeoutId) {
        clearTimeout(reconnectTimeoutId);
      }
      if (socket) {
        socket.close();
      }
    };
  }
}

export function createProgressChannel(baseUrl: string): ProgressChannel {
  return new NativeProgressChannel(baseUrl);
}

const defaultWsBaseUrl =
  typeof import.meta !== 'undefined' && import.meta.env?.VITE_WS_BASE_URL
    ? import.meta.env.VITE_WS_BASE_URL
    : 'ws://localhost:8000';

export const defaultProgressChannel = createProgressChannel(defaultWsBaseUrl);
