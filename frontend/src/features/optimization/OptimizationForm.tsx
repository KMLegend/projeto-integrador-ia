import React, { useState } from 'react';
import { OptimizationRequest } from '../../shared/api/contracts';
import {
  defaultOptimizationFormData,
  OptimizationFormData,
  toOptimizationRequest,
  validateOptimizationForm,
  FormErrors,
} from './optimizationFormSchema';
import { Sparkles, Loader2, Sliders, DollarSign } from 'lucide-react';

interface OptimizationFormProps {
  onSubmit: (request: OptimizationRequest) => void;
  isSubmitting: boolean;
}

export const OptimizationForm: React.FC<OptimizationFormProps> = ({
  onSubmit,
  isSubmitting,
}) => {
  const [formData, setFormData] = useState<OptimizationFormData>(defaultOptimizationFormData);
  const [errors, setErrors] = useState<FormErrors>({});
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);

  const handleChange = (field: keyof OptimizationFormData, value: string) => {
    const numValue = value === '' ? 0 : Number(value);
    setFormData((prev) => ({
      ...prev,
      [field]: numValue,
    }));
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const validationErrors = validateOptimizationForm(formData);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }
    onSubmit(toOptimizationRequest(formData));
  };

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className="bg-slate-800/80 backdrop-blur border border-slate-700/60 rounded-xl p-6 shadow-xl transition-all"
    >
      <div className="flex items-center justify-between pb-4 border-b border-slate-700/60 mb-6">
        <div>
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-indigo-400" />
            Parâmetros de Reposição
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Configure o orçamento e parâmetros do Algoritmo Genético para otimizar os pedidos de compra.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
        {/* Orçamento Limite */}
        <div className="space-y-1.5">
          <label htmlFor="budget_limit" className="block text-sm font-medium text-slate-200">
            Orçamento Limite (R$) <span className="text-rose-400">*</span>
          </label>
          <div className="relative">
            <span className="absolute left-3 top-2.5 text-slate-400 font-medium">R$</span>
            <input
              id="budget_limit"
              type="number"
              step="0.01"
              min="1"
              value={formData.budget_limit || ''}
              onChange={(e) => handleChange('budget_limit', e.target.value)}
              disabled={isSubmitting}
              aria-describedby={errors.budget_limit ? 'budget_limit_error' : undefined}
              className={`w-full bg-slate-900/90 border rounded-lg pl-10 pr-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors ${
                errors.budget_limit ? 'border-rose-500 ring-1 ring-rose-500' : 'border-slate-700'
              }`}
            />
          </div>
          {errors.budget_limit && (
            <p id="budget_limit_error" role="alert" className="text-xs text-rose-400">
              {errors.budget_limit}
            </p>
          )}
        </div>

        {/* Ciclo de Reposição */}
        <div className="space-y-1.5">
          <label htmlFor="cycle_weeks" className="block text-sm font-medium text-slate-200">
            Ciclo de Reposição (semanas)
          </label>
          <input
            id="cycle_weeks"
            type="number"
            min="1"
            max="52"
            value={formData.cycle_weeks || ''}
            onChange={(e) => handleChange('cycle_weeks', e.target.value)}
            disabled={isSubmitting}
            aria-describedby={errors.cycle_weeks ? 'cycle_weeks_error' : undefined}
            className={`w-full bg-slate-900/90 border rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors ${
              errors.cycle_weeks ? 'border-rose-500 ring-1 ring-rose-500' : 'border-slate-700'
            }`}
          />
          {errors.cycle_weeks && (
            <p id="cycle_weeks_error" role="alert" className="text-xs text-rose-400">
              {errors.cycle_weeks}
            </p>
          )}
        </div>

        {/* População do AG */}
        <div className="space-y-1.5">
          <label htmlFor="population_size" className="block text-sm font-medium text-slate-200">
            População do AG
          </label>
          <input
            id="population_size"
            type="number"
            min="10"
            max="500"
            value={formData.population_size || ''}
            onChange={(e) => handleChange('population_size', e.target.value)}
            disabled={isSubmitting}
            aria-describedby={errors.population_size ? 'population_size_error' : undefined}
            className={`w-full bg-slate-900/90 border rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors ${
              errors.population_size ? 'border-rose-500 ring-1 ring-rose-500' : 'border-slate-700'
            }`}
          />
          {errors.population_size && (
            <p id="population_size_error" role="alert" className="text-xs text-rose-400">
              {errors.population_size}
            </p>
          )}
        </div>

        {/* Gerações do AG */}
        <div className="space-y-1.5">
          <label htmlFor="generations" className="block text-sm font-medium text-slate-200">
            Gerações do AG
          </label>
          <input
            id="generations"
            type="number"
            min="10"
            max="500"
            value={formData.generations || ''}
            onChange={(e) => handleChange('generations', e.target.value)}
            disabled={isSubmitting}
            aria-describedby={errors.generations ? 'generations_error' : undefined}
            className={`w-full bg-slate-900/90 border rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors ${
              errors.generations ? 'border-rose-500 ring-1 ring-rose-500' : 'border-slate-700'
            }`}
          />
          {errors.generations && (
            <p id="generations_error" role="alert" className="text-xs text-rose-400">
              {errors.generations}
            </p>
          )}
        </div>
      </div>

      {/* Advanced Parameters Toggle */}
      <div className="mb-6">
        <button
          type="button"
          onClick={() => setShowAdvanced((prev) => !prev)}
          className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center gap-1.5 focus:outline-none focus:underline"
        >
          <Sliders className="w-3.5 h-3.5" />
          {showAdvanced ? 'Ocultar parâmetros avançados do AG' : 'Configurações avançadas do AG (mutação, pais, semente)'}
        </button>

        {showAdvanced && (
          <div className="mt-4 p-4 bg-slate-900/60 border border-slate-700/50 rounded-lg grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="space-y-1">
              <label htmlFor="mutation_rate" className="block text-xs font-medium text-slate-300">
                Taxa de Mutação (0.01 - 1.0)
              </label>
              <input
                id="mutation_rate"
                type="number"
                step="0.01"
                min="0.01"
                max="1"
                value={formData.mutation_rate || ''}
                onChange={(e) => handleChange('mutation_rate', e.target.value)}
                disabled={isSubmitting}
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white"
              />
              {errors.mutation_rate && <p className="text-xs text-rose-400">{errors.mutation_rate}</p>}
            </div>

            <div className="space-y-1">
              <label htmlFor="parents_size" className="block text-xs font-medium text-slate-300">
                Pais Selecionados
              </label>
              <input
                id="parents_size"
                type="number"
                min="2"
                value={formData.parents_size || ''}
                onChange={(e) => handleChange('parents_size', e.target.value)}
                disabled={isSubmitting}
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white"
              />
              {errors.parents_size && <p className="text-xs text-rose-400">{errors.parents_size}</p>}
            </div>

            <div className="space-y-1">
              <label htmlFor="random_seed" className="block text-xs font-medium text-slate-300">
                Semente Aleatória
              </label>
              <input
                id="random_seed"
                type="number"
                value={formData.random_seed}
                onChange={(e) => handleChange('random_seed', e.target.value)}
                disabled={isSubmitting}
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white"
              />
            </div>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between pt-2">
        <span className="text-xs text-slate-400">
          Valores padrão calibrados para a simulação de 6 SKUs alimentares.
        </span>
        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-500 to-indigo-600 hover:from-indigo-600 hover:to-indigo-700 disabled:from-slate-700 disabled:to-slate-800 disabled:text-slate-400 text-white font-medium px-5 py-2.5 rounded-lg shadow-lg hover:shadow-indigo-500/20 disabled:cursor-not-allowed transition-all focus:ring-2 focus:ring-indigo-400 focus:outline-none"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Iniciando otimização...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Otimizar Reposição</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};
