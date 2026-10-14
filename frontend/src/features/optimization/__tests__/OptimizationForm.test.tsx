import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { OptimizationForm } from '../OptimizationForm';
import { validateOptimizationForm, defaultOptimizationFormData } from '../optimizationFormSchema';

describe('OptimizationForm', () => {
  it('valida formulario e rejeita orcamento negativo ou zero', () => {
    const errorsZero = validateOptimizationForm({
      ...defaultOptimizationFormData,
      budget_limit: 0,
    });
    expect(errorsZero.budget_limit).toBe('O orçamento deve ser maior que zero.');

    const errorsNegative = validateOptimizationForm({
      ...defaultOptimizationFormData,
      budget_limit: -100,
    });
    expect(errorsNegative.budget_limit).toBe('O orçamento deve ser maior que zero.');
  });

  it('valida limites de populacao e geracoes', () => {
    const errors = validateOptimizationForm({
      ...defaultOptimizationFormData,
      population_size: 5,
      generations: 1000,
    });
    expect(errors.population_size).toBe('O tamanho da população deve ser um número inteiro entre 10 e 500.');
    expect(errors.generations).toBe('O número de gerações deve ser um número inteiro entre 10 e 500.');
  });

  it('renderiza inputs com valores padrao e permite submissao', () => {
    const handleSubmit = vi.fn();
    render(<OptimizationForm onSubmit={handleSubmit} isSubmitting={false} />);

    const budgetInput = screen.getByLabelText(/Orçamento Limite/i);
    expect(budgetInput).toHaveValue(1000);

    const submitButton = screen.getByRole('button', { name: /Otimizar Reposição/i });
    fireEvent.click(submitButton);

    expect(handleSubmit).toHaveBeenCalledTimes(1);
    expect(handleSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        budget_limit: 1000,
        ga_parameters: expect.objectContaining({
          population_size: 60,
          generations: 100,
          mutation_rate: 0.2,
        }),
      })
    );
  });

  it('desabilita botao e exibe spinner durante envio', () => {
    render(<OptimizationForm onSubmit={vi.fn()} isSubmitting={true} />);
    const submitButton = screen.getByRole('button', { name: /Iniciando otimização.../i });
    expect(submitButton).toBeDisabled();
  });
});
