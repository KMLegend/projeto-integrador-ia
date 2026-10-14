# Visão Geral da Arquitetura: Sistema de Otimização de Estoque com IA

## 1. Propósito do Sistema
Sistema baseado em Algoritmos Genéticos (AG) e Machine Learning (ML) para otimização de compras de estoque. O sistema processa históricos de vendas, projeta a demanda futura e utiliza computação evolutiva para sugerir a melhor lista de compras, respeitando restrições de orçamento.

## 2. Padrão Arquitetural
Aplica-se o padrão de Microsserviços e Processamento Assíncrono para separar a interface interativa do processamento matemático intensivo.

## 3. Stack Tecnológica
*   **Frontend:** React, Vite, Node.js (Ambiente), TailwindCSS, TanStack Query (React Query), react-plotly.js.
*   **Backend (API):** Python 3.11+, FastAPI (REST + WebSockets), Uvicorn.
*   **Processamento Assíncrono:** Celery (Workers), Redis (Message Broker e Result Backend).
*   **IA e Ciência de Dados:** DEAP ou PyGAD (Algoritmo Genético), Prophet/Scikit-Learn (Previsão de Demanda), Pandas/NumPy (ETL e manipulação de matrizes).
*   **Infraestrutura:** Docker e Docker Compose.

## 4. Fluxo de Dados (Data Flow)
1.  Usuário define parâmetros (ex: Orçamento) no **Frontend**.
2.  Frontend envia requisição POST via REST para a **API (FastAPI)**.
3.  API cria um ID de tarefa e envia os dados para a fila do **Redis**.
4.  Um **Worker (Celery)** consome a mensagem do Redis e inicia a execução do Algoritmo Genético.
5.  Frontend abre conexão **WebSocket** com a API para escutar o progresso (Geração atual, fitness máximo).
6.  Worker finaliza, salva o resultado no Redis. Frontend recebe notificação e busca o JSON final com os melhores cenários de compra.