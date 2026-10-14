import React from 'react';
import { Loader2, CheckCircle2, AlertCircle, WifiOff } from 'lucide-react';

interface ProgressBannerProps {
  status: 'idle' | 'evolving' | 'completed' | 'failed';
  currentGeneration: number;
  totalGenerations?: number;
  isSocketFailed?: boolean;
}

export const ProgressBanner: React.FC<ProgressBannerProps> = ({
  status,
  currentGeneration,
  totalGenerations = 100,
  isSocketFailed = false,
}) => {
  if (status === 'idle') {
    return null;
  }

  const progressPercentage = Math.min(
    100,
    Math.round((currentGeneration / (totalGenerations || 100)) * 100)
  );

  return (
    <div className="bg-slate-800/90 border border-slate-700 rounded-xl p-4 shadow-lg mb-6 transition-all">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          {status === 'evolving' && (
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <Loader2 className="w-5 h-5 animate-spin" />
            </div>
          )}
          {status === 'completed' && (
            <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          )}
          {status === 'failed' && (
            <div className="p-2 rounded-lg bg-rose-500/20 text-rose-400">
              <AlertCircle className="w-5 h-5" />
            </div>
          )}

          <div>
            <h3 className="text-base font-semibold text-white">
              {status === 'evolving' && `Evoluindo População (Geração ${currentGeneration} de ${totalGenerations})`}
              {status === 'completed' && 'Otimização Concluída com Sucesso!'}
              {status === 'failed' && 'Falha na Execução da Otimização'}
            </h3>
            <p className="text-xs text-slate-400">
              {status === 'evolving' && 'Algoritmo genético explorando planos de compra viáveis...'}
              {status === 'completed' && 'O melhor plano viável foi selecionado e validado contra o orçamento.'}
              {status === 'failed' && 'Ocorreu um erro no processamento da tarefa.'}
            </p>
          </div>
        </div>

        {isSocketFailed && (
          <div className="flex items-center gap-1.5 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-lg">
            <WifiOff className="w-3.5 h-3.5" />
            <span>WebSocket desconectado — acompanhando via polling</span>
          </div>
        )}
      </div>

      {status === 'evolving' && (
        <div className="mt-3">
          <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-700/50">
            <div
              className="bg-gradient-to-r from-indigo-500 to-indigo-400 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};
