import { describe, it, expect } from 'vitest';
import { formatCurrency } from '../currency';
import { formatPercentage } from '../percentage';
import { formatUnits } from '../units';

describe('Formatadores pt-BR', () => {
  it('formata moeda no padrao brasileiro', () => {
    const formatted = formatCurrency(987.44);
    // Replace non-breaking space with regular space for stable assertion
    const normalized = formatted.replace(/\u00a0/g, ' ');
    expect(normalized).toBe('R$ 987,44');
  });

  it('formata porcentagem com uma casa decimal', () => {
    expect(formatPercentage(82.1917)).toBe('82,2%');
    expect(formatPercentage(98.7)).toBe('98,7%');
    expect(formatPercentage(0)).toBe('0,0%');
  });

  it('formata unidades com sufixo un.', () => {
    expect(formatUnits(120)).toBe('120 un.');
    expect(formatUnits(0)).toBe('0 un.');
  });
});
