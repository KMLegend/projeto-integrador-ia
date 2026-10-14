import React, { useState } from 'react';
import { OptimizationRequest } from './shared/api/contracts';
import { OptimizationForm } from './features/optimization/OptimizationForm';
import { useStartOptimization } from './features/optimization/useStartOptimization';
import { useOptimizationStatus } from './features/optimization/useOptimizationStatus';
import { ProgressBanner } from './features/convergence/ProgressBanner';
import { ConvergenceChart } from './features/convergence/ConvergenceChart';
import { useProgressSocket } from './features/convergence/useProgressSocket';
import { KpiCards } from './features/results/KpiCards';
import { PurchasePlanTable } from './features/results/PurchasePlanTable';
import { StrategyComparisonTable } from './features/results/StrategyComparisonTable';
import { BudgetDistributionChart } from './features/results/BudgetDistributionChart';
import { DemandVsPurchasedChart } from './features/results/DemandVsPurchasedChart';
import {
  Boxes,
  RotateCcw,
  AlertOctagon,
  CheckCircle,
  Sparkles,
} from 'lucide-react';

interface AppProps {
  initialTaskId?: string | null;
}

export const App: React.FC<AppProps> = ({ initialTaskId = null }) => {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(initialTaskId);
  const [submittedRequest, setSubmittedRequest] = useState<OptimizationRequest | null>(null);

  const startMutation = useStartOptimization();
  const statusQuery = useOptimizationStatus(activeTaskId);
  const effectiveTaskId = activeTaskId || statusQuery.data?.task_id || null;
  const {
    points: socketPoints,
    isSocketFailed,
    status: socketStatus,
    currentGeneration,
  } = useProgressSocket(effectiveTaskId);

  const handleStart = async (request: OptimizationRequest) => {
    setSubmittedRequest(request);
    try {
      const response = await startMutation.mutateAsync(request);
      setActiveTaskId(response.task_id);
    } catch {
      // Error is captured by mutation state
    }
  };

  const handleReset = () => {
    setActiveTaskId(null);
    setSubmittedRequest(null);
    startMutation.reset();
  };

  // Derive consolidated status
  const isCompleted = statusQuery.data?.status === 'COMPLETED';
  const isFailed = statusQuery.data?.status === 'FAILED' || startMutation.isError;
  const isProcessing =
    Boolean(effectiveTaskId) &&
    !isCompleted &&
    !isFailed &&
    (statusQuery.data?.status === 'PROCESSING' || socketStatus === 'evolving');

  const bannerStatus: 'idle' | 'evolving' | 'completed' | 'failed' = isProcessing
    ? 'evolving'
    : isCompleted
    ? 'completed'
    : isFailed
    ? 'failed'
    : 'idle';

  const result = statusQuery.data?.result;
  const totalGenerations = submittedRequest?.ga_parameters?.generations || 100;

  // Combine points: use final result curve if available, otherwise socket live points
  const convergencePoints =
    result?.convergence_curve && result.convergence_curve.length > 0
      ? result.convergence_curve
      : socketPoints;

  const isZeroNeed =
    isCompleted &&
    result &&
    (result.best_scenario_summary.required_total === 0 ||
      result.items_to_buy.length === 0);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col antialiased">
      {/* Top Header */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-indigo-600 text-white shadow-lg shadow-indigo-500/30">
              <Boxes className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-base sm:text-lg font-bold text-white tracking-tight flex items-center gap-2">
                Otimização Preditiva de Estoque
                <span className="hidden sm:inline-flex items-center gap-1 text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  <Sparkles className="w-2.5 h-2.5" /> IA Híbrida
                </span>
              </h1>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Regressão Linear Multivariada + Algoritmo Genético Multiobjetivo
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {activeTaskId && (
              <button
                onClick={handleReset}
                className="inline-flex items-center gap-1.5 text-xs text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 px-3 py-1.5 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Nova Otimização</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* State 1 & 2: Form */}
        <section aria-label="Configuração dos Parâmetros">
          <OptimizationForm
            onSubmit={handleStart}
            isSubmitting={startMutation.isPending || (isProcessing && socketPoints.length === 0)}
          />
        </section>

        {/* State 6: Error Banner */}
        {isFailed && (
          <section
            role="alert"
            className="bg-rose-950/40 border border-rose-500/50 rounded-xl p-6 shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
          >
            <div className="flex items-start gap-3">
              <div className="p-2 bg-rose-500/20 text-rose-400 rounded-lg">
                <AlertOctagon className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-rose-200">
                  Falha ao executar otimização
                </h3>
                <p className="text-sm text-rose-300 mt-1">
                  {statusQuery.data?.error?.message ||
                    startMutation.error?.message ||
                    'Não foi possível concluir o processo de otimização de estoque.'}
                </p>
                {statusQuery.data?.error?.code && (
                  <span className="inline-block mt-2 text-xs font-mono bg-rose-900/60 text-rose-300 px-2 py-0.5 rounded border border-rose-700/50">
                    Código: {statusQuery.data.error.code}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={() => submittedRequest && handleStart(submittedRequest)}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-medium rounded-lg transition-colors shadow-lg shadow-rose-600/20"
            >
              <RotateCcw className="w-4 h-4" />
              Tentar novamente
            </button>
          </section>
        )}

        {/* State 3 & 4: Processing Banner & Real-time Convergence */}
        {effectiveTaskId && !isFailed && (
          <section aria-label="Progresso da Otimização">
            <ProgressBanner
              status={bannerStatus}
              currentGeneration={currentGeneration}
              totalGenerations={totalGenerations}
              isSocketFailed={isSocketFailed}
            />

            {/* Live Convergence Curve during processing or if completed */}
            <div className="mt-6">
              <ConvergenceChart
                points={convergencePoints}
                isLive={isProcessing}
              />
            </div>
          </section>
        )}

        {/* State 7: Empty Result (Sufficient Stock / No Needs) */}
        {isZeroNeed && (
          <section className="bg-slate-800/80 border border-emerald-500/40 rounded-xl p-8 shadow-xl text-center">
            <div className="w-12 h-12 bg-emerald-500/20 text-emerald-400 rounded-full mx-auto flex items-center justify-center mb-4">
              <CheckCircle className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white">
              Estoque suficiente para o ciclo — nenhuma compra necessária
            </h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-2">
              Todas as demandas previstas para as próximas semanas já estão plenamente cobertas pelo estoque atual dos produtos.
            </p>
          </section>
        )}

        {/* State 5: Completed Results Dashboard */}
        {isCompleted && result && !isZeroNeed && (
          <section aria-label="Resultados da Otimização" className="space-y-8 animate-fadeIn">
            {/* KPI Cards */}
            <KpiCards
              summary={result.best_scenario_summary}
              modelMae={result.model_metrics.mae}
            />

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <BudgetDistributionChart lines={result.items_to_buy} />
              <DemandVsPurchasedChart lines={result.items_to_buy} />
            </div>

            {/* Tables Grid */}
            <div className="space-y-6">
              <PurchasePlanTable lines={result.items_to_buy} />
              <StrategyComparisonTable comparison={result.baseline_comparison} />
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/60 py-6 mt-12 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4">
          <p>
            Projeto Integrador — Inteligência Artificial Aplicada à Cadeia de Suprimentos
          </p>
          <p className="mt-1 text-slate-400">
            Aviso de Conformidade (RN-09): Os dados de estoque e demanda são sintetizados e calibrados exclusivamente para fins de simulação e avaliação acadêmica.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;
