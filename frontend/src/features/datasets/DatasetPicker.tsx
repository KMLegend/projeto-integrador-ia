import React, { useRef, useState } from 'react';
import { Database, Upload } from 'lucide-react';
import { DatasetSummary } from '../../shared/api/contracts';

export interface DatasetPickerProps {
  datasets: DatasetSummary[];
  requiredColumns: string[];
  selected: string;
  isUploading: boolean;
  error: string | null;
  onSelect: (reference: string) => void;
  onUpload: (file: File) => void;
}

function describe(dataset: DatasetSummary): string {
  if (dataset.is_builtin) {
    return `${dataset.reference} — embutido (${dataset.rows} registros, ${dataset.skus} SKUs)`;
  }
  return `${dataset.reference} — ${dataset.rows} registros, ${dataset.skus} SKUs`;
}

export const DatasetPicker: React.FC<DatasetPickerProps> = ({
  datasets,
  requiredColumns,
  selected,
  isUploading,
  error,
  onSelect,
  onUpload,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [showSchema, setShowSchema] = useState(false);

  const handleFile = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onUpload(file);
    }
    event.target.value = '';
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
        <div className="flex-1">
          <label
            htmlFor="dataset-select"
            className="mb-1 flex items-center gap-2 text-sm font-medium text-slate-300"
          >
            <Database className="h-4 w-4" aria-hidden="true" />
            Base de Dados
          </label>
          <select
            id="dataset-select"
            value={selected}
            onChange={(event) => onSelect(event.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100 focus:border-indigo-500 focus:outline-none"
          >
            {datasets.map((dataset) => (
              <option key={dataset.reference} value={dataset.reference}>
                {describe(dataset)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <input
            ref={inputRef}
            type="file"
            accept=".csv,text/csv"
            onChange={handleFile}
            className="hidden"
            aria-label="Arquivo CSV do dataset"
          />
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            disabled={isUploading}
            className="flex w-full items-center justify-center gap-2 rounded-lg border border-indigo-500/40 bg-indigo-500/10 px-4 py-2 text-sm font-medium text-indigo-300 hover:bg-indigo-500/20 disabled:opacity-50 sm:w-auto"
          >
            <Upload className="h-4 w-4" aria-hidden="true" />
            {isUploading ? 'Enviando…' : 'Enviar CSV'}
          </button>
        </div>
      </div>

      <button
        type="button"
        onClick={() => setShowSchema((value) => !value)}
        className="text-xs text-indigo-400 hover:text-indigo-300"
        aria-expanded={showSchema}
      >
        {showSchema ? 'Ocultar' : 'Ver'} colunas obrigatórias do CSV
      </button>

      {showSchema && (
        <p className="rounded-lg bg-slate-800/60 p-3 font-mono text-xs text-slate-400">
          {requiredColumns.join(', ')}
        </p>
      )}

      {error && (
        <p role="alert" className="rounded-lg bg-red-500/10 p-3 text-sm text-red-300">
          {error}
        </p>
      )}
    </div>
  );
};
