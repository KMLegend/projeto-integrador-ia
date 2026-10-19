import React from 'react';
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

  it('ignora frames sentinela com geracao negativa ou fitness zero (D-09 / FIX 3)', () => {
    const fakeChannel = new FakeProgressChannel();
    const taskId = 'task-sentinel-123';

    const { result } = renderHook(() => useProgressSocket(taskId, fakeChannel));

    act(() => {
      fakeChannel.emitProgress(taskId, {
        generation: 0,
        max_fitness: 803.22,
        status: 'evolving',
      });
      // Sentinel frame: generation -1 and max_fitness 0.0
      fakeChannel.emitProgress(taskId, {
        generation: -1,
        max_fitness: 0.0,
        status: 'completed',
      });
    });

    expect(result.current.status).toBe('completed');
    expect(result.current.points).toHaveLength(1);
    expect(result.current.points[0]).toEqual({ generation: 0, max_fitness: 803.22 });
    expect(result.current.currentGeneration).toBe(0);
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

describe('useProgressSocket sob React.StrictMode', () => {
  it('acumula pontos mesmo com o updater invocado duas vezes', () => {
    const fakeChannel = new FakeProgressChannel();
    const taskId = 'task-strictmode';

    // StrictMode invoca os updaters de estado duas vezes em desenvolvimento.
    // Antes da correcao, o efeito colateral dentro do updater fazia a segunda
    // invocacao descartar todo ponto novo e o grafico ficava permanentemente vazio.
    const { result } = renderHook(() => useProgressSocket(taskId, fakeChannel), {
      wrapper: ({ children }) => <React.StrictMode>{children}</React.StrictMode>,
    });

    act(() => {
      fakeChannel.emitProgress(taskId, { generation: 0, max_fitness: 803.22, status: 'evolving' });
      fakeChannel.emitProgress(taskId, { generation: 10, max_fitness: 816.92, status: 'evolving' });
    });

    expect(result.current.points).toEqual([
      { generation: 0, max_fitness: 803.22 },
      { generation: 10, max_fitness: 816.92 },
    ]);
  });

  it('atualiza no lugar quando a mesma geracao chega de novo', () => {
    const fakeChannel = new FakeProgressChannel();
    const taskId = 'task-dedupe';

    const { result } = renderHook(() => useProgressSocket(taskId, fakeChannel), {
      wrapper: ({ children }) => <React.StrictMode>{children}</React.StrictMode>,
    });

    act(() => {
      fakeChannel.emitProgress(taskId, { generation: 99, max_fitness: 800.0, status: 'evolving' });
      fakeChannel.emitProgress(taskId, { generation: 99, max_fitness: 816.92, status: 'completed' });
    });

    expect(result.current.points).toEqual([{ generation: 99, max_fitness: 816.92 }]);
    expect(result.current.status).toBe('completed');
  });
});
