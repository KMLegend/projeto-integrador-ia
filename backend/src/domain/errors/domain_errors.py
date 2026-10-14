class DomainError(Exception):
    """Excecao base para todos os erros de dominio."""


class InvalidMoneyError(DomainError):
    """Lancado quando um valor monetario e invalido (ex: float)."""


class NegativeMoneyError(DomainError):
    """Lancado quando uma quantia monetaria e negativa."""


class NegativeQuantityError(DomainError):
    """Lancado quando uma quantidade de itens e negativa."""


class InvalidSkuError(DomainError):
    """Lancado quando um SKU e vazio ou invalido."""


class InvalidPercentageError(DomainError):
    """Lancado quando um percentual e invalido."""


class InvalidPositionError(DomainError):
    """Lancado quando uma posicao no vetor e invalida."""


class EmptyPositionError(DomainError):
    """Lancado ao tentar acessar o valor de MaybePosition ausente."""


class InvalidBudgetError(DomainError):
    """Lancado quando o orcamento limite e menor ou igual a zero."""


class InvalidCycleError(DomainError):
    """Lancado quando as semanas do ciclo de reposicao sao menores que 1."""


class InvalidParametersError(DomainError):
    """Lancado quando os parametros do algoritmo genetico sao invalidos."""


class TaskNotFoundError(DomainError):
    """Lancado quando uma tarefa de otimizacao nao e encontrada."""


class ModelNotAvailableError(DomainError):
    """Lancado quando o modelo de previsao nao esta disponivel."""


class UnknownDatasetError(DomainError):
    """Lancado quando uma referencia de dataset nao e reconhecida (D-07)."""
