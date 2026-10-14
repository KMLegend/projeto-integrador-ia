export function formatUnits(value: number): string {
  const formatted = new Intl.NumberFormat('pt-BR', {
    maximumFractionDigits: 0,
  }).format(value);
  return `${formatted} un.`;
}
