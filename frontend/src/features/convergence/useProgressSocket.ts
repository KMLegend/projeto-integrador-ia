import { useEffect, useState } from 'react';
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

  useEffect(() => {
    if (!taskId) {
      setPoints([]);
      setIsConnected(false);
      setIsSocketFailed(false);
      setStatus('idle');
      setCurrentGeneration(0);
      return;
    }

    setIsConnected(true);
    setIsSocketFailed(false);
    setStatus('evolving');
    setPoints([]);

    const unsubscribe = channel.subscribe(
      taskId,
      (msg: ProgressMessage) => {
        setIsConnected(true);
        setStatus(msg.status);

        if (msg.generation >= 0) {
          setCurrentGeneration(msg.generation);
        }

        // D-09: descarta frames sentinela para nao distorcer a escala do grafico.
        if (msg.generation >= 0 && msg.max_fitness > 0) {
          const point: ConvergencePoint = {
            generation: msg.generation,
            max_fitness: msg.max_fitness,
          };
          // O updater precisa ser PURO: o React 18 em StrictMode o invoca duas vezes,
          // e qualquer efeito colateral aqui (ex.: marcar a geracao num Set externo)
          // faz a segunda invocacao descartar o ponto. A deduplicacao olha o proprio
          // array acumulado, que e a unica fonte de verdade.
          setPoints((prev) => {
            const index = prev.findIndex((p) => p.generation === point.generation);
            if (index < 0) {
              return [...prev, point];
            }
            const next = [...prev];
            next[index] = point;
            return next;
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
