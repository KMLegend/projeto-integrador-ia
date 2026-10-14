export type TaskStatus = 'PROCESSING' | 'COMPLETED' | 'FAILED';

export interface GaParameters {
  population_size: number;
  generations: number;
  mutation_rate?: number;
  parents_size?: number;
  elite_size?: number;
  random_seed?: number;
}

export interface OptimizationRequest {
  budget_limit: number;
  dataset_reference: string;
  ga_parameters: GaParameters;
  cycle_weeks?: number;
}

export interface StartOptimizationResponse {
  task_id: string;
  status: TaskStatus;
  message: string;
}

export interface ScenarioSummary {
  total_cost: number;
  budget_limit: number;
  budget_usage_ratio: number;
  served_quantity: number;
  required_total: number;
  served_ratio: number;
  items_at_risk: number;
  fitness: number;
}

export interface PurchaseLine {
  sku: string;
  product: string;
  quantity: number;
  unit_cost: number;
  required_quantity: number;
  uncovered_quantity: number;
  line_cost: number;
}

export interface ConvergencePoint {
  generation: number;
  max_fitness: number;
}

export interface StrategyIndicators {
  total_cost: number;
  served_quantity: number;
  served_ratio: number;
  items_at_risk: number;
  fitness: number;
}

export interface OptimizationResult {
  best_scenario_summary: ScenarioSummary;
  items_to_buy: PurchaseLine[];
  baseline_comparison: {
    baseline: StrategyIndicators;
    optimized: StrategyIndicators;
  };
  convergence_curve: ConvergencePoint[];
  model_metrics: {
    mae: number;
    features: string[];
  };
}

export interface OptimizationStatusResponse {
  task_id: string;
  status: TaskStatus;
  result: OptimizationResult | null;
  error?: {
    code: string;
    message: string;
  };
}

export interface ProgressMessage {
  generation: number;
  max_fitness: number;
  status: 'evolving' | 'completed' | 'failed';
}
