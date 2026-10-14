import React from 'react';
import { ScenarioSummary } from '../../shared/api/contracts';
import { formatCurrency } from '../../shared/formatting/currency';
import { formatPercentage } from '../../shared/formatting/percentage';
import { formatUnits } from '../../shared/formatting/units';
import {
  DollarSign,
  ShoppingCart,
  AlertTriangle,
  TrendingUp,
  Cpu,
} from 'lucide-react';

interface KpiCardsProps {
  summary: ScenarioSummary;
  modelMae: number;
}

export const KpiCards: React.FC<KpiCardsProps> = ({ summary, modelMae }) => {
  const formattedFitness = new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(summary.fitness);

  const formattedMae = new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(modelMae);

  const riskLabel =
    summary.items_at_risk === 1
      ? '1 produto em risco'
      : `${summary.items_at_risk} produtos em risco`;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      {/* 1. Custo Total & Uso do Orçamento */}
      <div className="bg-slate-800/80 backdrop-blur border border-slate-700/60 rounded-xl p-4 shadow-lg flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-medium uppercase tracking-wider">Custo Total</span>
          <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
            <DollarSign className="w-4 h-4" />
          </div>
        </div>
        <div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {formatCurrency(summary.total_cost)}
          </div>
          <div className="text-xs text-emerald-400 font-medium mt-1">
            {formatPercentage(summary.budget_usage_ratio)} do orçamento utilizado
          </div>
        </div>
      </div>

      {/* 2. Atendimento da Demanda */}
      <div className="bg-slate-800/80 backdrop-blur border border-slate-700/60 rounded-xl p-4 shadow-lg flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-medium uppercase tracking-wider">Atendimento</span>
          <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400">
            <ShoppingCart className="w-4 h-4" />
          </div>
        </div>
        <div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {formatPercentage(summary.served_ratio)}
          </div>
          <div className="text-xs text-slate-300 font-medium mt-1">
            {formatUnits(summary.served_quantity)} de {formatUnits(summary.required_total)}
          </div>
        </div>
      </div>

      {/* 3. Itens em Risco */}
      <div className="bg-slate-800/80 backdrop-blur border border-slate-700/60 rounded-xl p-4 shadow-lg flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-medium uppercase tracking-wider">Risco de Ruptura</span>
          <div className={`p-1.5 rounded-lg ${summary.items_at_risk > 0 ? 'bg-amber-500/10 text-amber-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
            <AlertTriangle className="w-4 h-4" />
          </div>
        </div>
        <div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {riskLabel}
          </div>
          <div className="text-xs text-slate-400 mt-1">
            {summary.items_at_risk === 0 ? 'Estoque seguro para o ciclo' : 'Abaixo da margem de segurança'}
          </div>
        </div>
      </div>

      {/* 4. Fitness do Plano */}
      <div className="bg-slate-800/80 backdrop-blur border border-slate-700/60 rounded-xl p-4 shadow-lg flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-medium uppercase tracking-wider">Fitness AG</span>
          <div className="p-1.5 rounded-lg bg-purple-500/10 text-purple-400">
            <TrendingUp className="w-4 h-4" />
          </div>
        </div>
        <div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {formattedFitness}
          </div>
          <div className="text-xs text-purple-300 font-medium mt-1">
            Score ponderado de aptidão
          </div>
        </div>
      </div>

      {/* 5. Precisão do Modelo (MAE) */}
      <div className="bg-slate-800/80 backdrop-blur border border-slate-700/60 rounded-xl p-4 shadow-lg flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-medium uppercase tracking-wider">Erro do Modelo</span>
          <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400">
            <Cpu className="w-4 h-4" />
          </div>
        </div>
        <div>
          <div className="text-2xl font-bold text-white tracking-tight">
            ± {formattedMae}
          </div>
          <div className="text-xs text-slate-400 mt-1">
            un./semana (MAE Regressão)
          </div>
        </div>
      </div>
    </div>
  );
};
