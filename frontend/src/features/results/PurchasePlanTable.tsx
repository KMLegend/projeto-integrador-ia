import React from 'react';
import { PurchaseLine } from '../../shared/api/contracts';
import { formatCurrency } from '../../shared/formatting/currency';
import { formatUnits } from '../../shared/formatting/units';
import { Package } from 'lucide-react';

interface PurchasePlanTableProps {
  lines: PurchaseLine[];
}

export const PurchasePlanTable: React.FC<PurchasePlanTableProps> = ({ lines }) => {
  return (
    <div className="bg-slate-800/80 backdrop-blur border border-slate-700/60 rounded-xl p-6 shadow-xl">
      <div className="flex items-center gap-2 mb-4">
        <Package className="w-5 h-5 text-indigo-400" />
        <h3 className="text-lg font-semibold text-white">
          Plano Recomendado de Reposição
        </h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <caption className="sr-only">Plano Recomendado de Reposição de Estoque</caption>
          <thead className="bg-slate-900/80 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-700">
            <tr>
              <th scope="col" className="py-3 px-4">SKU</th>
              <th scope="col" className="py-3 px-4">Produto</th>
              <th scope="col" className="py-3 px-4 text-right">Qtd. a Comprar</th>
              <th scope="col" className="py-3 px-4 text-right">Custo Unitário</th>
              <th scope="col" className="py-3 px-4 text-right">Custo Total</th>
              <th scope="col" className="py-3 px-4 text-right">Necessidade</th>
              <th scope="col" className="py-3 px-4 text-right">Não Atendido</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/60">
            {lines.map((line) => (
              <tr key={line.sku} className="hover:bg-slate-700/30 transition-colors">
                <td className="py-3.5 px-4 font-mono text-xs text-indigo-300">
                  {line.sku}
                </td>
                <td className="py-3.5 px-4 font-medium text-white">
                  {line.product}
                </td>
                <td className="py-3.5 px-4 text-right font-semibold text-emerald-400">
                  {formatUnits(line.quantity)}
                </td>
                <td className="py-3.5 px-4 text-right">
                  {formatCurrency(line.unit_cost)}
                </td>
                <td className="py-3.5 px-4 text-right font-semibold text-white">
                  {formatCurrency(line.line_cost)}
                </td>
                <td className="py-3.5 px-4 text-right text-slate-400">
                  {formatUnits(line.required_quantity)}
                </td>
                <td className="py-3.5 px-4 text-right">
                  {line.uncovered_quantity > 0 ? (
                    <span className="text-amber-400 font-medium">
                      {formatUnits(line.uncovered_quantity)}
                    </span>
                  ) : (
                    <span className="text-slate-500">0 un.</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
