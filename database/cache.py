"""Cache de métricas do banco para evitar reconsultas a cada troca de aba.

Este módulo implementa:
- Cache em memória de todas as métricas agregadas
- Uma única query que retorna tudo (metricas_dashboard)
- Invalidação automática via db_manager após escritas
- Thread-safe com lock
"""

import threading

_lock = threading.Lock()
_dados = {
    "total": 0,
    "fazenda": 0,
    "outros": 0,
    "geral": 0,
    "ultima": None,
    "status": {},
    "conferencia_pendente": 0,
    "conferencia_total": 0,
    "conferencia_cpfs": 0,
    "sem_processo_cpfs": 0,
    "cpfs_totais": 0,
    "secretarias": [],
    "valido": False,
}
_db = None


def _get_db():
    """Retorna a instância do banco (criada uma única vez)."""
    global _db
    if _db is None:
        from database.db_manager import DatabaseManager
        _db = DatabaseManager()
    return _db


def _recarregar():
    """Recarrega todas as métricas do banco em uma única consulta."""
    db = _get_db()
    m = db.metricas_dashboard()
    status = db.contar_por_status()
    conferencia_pendente = db.contar_conferencia_pendentes()
    conferencia_total = db.contar_conferencia_total()
    conferencia_cpfs = db.contar_conferencia_cpfs_unicos()
    sem_processo_cpfs = db.contar_cpfs_sem_processo()
    cpfs_totais = db.contar_cpfs_totais()
    secretarias = db.contar_cpfs_por_secretaria()
    with _lock:
        _dados["total"] = m["total_pessoas"]
        _dados["fazenda"] = m["total_fazenda"]
        _dados["outros"] = m["total_outros"]
        _dados["geral"] = m["total_geral"]
        _dados["ultima"] = m["ultima_atualizacao"]
        _dados["status"] = status
        _dados["conferencia_pendente"] = conferencia_pendente
        _dados["conferencia_total"] = conferencia_total
        _dados["conferencia_cpfs"] = conferencia_cpfs
        _dados["sem_processo_cpfs"] = sem_processo_cpfs
        _dados["cpfs_totais"] = cpfs_totais
        _dados["secretarias"] = secretarias
        _dados["valido"] = True


def invalidar():
    """Marca o cache como inválido (após importações/limpezas/edições)."""
    with _lock:
        _dados["valido"] = False


def obter_metricas():
    """Retorna métricas (recarrega apenas se necessário)."""
    with _lock:
        precisa = not _dados["valido"]
    if precisa:
        _recarregar()
    with _lock:
        return dict(_dados)


def total():
    return obter_metricas()["total"]


def fazenda():
    return obter_metricas()["fazenda"]


def outros():
    return obter_metricas()["outros"]


def geral():
    return obter_metricas()["geral"]


def status():
    return obter_metricas()["status"]


def ultima():
    return obter_metricas()["ultima"]


def conferencia_pendente():
    return obter_metricas()["conferencia_pendente"]


def conferencia_total():
    return obter_metricas()["conferencia_total"]


def conferencia_cpfs():
    return obter_metricas()["conferencia_cpfs"]


def sem_processo_cpfs():
    return obter_metricas()["sem_processo_cpfs"]


def cpfs_totais():
    return obter_metricas()["cpfs_totais"]


def secretarias():
    return obter_metricas()["secretarias"]
