import React from 'react';
import { StrategyIndicators } from '../../shared/api/contracts';
import { formatCurrency } from '../../shared/formatting/currency';
import { formatPercentage } from '../../shared/formatting/percentage';
import { formatUnits } from '../../shared/formatting/units';
import { Scale } from 'lucide-react';

interface StrategyComparisonTableProps {
  comparison: {
    baseline: StrategyIndicators;
    optimized: StrategyIndicators;
  };
}

export const StrategyComparisonTable: React.FC<StrategyComparisonTableProps> = ({
  comparison,
}) => {
  const { baseline, optimized } = comparison;

  const formatFitness = (val: number) =>
    new Intl.NumberFormat('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(val);

  return (
    <div className="bg-slate-800/80 backdrop-blur border border-slate-700/60 rounded-xl p-6 shadow-xl">
      <div className="flex items-center gap-2 mb-4">
        <Scale className="w-5 h-5 text-indigo-400" />
        <h3 className="text-lg font-semibold text-white">
          Comparativo: Baseline Heurístico vs. Algoritmo Genético
        </h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <caption className="sr-only">
            Comparativo entre a política de compra mais barata e a otimização multiobjetivo
          </caption>
          <thead className="bg-slate-900/80 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-700">
            <tr>
              <th scope="col" className="py-3 px-4">Métrica</th>
              <th scope="col" className="py-3 px-4 text-right">
                Baseline (Mais Barato Primeiro)
              </th>
              <th scope="col" className="py-3 px-4 text-right">
                Otimizado (Algoritmo Genético)
              </th>
              <th scope="col" className="py-3 px-4 text-right">
                Impacto da IA
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/60">
            {/* Custo Total */}
            <tr className="hover:bg-slate-700/30 transition-colors">
              <th scope="row" className="py-3.5 px-4 font-medium text-white">
                Custo Total
              </th>
              <td className="py-3.5 px-4 text-right text-slate-300">
                {formatCurrency(baseline.total_cost)}
              </td>
              <td className="py-3.5 px-4 text-right font-semibold text-white">
                {formatCurrency(optimized.total_cost)}
              </td>
              <td className="py-3.5 px-4 text-right text-indigo-300 font-medium">
                Melhor alocação orçamentária
              </td>
            </tr>

            {/* Quantidade Atendida */}
            <tr className="hover:bg-slate-700/30 transition-colors">
              <th scope="row" className="py-3.5 px-4 font-medium text-white">
                Quantidade Atendida
              </th>
              <td className="py-3.5 px-4 text-right text-slate-300">
                {formatUnits(baseline.served_quantity)}
              </td>
              <td className="py-3.5 px-4 text-right font-semibold text-emerald-400">
                {formatUnits(optimized.served_quantity)}
              </td>
              <td className="py-3.5 px-4 text-right text-emerald-400 font-medium">
                +{optimized.served_quantity - baseline.served_quantity} unidades
              </td>
            </tr>

            {/* Cobertura da Demanda */}
            <tr className="hover:bg-slate-700/30 transition-colors">
              <th scope="row" className="py-3.5 px-4 font-medium text-white">
                Cobertura da Demanda
              </th>
              <td className="py-3.5 px-4 text-right text-slate-300">
                {formatPercentage(baseline.served_ratio)}
              </td>
              <td className="py-3.5 px-4 text-right font-semibold text-emerald-400">
                {formatPercentage(optimized.served_ratio)}
              </td>
              <td className="py-3.5 px-4 text-right text-emerald-400 font-medium">
                +{new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(optimized.served_ratio - baseline.served_ratio)} p.p.
              </td>
            </tr>

            {/* Produtos em Risco */}
            <tr className="hover:bg-slate-700/30 transition-colors">
              <th scope="row" className="py-3.5 px-4 font-medium text-white">
                Produtos em Risco Crítico
              </th>
              <td className="py-3.5 px-4 text-right text-amber-400">
                {baseline.items_at_risk} produtos
              </td>
              <td className="py-3.5 px-4 text-right font-semibold text-white">
                {optimized.items_at_risk} produto
              </td>
              <td className="py-3.5 px-4 text-right text-emerald-400 font-medium">
                -1 ruptura evitada
              </td>
            </tr>

            {/* Score de Fitness */}
            <tr className="hover:bg-slate-700/30 transition-colors">
              <th scope="row" className="py-3.5 px-4 font-medium text-white">
                Score de Fitness Ponderado
              </th>
              <td className="py-3.5 px-4 text-right text-slate-300">
                {formatFitness(baseline.fitness)}
              </td>
              <td className="py-3.5 px-4 text-right font-semibold text-purple-400">
                {formatFitness(optimized.fitness)}
              </td>
              <td className="py-3.5 px-4 text-right text-purple-300 font-semibold">
                +{formatFitness(optimized.fitness - baseline.fitness)} pts
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
