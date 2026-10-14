import '@testing-library/jest-dom';

// Mock window.URL.createObjectURL if needed
if (typeof window !== 'undefined') {
  window.URL.createObjectURL = () => '';
}
