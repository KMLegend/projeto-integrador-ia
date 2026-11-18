"""Prova de equivalencia entre as duas rodadas.
Rodada 1: fitness + AG escritos a mao no notebook (Entregavel 04).
Rodada 2: mesmo calculo no dominio do sistema, construido via engenharia de prompt.
"""
import json, sys, random
sys.path.insert(0, "backend/src")

cen = json.load(open("backend/tests/fixtures/reference_scenario.json"))
itens = cen["items"]
precos = [float(i["unit_price"]) for i in itens]
necess = [int(i["required_quantity"]) for i in itens]
ORCAMENTO = float(cen["budget_limit"])

# ---------- RODADA 1: codigo do notebook, copiado sem alteracao ----------
def ajustar_ao_orcamento(solucao):
    solucao = [min(max(int(q), 0), necess[i]) for i, q in enumerate(solucao)]
    while sum(solucao[i] * precos[i] for i in range(len(solucao))) > ORCAMENTO:
        candidatos = [i for i, q in enumerate(solucao) if q > 0]
        if not candidatos:
            break
        indice = max(candidatos, key=lambda i: precos[i])
        solucao[indice] -= 1
    return solucao

def avaliar(solucao):
    solucao = ajustar_ao_orcamento(solucao)
    custo = sum(solucao[i] * precos[i] for i in range(len(solucao)))
    atendido = sum(min(solucao[i], necess[i]) for i in range(len(solucao)))
    total = sum(necess)
    pct = 100 * atendido / total if total else 100
    risco = sum(1 for i in range(len(solucao)) if solucao[i] < necess[i])
    return {"custo": custo, "atendido": atendido, "pct": pct,
            "risco": risco, "fitness": pct * 10 - risco * 5}

# ---------- RODADA 2: dominio do sistema ----------
from domain.model.budget_constraint import BudgetConstraint
from domain.model.catalog_item import CatalogItem
from domain.model.purchase_plan import PurchasePlan
from domain.model.quantity import Quantity
from domain.model.replenishment_item import ReplenishmentItem
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.model.sku import Sku
from domain.model.unit_price import UnitPrice
from domain.policy.budget_aware_plan_repair import BudgetAwarePlanRepair
from domain.policy.weighted_fitness_policy import WeightedFitnessPolicy

cenario = ReplenishmentScenario.of_items([
    ReplenishmentItem(CatalogItem(Sku(i["sku"]), UnitPrice.from_reais(i["unit_price"])),
                      Quantity.of(int(i["required_quantity"]))) for i in itens])
orcamento = BudgetConstraint.from_reais(cen["budget_limit"])
reparo = BudgetAwarePlanRepair(orcamento)
politica = WeightedFitnessPolicy.standard()

def sistema(units):
    plano = reparo.repair(PurchasePlan.of_units(tuple(units)), cenario)
    return {"plano": plano.units_for_serialization(),
            "custo": float(cenario.total_cost_of(plano).value_for_serialization()),
            "fitness": politica.evaluate(plano, cenario).fitness_value()}

print("=" * 66)
print("EQUIVALENCIA ENTRE AS DUAS RODADAS")
print("=" * 66)
casos = [("baseline do notebook", [0, 8, 0, 0, 28, 0]),
         ("plano otimo", [0, 22, 0, 0, 98, 0]),
         ("plano vazio", [0, 0, 0, 0, 0, 0]),
         ("acima da necessidade", [99, 99, 99, 99, 99, 99])]
ok = True
for nome, plano in casos:
    r1 = avaliar(list(plano)); r2 = sistema(plano)
    igual = abs(r1["fitness"] - r2["fitness"]) < 1e-6 and abs(r1["custo"] - r2["custo"]) < 0.005
    ok &= igual
    print(f"\n{nome}")
    print(f"  Rodada 1 (na mao)   fitness {r1['fitness']:10.4f}  custo R$ {r1['custo']:8.2f}")
    print(f"  Rodada 2 (prompt)   fitness {r2['fitness']:10.4f}  custo R$ {r2['custo']:8.2f}")
    print(f"  {'IDENTICO' if igual else '>>> DIVERGE <<<'}")

print("\n" + "-" * 66)
print("Teste aleatorio: 3.000 planos sorteados")
random.seed(7); div = 0
for _ in range(3000):
    p = [random.randint(0, 150) for _ in range(len(itens))]
    if abs(avaliar(list(p))["fitness"] - sistema(p)["fitness"]) > 1e-6:
        div += 1
print(f"  divergencias: {div} de 3000")
ok &= div == 0
print("\n" + "=" * 66)
print("RESULTADO:", "as duas implementacoes sao equivalentes" if ok else "HA DIVERGENCIA")
print("=" * 66)
