# Especificações Técnicas: Frontend (React + Node.js)

## 1. Setup e Build
*   **Ferramenta de Build:** Vite (preferencial em relação ao Create React App para melhor performance).
*   **Linguagem:** TypeScript (fortemente recomendado para tipar os retornos complexos da API de otimização).

## 2. Gerenciamento de Estado e Data Fetching
*   **Biblioteca Principal:** `@tanstack/react-query` (TanStack Query).
*   **Motivo:** Perfeito para lidar com o ciclo de vida do algoritmo. Permite fazer requisições POST para iniciar a tarefa e realizar *polling* (verificações periódicas) na rota de status caso o WebSocket falhe ou não seja utilizado, mantendo estado de *loading*, *error* e *success* cacheados.

## 3. Visualização de Dados (Data Viz)
*   **Biblioteca:** `react-plotly.js` integrado com `plotly.js`.
*   **Gráficos Necessários:**
    1.  *Curva de Convergência:* Gráfico de linha mostrando o aumento da aptidão (lucro projetado) ao longo das gerações do AG.
    2.  *Distribuição de Orçamento:* Gráfico de pizza ou barras horizontais mostrando como o orçamento final foi dividido entre os SKUs.
    3.  *Comparativo:* Histórico de Vendas vs. Demanda Prevista.

## 4. UI/UX
*   Utilizar TailwindCSS para estilização de formulários de input (Orçamento, Restrições) e cards de KPI (Lucro Máximo Projetado, Orçamento Utilizado).