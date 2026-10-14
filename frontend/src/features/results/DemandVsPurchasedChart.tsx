import React from 'react';
import Plot from 'react-plotly.js';
import { PurchaseLine } from '../../shared/api/contracts';
import { BarChart3 } from 'lucide-react';
import { formatUnits } from '../../shared/formatting/units';

interface DemandVsPurchasedChartProps {
  lines: PurchaseLine[];
}

export const DemandVsPurchasedChart: React.FC<DemandVsPurchasedChartProps> = ({
  lines,
}) => {
  if (!lines || lines.length === 0) {
    return null;
  }

  const products = lines.map((l) => l.product);
  const required = lines.map((l) => l.required_quantity);
  const purchased = lines.map((l) => l.quantity);

  return (
    <div className="bg-slate-800/80 backdrop-blur border border-slate-700/60 rounded-xl p-6 shadow-xl">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-5 h-5 text-indigo-400" />
        <h3 className="text-lg font-semibold text-white">
          Comparativo: Demanda Prevista vs. Quantidade Comprada
        </h3>
      </div>

      <div className="w-full h-[280px]">
        <Plot
          data={[
            {
              name: 'Necessidade Calculada',
              type: 'bar',
              x: products,
              y: required,
              marker: { color: '#94a3b8' },
              hovertemplate: '%{x}<br>Necessidade: %{y} un.<extra></extra>',
            },
            {
              name: 'Comprado pelo AG',
              type: 'bar',
              x: products,
              y: purchased,
              marker: { color: '#10b981' },
              hovertemplate: '%{x}<br>Comprado: %{y} un.<extra></extra>',
            },
          ]}
          layout={{
            barmode: 'group',
            autosize: true,
            margin: { l: 45, r: 25, t: 25, b: 65 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            legend: {
              orientation: 'h',
              x: 0,
              y: 1.15,
              font: { color: '#cbd5e1', size: 12 },
            },
            xaxis: {
              tickfont: { color: '#cbd5e1', size: 11 },
              tickangle: -20,
            },
            yaxis: {
              title: { text: 'Unidades', font: { color: '#94a3b8', size: 12 } },
              tickfont: { color: '#94a3b8', size: 11 },
              gridcolor: '#334155',
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
        <caption>Comparativo entre necessidade calculada e quantidade comprada</caption>
        <thead>
          <tr>
            <th scope="col">Produto</th>
            <th scope="col">Necessidade</th>
            <th scope="col">Comprado</th>
          </tr>
        </thead>
        <tbody>
          {lines.map((l) => (
            <tr key={l.sku}>
              <td>{l.product}</td>
              <td>{formatUnits(l.required_quantity)}</td>
              <td>{formatUnits(l.quantity)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
