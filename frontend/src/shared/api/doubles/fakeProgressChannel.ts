import { ProgressChannel } from '../websocketClient';
import { ProgressMessage } from '../contracts';

export class FakeProgressChannel implements ProgressChannel {
  public subscribedTasks: string[] = [];
  public activeListeners: Map<string, Array<(message: ProgressMessage) => void>> = new Map();
  public errorListeners: Map<string, Array<(err: Event) => void>> = new Map();

  subscribe(
    taskId: string,
    onMessage: (message: ProgressMessage) => void,
    onError?: (err: Event) => void
  ): () => void {
    this.subscribedTasks.push(taskId);

    const listeners = this.activeListeners.get(taskId) || [];
    listeners.push(onMessage);
    this.activeListeners.set(taskId, listeners);

    if (onError) {
      const errListeners = this.errorListeners.get(taskId) || [];
      errListeners.push(onError);
      this.errorListeners.set(taskId, errListeners);
    }

    return () => {
      const current = this.activeListeners.get(taskId) || [];
      this.activeListeners.set(
        taskId,
        current.filter((l) => l !== onMessage)
      );
    };
  }

  emitProgress(taskId: string, message: ProgressMessage): void {
    const listeners = this.activeListeners.get(taskId) || [];
    listeners.forEach((listener) => listener(message));
  }

  emitError(taskId: string, event: Event): void {
    const listeners = this.errorListeners.get(taskId) || [];
    listeners.forEach((listener) => listener(event));
  }
}
