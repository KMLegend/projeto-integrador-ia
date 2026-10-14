#!/usr/bin/env bash
set -euo pipefail

# Script de verificacao automatica de regras de Object Calisthenics
# Referencia: .context/02-padroes-de-engenharia/02-object-calisthenics.md (secao 10)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOMAIN_DIR="${ROOT_DIR}/src/domain"
APP_DIR="${ROOT_DIR}/src/application"

FAILED=0

echo "==> Verificando Regra 2: Nenhum else/elif em domain/ ou application/..."
if grep -rnE "^\s*(else:|elif )" "${DOMAIN_DIR}" "${APP_DIR}" 2>/dev/null; then
    echo "ERRO: Violacao da Regra 2 (Object Calisthenics) detectada! Nao use else/elif."
    FAILED=1
else
    echo "OK: Nenhum else/elif encontrado."
fi

echo "==> Verificando Regra 9: Nenhum @property ou getter/setter em domain/..."
if grep -rnE "@property|def get_|def set_" "${DOMAIN_DIR}" 2>/dev/null; then
    echo "ERRO: Violacao da Regra 9 (Object Calisthenics) detectada! Exponha comportamento, nao getters/setters/properties."
    FAILED=1
else
    echo "OK: Nenhum getter/setter/property encontrado."
fi

echo "==> Verificando Regra 7: Arquivos com no maximo 200 linhas em domain/..."
LONG_FILES=$(find "${DOMAIN_DIR}" -name "*.py" -exec awk 'END{if(NR>200) print FILENAME": "NR" linhas"}' {} \;)
if [ -n "${LONG_FILES}" ]; then
    echo "ERRO: Violacao da Regra 7 (Object Calisthenics) detectada! Arquivos acima de 200 linhas:"
    echo "${LONG_FILES}"
    FAILED=1
else
    echo "OK: Nenhum arquivo em domain/ excede 200 linhas."
fi

echo "==> Verificando Regra 3: Tipos primitivos em assinaturas publicas do dominio..."
PRIMITIVES=$(grep -rnE "def [a-z_]+\(self[^)]*: (int|float|str|bool)" "${DOMAIN_DIR}" 2>/dev/null | grep -v "__post_init__\|_for_serialization" || true)
if [ -n "${PRIMITIVES}" ]; then
    echo "ERRO: Violacao da Regra 3 (Object Calisthenics) detectada! Envolva primitivos em Value Objects:"
    echo "${PRIMITIVES}"
    FAILED=1
else
    echo "OK: Nao ha tipos primitivos crus expostos em assinaturas publicas."
fi

if [ "${FAILED}" -ne 0 ]; then
    echo "FAILED: Object Calisthenics checks failed."
    exit 1
fi

echo "SUCCESS: Todos os portoes de Object Calisthenics passaram!"
exit 0
