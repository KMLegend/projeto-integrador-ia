import { useEffect, useState, useRef } from 'react';
import { ConvergencePoint, ProgressMessage } from '../../shared/api/contracts';
import {
  defaultProgressChannel,
  ProgressChannel,
} from '../../shared/api/websocketClient';

export interface UseProgressSocketReturn {
  points: ConvergencePoint[];
  isConnected: boolean;
  isSocketFailed: boolean;
  status: 'idle' | 'evolving' | 'completed' | 'failed';
  currentGeneration: number;
}

export function useProgressSocket(
  taskId: string | null,
  channel: ProgressChannel = defaultProgressChannel
): UseProgressSocketReturn {
  const [points, setPoints] = useState<ConvergencePoint[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isSocketFailed, setIsSocketFailed] = useState<boolean>(false);
  const [status, setStatus] = useState<'idle' | 'evolving' | 'completed' | 'failed'>('idle');
  const [currentGeneration, setCurrentGeneration] = useState<number>(0);

  // Keep track of observed generations to prevent duplicate points
  const observedGenerations = useRef<Set<number>>(new Set());

  useEffect(() => {
    if (!taskId) {
      setPoints([]);
      setIsConnected(false);
      setIsSocketFailed(false);
      setStatus('idle');
      setCurrentGeneration(0);
      observedGenerations.current.clear();
      return;
    }

    setIsConnected(true);
    setIsSocketFailed(false);
    setStatus('evolving');
    observedGenerations.current.clear();
    setPoints([]);

    const unsubscribe = channel.subscribe(
      taskId,
      (msg: ProgressMessage) => {
        setIsConnected(true);
        setStatus(msg.status);

        if (msg.generation >= 0) {
          setCurrentGeneration(msg.generation);
        }

        // D-09 / FIX 3: Ignore sentinel or non-positive fitness values from polluting chart points
        if (msg.generation >= 0 && msg.max_fitness > 0) {
          setPoints((prev) => {
            if (observedGenerations.current.has(msg.generation)) {
              return prev.map((p) =>
                p.generation === msg.generation
                  ? { generation: msg.generation, max_fitness: msg.max_fitness }
                  : p
              );
            }
            observedGenerations.current.add(msg.generation);
            return [
              ...prev,
              { generation: msg.generation, max_fitness: msg.max_fitness },
            ];
          });
        }
      },
      () => {
        setIsConnected(false);
        setIsSocketFailed(true);
      }
    );

    return () => {
      unsubscribe();
    };
  }, [taskId, channel]);

  return {
    points,
    isConnected,
    isSocketFailed,
    status,
    currentGeneration,
  };
}
