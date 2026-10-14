# Contratos de Integração (API Contracts)

Esta documentação serve para alinhar as chamadas HTTP entre o Frontend e o Backend.

## 1. Iniciar Otimização
*   **Endpoint:** `POST /api/v1/optimize`
*   **Descrição:** Envia os parâmetros iniciais e aciona o Worker no background.
*   **Payload de Entrada (JSON):**
    ```json
    {
      "budget_limit": 50000.00,
      "dataset_reference": "historico_mensal_v1",
      "ga_parameters": {
        "population_size": 100,
        "generations": 50
      }
    }
    ```
*   **Resposta (202 Accepted):**
    ```json
    {
      "task_id": "abc123xyz-890",
      "status": "PROCESSING",
      "message": "Algoritmo genético iniciado em background."
    }
    ```

## 2. Consultar Status/Resultado
*   **Endpoint:** `GET /api/v1/status/{task_id}`
*   **Descrição:** Usado pelo React Query para verificar se o AG terminou.
*   **Resposta (Processando):**
    ```json
    { "task_id": "abc123xyz-890", "status": "PROCESSING", "result": null }
    ```
*   **Resposta (Concluído):**
    ```json
    {
      "task_id": "abc123xyz-890",
      "status": "COMPLETED",
      "result": {
        "best_scenario_summary": {
          "total_cost": 49850.00,
          "projected_profit": 15200.00
        },
        "items_to_buy": [
          {"sku": "ITEM-A", "quantity": 150, "unit_cost": 100.00},
          {"sku": "ITEM-B", "quantity": 30, "unit_cost": 250.00}
        ]
      }
    }
    ```

## 3. WebSocket para Progresso
*   **Endpoint:** `WS /ws/v1/progress/{task_id}`
*   **Mensagens Emitidas pelo Servidor (JSON):**
    ```json
    {
      "generation": 15,
      "max_fitness": 12500.00,
      "status": "evolving"
    }
    ```