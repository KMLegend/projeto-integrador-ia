import React from 'react';
import Plot from 'react-plotly.js';
import { ConvergencePoint } from '../../shared/api/contracts';
import { Activity, Clock } from 'lucide-react';

interface ConvergenceChartProps {
  points: ConvergencePoint[];
  isLive?: boolean;
}

export const ConvergenceChart: React.FC<ConvergenceChartProps> = ({
  points,
  isLive = false,
}) => {
  if (!points || points.length === 0) {
    return (
      <div className="bg-slate-800/80 backdrop-blur border border-slate-700/60 rounded-xl p-8 shadow-xl flex flex-col items-center justify-center min-h-[320px] text-center">
        <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-full mb-3 animate-pulse">
          <Clock className="w-6 h-6" />
        </div>
        <h4 className="text-base font-medium text-slate-200">
          Aguardando primeira geração…
        </h4>
        <p className="text-xs text-slate-400 max-w-sm mt-1">
          A curva de evolução será desenhada em tempo real conforme as gerações forem avaliadas pelo Algoritmo Genético.
        </p>
      </div>
    );
  }

  const x = points.map((p) => p.generation);
  const y = points.map((p) => p.max_fitness);

  const minFitness = Math.min(...y);
  const maxFitness = Math.max(...y);
  const yMargin = Math.max(10, (maxFitness - minFitness) * 0.1);

  return (
    <div className="bg-slate-800/80 backdrop-blur border border-slate-700/60 rounded-xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-400" />
          <h3 className="text-lg font-semibold text-white">
            Curva de Convergência do Algoritmo Genético
          </h3>
        </div>
        {isLive && (
          <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            Ao vivo
          </span>
        )}
      </div>

      <div className="w-full h-[320px]">
        <Plot
          data={[
            {
              x,
              y,
              type: 'scatter',
              mode: 'lines+markers',
              marker: {
                color: '#818cf8',
                size: 6,
              },
              line: {
                color: '#6366f1',
                width: 3,
                shape: 'spline',
              },
              name: 'Melhor Fitness',
              hovertemplate: 'Geração: %{x}<br>Fitness: %{y:.2f}<extra></extra>',
            },
          ]}
          layout={{
            autosize: true,
            margin: { l: 55, r: 20, t: 20, b: 45 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            xaxis: {
              title: { text: 'Geração', font: { color: '#94a3b8', size: 12 } },
              tickfont: { color: '#94a3b8', size: 11 },
              gridcolor: '#334155',
              zeroline: false,
            },
            yaxis: {
              title: { text: 'Aptidão (Fitness)', font: { color: '#94a3b8', size: 12 } },
              tickfont: { color: '#94a3b8', size: 11 },
              gridcolor: '#334155',
              zeroline: false,
              // Decision D-09: Y-axis auto-scaled to the data, never 0-12500
              range: [minFitness - yMargin, maxFitness + yMargin],
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

      {/* Tabela de dados equivalente para acessibilidade */}
      <table className="sr-only">
        <caption>Histórico de convergência do Algoritmo Genético</caption>
        <thead>
          <tr>
            <th scope="col">Geração</th>
            <th scope="col">Fitness Máximo</th>
          </tr>
        </thead>
        <tbody>
          {points.map((p) => (
            <tr key={p.generation}>
              <td>{p.generation}</td>
              <td>{p.max_fitness.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
