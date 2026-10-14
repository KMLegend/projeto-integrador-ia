import { OptimizationRequest } from '../../shared/api/contracts';

export interface OptimizationFormData {
  budget_limit: number;
  population_size: number;
  generations: number;
  mutation_rate: number;
  parents_size: number;
  elite_size: number;
  cycle_weeks: number;
  random_seed: number;
  dataset_reference: string;
}

export const defaultOptimizationFormData: OptimizationFormData = {
  budget_limit: 1000.0,
  population_size: 60,
  generations: 100,
  mutation_rate: 0.2,
  parents_size: 20,
  elite_size: 2,
  cycle_weeks: 4,
  random_seed: 42,
  dataset_reference: 'historico_mensal_v1',
};

export type FormErrors = Partial<Record<keyof OptimizationFormData, string>>;

export function validateOptimizationForm(data: OptimizationFormData): FormErrors {
  const errors: FormErrors = {};

  if (!data.budget_limit || data.budget_limit <= 0) {
    errors.budget_limit = 'O orçamento deve ser maior que zero.';
  }

  if (!Number.isInteger(data.population_size) || data.population_size < 10 || data.population_size > 500) {
    errors.population_size = 'O tamanho da população deve ser um número inteiro entre 10 e 500.';
  }

  if (!Number.isInteger(data.generations) || data.generations < 10 || data.generations > 500) {
    errors.generations = 'O número de gerações deve ser um número inteiro entre 10 e 500.';
  }

  if (isNaN(data.mutation_rate) || data.mutation_rate < 0.01 || data.mutation_rate > 1.0) {
    errors.mutation_rate = 'A taxa de mutação deve estar entre 0,01 e 1,00.';
  }

  if (!Number.isInteger(data.parents_size) || data.parents_size < 2 || data.parents_size > data.population_size) {
    errors.parents_size = 'O número de pais deve ser entre 2 e o tamanho da população.';
  }

  if (!Number.isInteger(data.elite_size) || data.elite_size < 0 || data.elite_size > data.population_size) {
    errors.elite_size = 'O tamanho da elite deve ser entre 0 e o tamanho da população.';
  }

  if (!Number.isInteger(data.cycle_weeks) || data.cycle_weeks < 1 || data.cycle_weeks > 52) {
    errors.cycle_weeks = 'O ciclo deve estar entre 1 e 52 semanas.';
  }

  return errors;
}

export function toOptimizationRequest(data: OptimizationFormData): OptimizationRequest {
  return {
    budget_limit: Number(data.budget_limit),
    dataset_reference: data.dataset_reference || 'default',
    cycle_weeks: Number(data.cycle_weeks),
    ga_parameters: {
      population_size: Number(data.population_size),
      generations: Number(data.generations),
      mutation_rate: Number(data.mutation_rate),
      parents_size: Number(data.parents_size),
      elite_size: Number(data.elite_size),
      random_seed: Number(data.random_seed),
    },
  };
}
