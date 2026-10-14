import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useProgressSocket } from '../useProgressSocket';
import { FakeProgressChannel } from '../../../shared/api/doubles/fakeProgressChannel';

describe('useProgressSocket', () => {
  it('acumula pontos de convergencia emitidos pelo canal sem duplicar', () => {
    const fakeChannel = new FakeProgressChannel();
    const taskId = 'task-evolve-123';

    const { result } = renderHook(() => useProgressSocket(taskId, fakeChannel));

    expect(result.current.isConnected).toBe(true);
    expect(result.current.points).toHaveLength(0);

    act(() => {
      fakeChannel.emitProgress(taskId, {
        generation: 0,
        max_fitness: 777.67,
        status: 'evolving',
      });
    });

    expect(result.current.points).toEqual([
      { generation: 0, max_fitness: 777.67 },
    ]);
    expect(result.current.currentGeneration).toBe(0);

    act(() => {
      fakeChannel.emitProgress(taskId, {
        generation: 10,
        max_fitness: 816.92,
        status: 'evolving',
      });
    });

    expect(result.current.points).toHaveLength(2);
    expect(result.current.currentGeneration).toBe(10);

    act(() => {
      fakeChannel.emitProgress(taskId, {
        generation: 100,
        max_fitness: 816.92,
        status: 'completed',
      });
    });

    expect(result.current.points).toHaveLength(3);
    expect(result.current.status).toBe('completed');
  });

  it('sinaliza falha sem quebrar quando socket dispara erro', () => {
    const fakeChannel = new FakeProgressChannel();
    const taskId = 'task-err-123';

    const { result } = renderHook(() => useProgressSocket(taskId, fakeChannel));

    act(() => {
      fakeChannel.emitError(taskId, new Event('error'));
    });

    expect(result.current.isSocketFailed).toBe(true);
    expect(result.current.isConnected).toBe(false);
  });
});
