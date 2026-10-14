---
id: 03-contratos-de-codigo-frontend
dominio: implementacao
palavras-chave: frontend, react, typescript, vite, tanstack query, react-query, plotly, tailwind, websocket, hooks, componentes
fonte-da-verdade: .context/00-arquitetura-tecnica/especifica_es_do_frontend.md + contratos_de_api.md
depende-de: [01-estrutura-de-diretorios, 02-contratos-de-codigo-backend]
---

# Contratos de Código — Frontend

Stack fixa: **React + Vite + TypeScript + TanStack Query + react-plotly.js + TailwindCSS**.

---

## 1. Tipos do contrato (`shared/api/contracts.ts`)

Único lugar do frontend com os tipos da API. Nenhum componente declara tipo de resposta por conta própria.

```ts
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

export interface ConvergencePoint { generation: number; max_fitness: number; }

export interface StrategyIndicators {
  total_cost: number; served_quantity: number; served_ratio: number;
  items_at_risk: number; fitness: number;
}

export interface OptimizationResult {
  best_scenario_summary: ScenarioSummary;
  items_to_buy: PurchaseLine[];
  baseline_comparison: { baseline: StrategyIndicators; optimized: StrategyIndicators };
  convergence_curve: ConvergencePoint[];
  model_metrics: { mae: number; features: string[] };
}

export interface OptimizationStatusResponse {
  task_id: string;
  status: TaskStatus;
  result: OptimizationResult | null;
  error?: { code: string; message: string };
}

export interface ProgressMessage {
  generation: number;
  max_fitness: number;
  status: 'evolving' | 'completed' | 'failed';
}
```

## 2. Clientes (`shared/api/`)

```ts
// httpClient.ts — DIP: componentes dependem da interface, nao do fetch
export interface OptimizationApi {
  start(request: OptimizationRequest): Promise<StartOptimizationResponse>;
  status(taskId: string): Promise<OptimizationStatusResponse>;
}
export function createOptimizationApi(baseUrl: string): OptimizationApi;

// websocketClient.ts
export interface ProgressChannel {
  subscribe(taskId: string, onMessage: (message: ProgressMessage) => void): () => void;
}
export function createProgressChannel(baseUrl: string): ProgressChannel;
```

Em teste, injeta-se uma implementação falsa de `OptimizationApi` — sem mock de `fetch`.

## 3. Hooks (`features/*/hooks/`)

```ts
// useStartOptimization.ts
export function useStartOptimization(): UseMutationResult<StartOptimizationResponse, Error, OptimizationRequest>;

// useOptimizationStatus.ts — polling como rede de seguranca do WebSocket
export function useOptimizationStatus(taskId: string | null): UseQueryResult<OptimizationStatusResponse>;

// useProgressSocket.ts — curva em tempo real; cai para polling se o socket falhar
export function useProgressSocket(taskId: string | null): {
  points: ConvergencePoint[];
  isConnected: boolean;
};
```

Configuração do TanStack Query para o status:

| Opção | Valor | Motivo |
|---|---|---|
| `enabled` | `taskId !== null` | Não consulta antes de existir tarefa |
| `refetchInterval` | `2000` enquanto `PROCESSING`, `false` quando `COMPLETED`/`FAILED` | Polling é fallback, não carga permanente |
| `staleTime` | `Infinity` após conclusão | Resultado é imutável |
| `retry` | `2` | Tolera instabilidade de rede |

## 4. Componentes

| Componente | Feature | Responsabilidade única | Props |
|---|---|---|---|
| `OptimizationForm` | optimization | Capturar orçamento e parâmetros do AG | `onSubmit(request)`, `isSubmitting` |
| `KpiCards` | results | Exibir os 5 KPIs | `summary`, `modelMae` |
| `PurchasePlanTable` | results | Tabela do plano recomendado | `lines` |
| `StrategyComparisonTable` | results | Baseline × otimizado | `comparison` |
| `BudgetDistributionChart` | results | Distribuição do orçamento por SKU | `lines` |
| `ConvergenceChart` | convergence | Curva de fitness por geração | `points`, `isLive` |
| `ProgressBanner` | convergence | Estado e geração atual | `status`, `currentGeneration` |

Regras:

* Componente **não** faz cálculo de negócio. Se precisar de valor derivado, ele vem do backend ou de função pura em `shared/formatting/`.
* Componente de `shared/ui/` não conhece domínio de estoque.
* Uma feature nunca importa de outra feature.

## 5. Gráficos (react-plotly.js)

| Gráfico | Tipo | Eixos / dados | Observações |
|---|---|---|---|
| Curva de convergência | `scatter` modo `lines+markers` | x = `generation`, y = `max_fitness` | Atualiza por WebSocket; eixo y começa abaixo do primeiro valor, não em 0, para a evolução ser visível |
| Distribuição de orçamento | `bar` horizontal | y = produto, x = `line_cost` | Ordenado por custo decrescente; só itens com `quantity > 0` |
| Necessidade × comprado | `bar` agrupado | duas séries por produto | Evidencia o saldo de risco |

Padrões obrigatórios: `locale: 'pt-BR'`, `responsive: true`, rótulos em português, moeda formatada em `R$`, tooltip com unidades. Paleta consistente entre os três gráficos; estado vazio explícito ("Aguardando primeira geração…") em vez de gráfico em branco.

## 6. Formatação pt-BR (`shared/formatting/`)

```ts
export function formatCurrency(value: number): string;   // 987.44  -> "R$ 987,44"
export function formatPercentage(value: number): string; // 82.1917 -> "82,2%"
export function formatUnits(value: number): string;      // 120     -> "120 un."
```

Implementadas com `Intl.NumberFormat('pt-BR', ...)`. **Nenhum** componente formata número por conta própria (sem `toFixed` espalhado).

## 7. Fluxo da tela

```
1. Usuario informa orcamento (padrao R$ 1.000,00) e parametros do AG (padroes 60/100/0.20)
2. Submit -> useStartOptimization -> POST /api/v1/optimize -> guarda task_id
3. Em paralelo:
   a. useProgressSocket abre WS /ws/v1/progress/{task_id} e alimenta ConvergenceChart
   b. useOptimizationStatus faz polling de GET /api/v1/status/{task_id}
4. status === 'COMPLETED' -> renderiza KpiCards, PurchasePlanTable,
   StrategyComparisonTable e BudgetDistributionChart
5. status === 'FAILED'    -> mensagem de erro em português, com botao de nova tentativa
```

## 8. Estados de UI obrigatórios

| Estado | Tratamento |
|---|---|
| Inicial | Formulário com valores padrão e explicação curta do que o AG faz |
| Enviando | Botão desabilitado + spinner |
| Processando | Banner com geração atual + curva crescendo ao vivo |
| WebSocket indisponível | Avisa que está acompanhando por polling; **não** mostra erro bloqueante |
| Concluído | KPIs, plano, comparativo e gráficos |
| Falha | Mensagem em português + código do erro + nova tentativa |
| Resultado vazio (nenhuma necessidade) | "Estoque suficiente para o ciclo — nenhuma compra necessária" |

## 9. Acessibilidade e responsividade

* Todo input com `<label>` associado; erro de validação ligado por `aria-describedby`.
* Tabelas com `<caption>` e `<th scope>`.
* Gráficos acompanhados de tabela equivalente (dado numérico não fica só no gráfico).
* Layout funcional a partir de 360 px; tabelas com rolagem horizontal própria.
* Contraste mínimo AA nas cores do Tailwind escolhidas.

## 10. Critérios de aceite do frontend

1. `tsc --noEmit` sem erro; sem `any` no código de produção.
2. Nenhum componente importa `fetch`/`axios` direto — tudo via `shared/api/`.
3. Os tipos da API existem em **um só** arquivo (`contracts.ts`).
4. A curva de convergência avança durante a execução (verificado em e2e com ≥ 2 mensagens).
5. Com o backend devolvendo o resultado de referência, a tela mostra: R$ 987,44 · 98,7% · 82,2% · 1 produto em risco · fitness 816,92.
6. Nenhuma feature importa de outra feature (verificado por regra de ESLint `import/no-restricted-paths`).
