import React from 'react';
import Plot from 'react-plotly.js';
import { PurchaseLine } from '../../shared/api/contracts';
import { PieChart } from 'lucide-react';
import { formatCurrency } from '../../shared/formatting/currency';

interface BudgetDistributionChartProps {
  lines: PurchaseLine[];
}

export const BudgetDistributionChart: React.FC<BudgetDistributionChartProps> = ({
  lines,
}) => {
  // Only items with quantity > 0, ordered descending by line_cost
  const purchased = lines
    .filter((line) => line.quantity > 0)
    .sort((a, b) => b.line_cost - a.line_cost);

  if (purchased.length === 0) {
    return (
      <div className="bg-slate-800/80 backdrop-blur border border-slate-700/60 rounded-xl p-6 shadow-xl text-center">
        <p className="text-sm text-slate-400">Nenhum item comprado no plano atual.</p>
      </div>
    );
  }

  // Plotly horizontal bar: y ordered so top is highest (reverse for Plotly y-axis layout)
  const reversed = [...purchased].reverse();
  const y = reversed.map((l) => l.product);
  const x = reversed.map((l) => l.line_cost);
  const text = reversed.map((l) => formatCurrency(l.line_cost));

  return (
    <div className="bg-slate-800/80 backdrop-blur border border-slate-700/60 rounded-xl p-6 shadow-xl">
      <div className="flex items-center gap-2 mb-4">
        <PieChart className="w-5 h-5 text-indigo-400" />
        <h3 className="text-lg font-semibold text-white">
          Distribuição do Orçamento por Produto
        </h3>
      </div>

      <div className="w-full h-[280px]">
        <Plot
          data={[
            {
              type: 'bar',
              orientation: 'h',
              y,
              x,
              text,
              textposition: 'auto',
              marker: {
                color: '#6366f1',
                line: { color: '#818cf8', width: 1 },
              },
              hovertemplate: '%{y}: %{text}<extra></extra>',
            },
          ]}
          layout={{
            autosize: true,
            margin: { l: 140, r: 25, t: 15, b: 35 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            xaxis: {
              title: { text: 'Valor Alocado (R$)', font: { color: '#94a3b8', size: 12 } },
              tickfont: { color: '#94a3b8', size: 11 },
              gridcolor: '#334155',
            },
            yaxis: {
              tickfont: { color: '#e2e8f0', size: 12 },
              automargin: true,
            },
          }}
          config={{
            responsive: true,
            displayModeBar: false,
            locale: 'pt-BR',
          }}
          style={{ width: '100%', height: '100%' }}
        />
      </div>

      <table className="sr-only">
        <caption>Distribuição do orçamento por produto comprado</caption>
        <thead>
          <tr>
            <th scope="col">Produto</th>
            <th scope="col">Custo Total</th>
          </tr>
        </thead>
        <tbody>
          {purchased.map((line) => (
            <tr key={line.sku}>
              <td>{line.product}</td>
              <td>{formatCurrency(line.line_cost)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
