import { useCallback, useEffect, useState } from 'react';
import { DatasetSummary } from '../../shared/api/contracts';
import { DatasetApi, defaultDatasetApi } from '../../shared/api/httpClient';

export interface UseDatasetsReturn {
  datasets: DatasetSummary[];
  requiredColumns: string[];
  isUploading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  upload: (file: File, reference?: string) => Promise<DatasetSummary | null>;
}

export function useDatasets(api: DatasetApi = defaultDatasetApi): UseDatasetsReturn {
  const [datasets, setDatasets] = useState<DatasetSummary[]>([]);
  const [requiredColumns, setRequiredColumns] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const body = await api.list();
      setDatasets(body.datasets);
      setRequiredColumns(body.required_columns);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao listar datasets.');
    }
  }, [api]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const upload = useCallback(
    async (file: File, reference?: string): Promise<DatasetSummary | null> => {
      setIsUploading(true);
      setError(null);
      try {
        const summary = await api.upload(file, reference);
        await refresh();
        return summary;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Falha ao enviar dataset.');
        return null;
      } finally {
        setIsUploading(false);
      }
    },
    [api, refresh]
  );

  return { datasets, requiredColumns, isUploading, error, refresh, upload };
}
