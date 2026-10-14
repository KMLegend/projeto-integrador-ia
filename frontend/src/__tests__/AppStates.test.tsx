import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { App } from '../App';
import * as useStartModule from '../features/optimization/useStartOptimization';
import * as useStatusModule from '../features/optimization/useOptimizationStatus';
import * as useSocketModule from '../features/convergence/useProgressSocket';
import { OptimizationResult } from '../shared/api/contracts';

vi.mock('react-plotly.js', () => ({
  default: ({ data }: { data: unknown }) => (
    <div data-testid="plotly-chart" data-points={JSON.stringify(data)} />
  ),
}));

describe('App - 7 Estados Obrigatórios de UI (TASK 37)', () => {
  const renderWithQuery = (ui: React.ReactElement) => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
  };

  it('Estado 1 - Inicial: renderiza formulario com valores padrao e explicacao', () => {
    renderWithQuery(<App />);

    expect(screen.getByText('Otimização Preditiva de Estoque')).toBeInTheDocument();
    expect(screen.getByLabelText(/Orçamento Limite/i)).toHaveValue(1000);
    expect(screen.getByLabelText(/População do AG/i)).toHaveValue(60);
    expect(screen.getByLabelText(/Gerações do AG/i)).toHaveValue(100);
    expect(screen.getByRole('button', { name: /Otimizar Reposição/i })).toBeInTheDocument();
  });

  it('Estado 2 - Enviando: desabilita botao e exibe spinner', () => {
    vi.spyOn(useStartModule, 'useStartOptimization').mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: true,
      reset: vi.fn(),
    } as unknown as ReturnType<typeof useStartModule.useStartOptimization>);

    renderWithQuery(<App />);
    const submitButton = screen.getByRole('button', { name: /Iniciando otimização.../i });
    expect(submitButton).toBeDisabled();
  });

  it('Estado 3 - Processando: exibe banner com geracao atual e curva ao vivo', () => {
    vi.spyOn(useStartModule, 'useStartOptimization').mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
      reset: vi.fn(),
    } as unknown as ReturnType<typeof useStartModule.useStartOptimization>);

    vi.spyOn(useStatusModule, 'useOptimizationStatus').mockReturnValue({
      data: {
        task_id: 'task-live-1',
        status: 'PROCESSING',
        result: null,
      },
    } as unknown as ReturnType<typeof useStatusModule.useOptimizationStatus>);

    vi.spyOn(useSocketModule, 'useProgressSocket').mockReturnValue({
      points: [
        { generation: 0, max_fitness: 777.67 },
        { generation: 20, max_fitness: 800.0 },
      ],
      isConnected: true,
      isSocketFailed: false,
      status: 'evolving',
      currentGeneration: 20,
    });

    renderWithQuery(<App initialTaskId="task-live-1" />);
    expect(screen.getByText(/Evoluindo População/i)).toBeInTheDocument();
    expect(screen.getByText(/Geração 20/i)).toBeInTheDocument();
  });

  it('Estado 4 - WebSocket indisponivel: exibe aviso discreto sem bloquear tela', () => {
    vi.spyOn(useStatusModule, 'useOptimizationStatus').mockReturnValue({
      data: {
        task_id: 'task-live-2',
        status: 'PROCESSING',
        result: null,
      },
    } as unknown as ReturnType<typeof useStatusModule.useOptimizationStatus>);

    vi.spyOn(useSocketModule, 'useProgressSocket').mockReturnValue({
      points: [],
      isConnected: false,
      isSocketFailed: true,
      status: 'evolving',
      currentGeneration: 10,
    });

    renderWithQuery(<App initialTaskId="task-live-2" />);
    expect(
      screen.getByText(/WebSocket desconectado — acompanhando via polling/i)
    ).toBeInTheDocument();
  });

  it('Estado 5 - Concluido: renderiza KPIs, plano e comparativo de referencia', () => {
    const mockResult: OptimizationResult = {
      best_scenario_summary: {
        total_cost: 987.44,
        budget_limit: 1000.0,
        budget_usage_ratio: 98.7,
        served_quantity: 120,
        required_total: 146,
        served_ratio: 82.2,
        items_at_risk: 1,
        fitness: 816.92,
      },
      items_to_buy: [
        {
          sku: 'LEITE-UHT-1L',
          product: 'Leite UHT 1L',
          quantity: 98,
          unit_cost: 5.86,
          required_quantity: 98,
          uncovered_quantity: 0,
          line_cost: 574.28,
        },
      ],
      baseline_comparison: {
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
      },
      convergence_curve: [{ generation: 0, max_fitness: 777.67 }],
      model_metrics: { mae: 4.76, features: ['f1', 'f2'] },
    };

    vi.spyOn(useStatusModule, 'useOptimizationStatus').mockReturnValue({
      data: {
        task_id: 'task-completed-5',
        status: 'COMPLETED',
        result: mockResult,
      },
    } as unknown as ReturnType<typeof useStatusModule.useOptimizationStatus>);

    renderWithQuery(<App />);

    const text = document.body.textContent?.replace(/\u00a0/g, ' ') || '';
    expect(text).toContain('R$ 987,44');
    expect(text).toContain('82,2%');
    expect(text).toContain('1 produto em risco');
    expect(text).toContain('Leite UHT 1L');
  });

  it('Estado 6 - Falha: exibe mensagem em portugues e botao de nova tentativa', () => {
    vi.spyOn(useStatusModule, 'useOptimizationStatus').mockReturnValue({
      data: {
        task_id: 'task-failed-6',
        status: 'FAILED',
        result: null,
        error: {
          code: 'BUDGET_INSUFFICIENT',
          message: 'Orçamento insuficiente para cobrir lote mínimo.',
        },
      },
    } as unknown as ReturnType<typeof useStatusModule.useOptimizationStatus>);

    renderWithQuery(<App />);

    expect(screen.getByText('Falha ao executar otimização')).toBeInTheDocument();
    expect(
      screen.getByText('Orçamento insuficiente para cobrir lote mínimo.')
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Tentar novamente/i })).toBeInTheDocument();
  });

  it('Estado 7 - Resultado vazio: exibe mensagem de estoque suficiente quando nao ha necessidade', () => {
    const mockZeroResult: OptimizationResult = {
      best_scenario_summary: {
        total_cost: 0,
        budget_limit: 1000.0,
        budget_usage_ratio: 0,
        served_quantity: 0,
        required_total: 0,
        served_ratio: 100.0,
        items_at_risk: 0,
        fitness: 0,
      },
      items_to_buy: [],
      baseline_comparison: {
        baseline: {
          total_cost: 0,
          served_quantity: 0,
          served_ratio: 100,
          items_at_risk: 0,
          fitness: 0,
        },
        optimized: {
          total_cost: 0,
          served_quantity: 0,
          served_ratio: 100,
          items_at_risk: 0,
          fitness: 0,
        },
      },
      convergence_curve: [],
      model_metrics: { mae: 4.76, features: ['f1'] },
    };

    vi.spyOn(useStatusModule, 'useOptimizationStatus').mockReturnValue({
      data: {
        task_id: 'task-zero-7',
        status: 'COMPLETED',
        result: mockZeroResult,
      },
    } as unknown as ReturnType<typeof useStatusModule.useOptimizationStatus>);

    renderWithQuery(<App />);

    expect(
      screen.getByText(/Estoque suficiente para o ciclo — nenhuma compra necessária/i)
    ).toBeInTheDocument();
  });
});
