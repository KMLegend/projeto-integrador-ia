import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ConvergenceChart } from '../ConvergenceChart';

vi.mock('react-plotly.js', () => ({
  default: ({ data, layout }: { data: unknown[]; layout: unknown }) => (
    <div data-testid="plotly-chart" data-points={JSON.stringify(data)} data-layout={JSON.stringify(layout)} />
  ),
}));

describe('ConvergenceChart', () => {
  it('exibe estado vazio explicito quando nao ha pontos', () => {
    render(<ConvergenceChart points={[]} />);
    expect(screen.getByText('Aguardando primeira geração…')).toBeInTheDocument();
  });

  it('renderiza grafico e escala eixo Y dinamicamente pelos dados (D-09)', () => {
    const points = [
      { generation: 0, max_fitness: 777.67 },
      { generation: 50, max_fitness: 800.12 },
      { generation: 100, max_fitness: 816.92 },
    ];

    render(<ConvergenceChart points={points} isLive={true} />);

    const chart = screen.getByTestId('plotly-chart');
    expect(chart).toBeInTheDocument();

    const layout = JSON.parse(chart.getAttribute('data-layout') || '{}');
    expect(layout.yaxis.range).toBeDefined();
    // Verify it is NOT 0 to 12500
    expect(layout.yaxis.range[0]).toBeGreaterThan(700);
    expect(layout.yaxis.range[1]).toBeLessThan(1000);
  });
});
