import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KpiCards } from '../KpiCards';
import { PurchasePlanTable } from '../PurchasePlanTable';
import { StrategyComparisonTable } from '../StrategyComparisonTable';
import { ScenarioSummary, PurchaseLine } from '../../../shared/api/contracts';

describe('Resultados - Componentes com valores-ouro de referencia', () => {
  const referenceSummary: ScenarioSummary = {
    total_cost: 987.44,
    budget_limit: 1000.0,
    budget_usage_ratio: 98.7,
    served_quantity: 120,
    required_total: 146,
    served_ratio: 82.2,
    items_at_risk: 1,
    fitness: 816.92,
  };

  const referenceMae = 4.76;

  it('exibe todos os 5 KPIs formatados em pt-BR', () => {
    render(<KpiCards summary={referenceSummary} modelMae={referenceMae} />);

    // R$ 987,44 (normalize non-breaking spaces)
    const containerText = document.body.textContent?.replace(/\u00a0/g, ' ') || '';
    expect(containerText).toContain('R$ 987,44');
    expect(containerText).toContain('98,7% do orçamento utilizado');
    expect(containerText).toContain('82,2%');
    expect(containerText).toContain('120 un. de 146 un.');
    expect(containerText).toContain('1 produto em risco');
    expect(containerText).toContain('816,92');
    expect(containerText).toContain('± 4,76');
  });

  it('renderiza PurchasePlanTable com caption e th de cabecalho', () => {
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
    ];

    render(<PurchasePlanTable lines={lines} />);

    expect(screen.getByText('Leite UHT 1L')).toBeInTheDocument();
    expect(screen.getByText('Feijão Carioca 1kg')).toBeInTheDocument();
    expect(document.querySelector('caption')).toBeInTheDocument();
    expect(document.querySelectorAll('th[scope="col"]').length).toBeGreaterThan(0);
  });

  it('renderiza StrategyComparisonTable confrontando baseline x otimizado', () => {
    const comparison = {
      baseline: {
        total_cost: 314.32,
        served_quantity: 36,
        served_ratio: 24.7,
        items_at_risk: 2,
        fitness: 236.58,
      },
      optimized: {
        total_cost: 987.44,
        served_quantity: 120,
        served_ratio: 82.2,
        items_at_risk: 1,
        fitness: 816.92,
      },
    };

    render(<StrategyComparisonTable comparison={comparison} />);

    const text = document.body.textContent?.replace(/\u00a0/g, ' ') || '';
    expect(text).toContain('R$ 314,32');
    expect(text).toContain('R$ 987,44');
    expect(text).toContain('36 un.');
    expect(text).toContain('120 un.');
    expect(text).toContain('24,7%');
    expect(text).toContain('82,2%');
    expect(text).toContain('2 produtos');
    expect(text).toContain('1 produto');
  });
});
