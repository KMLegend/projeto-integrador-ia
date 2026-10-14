import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NativeProgressChannel } from '../websocketClient';
import { ProgressMessage } from '../contracts';

describe('NativeProgressChannel', () => {
  const baseUrl = 'ws://api.test';
  let channel: NativeProgressChannel;

  beforeEach(() => {
    channel = new NativeProgressChannel(baseUrl);
  });

  it('conecta ao endpoint correto e repassa mensagens parseadas', () => {
    const receivedMessages: ProgressMessage[] = [];

    // Mock WebSocket
    class MockWebSocket {
      public url: string;
      public onmessage: ((e: { data: string }) => void) | null = null;
      public onerror: ((e: Event) => void) | null = null;
      public onclose: ((e: { code: number }) => void) | null = null;
      public readyState = 1;

      constructor(url: string) {
        this.url = url;
      }

      close = vi.fn();
    }

    interface IMockWebSocket {
      url: string;
      onmessage: ((e: { data: string }) => void) | null;
      onerror: ((e: Event) => void) | null;
      onclose: ((e: { code: number }) => void) | null;
      readyState: number;
      close: () => void;
    }

    const originalWebSocket = global.WebSocket;
    let mockInstance: IMockWebSocket | null = null;
    // @ts-expect-error test mock
    global.WebSocket = class extends MockWebSocket {
      constructor(url: string) {
        super(url);
        mockInstance = this as unknown as IMockWebSocket;
      }
    };

    const unsubscribe = channel.subscribe('task-456', (msg) => {
      receivedMessages.push(msg);
    });

    const getMockInstance = (): IMockWebSocket => {
      if (!mockInstance) throw new Error('mockInstance is null');
      return mockInstance;
    };

    expect(getMockInstance().url).toBe('ws://api.test/ws/v1/progress/task-456');

    // Simulate receiving message
    getMockInstance().onmessage?.({
      data: JSON.stringify({
        generation: 10,
        max_fitness: 816.92,
        status: 'evolving',
      }),
    });

    expect(receivedMessages).toHaveLength(1);
    expect(receivedMessages[0]).toEqual({
      generation: 10,
      max_fitness: 816.92,
      status: 'evolving',
    });

    unsubscribe();
    expect(getMockInstance().close).toHaveBeenCalled();

    global.WebSocket = originalWebSocket;
  });
});
