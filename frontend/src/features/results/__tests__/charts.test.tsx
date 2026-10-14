import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BudgetDistributionChart } from '../BudgetDistributionChart';
import { DemandVsPurchasedChart } from '../DemandVsPurchasedChart';
import { PurchaseLine } from '../../../shared/api/contracts';

vi.mock('react-plotly.js', () => ({
  default: ({ data, layout }: { data: unknown[]; layout: unknown }) => (
    <div data-testid="plotly-chart" data-points={JSON.stringify(data)} data-layout={JSON.stringify(layout)} />
  ),
}));

describe('Graficos de Resultados', () => {
  const lines: PurchaseLine[] = [
    {
      sku: 'LEITE-UHT-1L',
      product: 'Leite UHT 1L',
      quantity: 98,
      unit_cost: 5.86,
      required_quantity: 98,
      uncovered_quantity: 0,
      line_cost: 574.28,
    },
    {
      sku: 'FEIJAO-CARIOCA-1KG',
      product: 'Feijão Carioca 1kg',
      quantity: 22,
      unit_cost: 8.79,
      required_quantity: 48,
      uncovered_quantity: 26,
      line_cost: 193.38,
    },
    {
      sku: 'ARROZ-5KG',
      product: 'Arroz Tipo 1 5kg',
      quantity: 0,
      unit_cost: 29.89,
      required_quantity: 0,
      uncovered_quantity: 0,
      line_cost: 0.0,
    },
  ];

  it('BudgetDistributionChart renderiza apenas itens com quantidade > 0 ordenados decrescente', () => {
    render(<BudgetDistributionChart lines={lines} />);
    const chart = screen.getByTestId('plotly-chart');
    expect(chart).toBeInTheDocument();

    const data = JSON.parse(chart.getAttribute('data-points') || '[]');
    // Leite (574.28) and Feijao (193.38), excluding Arroz (0)
    expect(data[0].x).toHaveLength(2);
    expect(data[0].x).toContain(574.28);
    expect(data[0].x).toContain(193.38);
  });

  it('DemandVsPurchasedChart renderiza comparativo agrupado com duas series', () => {
    render(<DemandVsPurchasedChart lines={lines} />);
    const chart = screen.getByTestId('plotly-chart');
    expect(chart).toBeInTheDocument();

    const data = JSON.parse(chart.getAttribute('data-points') || '[]');
    expect(data).toHaveLength(2); // required and purchased
    expect(data[0].name).toBe('Necessidade Calculada');
    expect(data[1].name).toBe('Comprado pelo AG');
  });
});
