module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs', 'vite.config.ts', 'tailwind.config.js', 'postcss.config.js'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh', 'import'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    'import/no-restricted-paths': [
      'error',
      {
        zones: [
          {
            target: './src/features/optimization',
            from: './src/features',
            except: ['./optimization'],
            message: 'Features cannot import from other features.',
          },
          {
            target: './src/features/convergence',
            from: './src/features',
            except: ['./convergence'],
            message: 'Features cannot import from other features.',
          },
          {
            target: './src/features/results',
            from: './src/features',
            except: ['./results'],
            message: 'Features cannot import from other features.',
          },
        ],
      },
    ],
  },
};
