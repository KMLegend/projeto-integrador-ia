export function formatPercentage(value: number): string {
  const formatted = new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value);
  return `${formatted}%`;
}
