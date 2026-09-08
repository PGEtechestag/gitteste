"""Histórico persistente de consultas, importações e atividades do sistema.

Os dados são guardados em JSON dentro da pasta data/, junto do banco SQLite.
Implementação com cache em memória para acesso instantâneo.
"""

import json
import os
import threading
from datetime import datetime

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data",
)
ARQ_CONSULTAS = os.path.join(DATA_DIR, "consultas_recentes.json")
ARQ_EVENTOS = os.path.join(DATA_DIR, "eventos.json")

MAX_CONSULTAS = 30
MAX_EVENTOS = 60

_cache = {"consultas": None, "eventos": None, "mtime_consultas": 0, "mtime_eventos": 0}
_lock = threading.Lock()


def _mtime(caminho):
    try:
        return os.path.getmtime(caminho)
    except OSError:
        return 0


def _carregar(caminho, chave_cache):
    """Carrega lista do disco com cache em memória."""
    mt = _mtime(caminho)
    cached = _cache.get(chave_cache)
    cache_mt = _cache.get(f"mtime_{chave_cache}", 0)
    if cached is not None and mt == cache_mt and mt > 0:
        return cached
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        dados = dados if isinstance(dados, list) else []
    except (OSError, ValueError):
        dados = []
    _cache[chave_cache] = dados
    _cache[f"mtime_{chave_cache}"] = mt
    return dados


def _salvar(caminho, lista, chave_cache):
    """Salva lista no disco e atualiza cache."""
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = caminho + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False)
        os.replace(tmp, caminho)
    except OSError:
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(lista, f, ensure_ascii=False)
        except OSError:
            return
    _cache[chave_cache] = lista
    _cache[f"mtime_{chave_cache}"] = _mtime(caminho)


def _agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ------------------------------------------------------------- Consultas
def registrar_consulta(cpf, nome):
    if not cpf:
        return
    with _lock:
        lista = [c for c in _carregar(ARQ_CONSULTAS, "consultas") if c.get("cpf") != cpf]
        lista.insert(0, {"cpf": cpf, "nome": nome or "", "ts": _agora()})
        _salvar(ARQ_CONSULTAS, lista[:MAX_CONSULTAS], "consultas")


def obter_consultas(limite=None):
    lista = _carregar(ARQ_CONSULTAS, "consultas")
    return lista[:limite] if limite else lista


# --------------------------------------------------------------- Eventos
def registrar_evento(tipo, titulo, detalhe=""):
    with _lock:
        eventos = _carregar(ARQ_EVENTOS, "eventos")
        eventos.insert(0, {"tipo": tipo, "titulo": titulo, "detalhe": detalhe, "ts": _agora()})
        _salvar(ARQ_EVENTOS, eventos[:MAX_EVENTOS], "eventos")


def obter_eventos(tipo=None, limite=None):
    eventos = _carregar(ARQ_EVENTOS, "eventos")
    if tipo:
        eventos = [e for e in eventos if e.get("tipo") == tipo]
    return eventos[:limite] if limite else eventos


def invalidar_cache():
    """Limpa o cache (use após operações externas que mudem os arquivos)."""
    _cache["consultas"] = None
    _cache["eventos"] = None
    _cache["mtime_consultas"] = 0
    _cache["mtime_eventos"] = 0


# ----------------------------------------------------------------- Utils
def tempo_relativo(ts_str):
    try:
        ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return ""
    delta = datetime.now() - ts
    segundos = int(delta.total_seconds())
    if segundos < 60:
        return "agora mesmo"
    minutos = segundos // 60
    if minutos < 60:
        return f"há {minutos} min"
    horas = minutos // 60
    if horas < 24:
        return f"há {horas} hora" + ("s" if horas > 1 else "")
    dias = horas // 24
    if dias < 30:
        return f"há {dias} dia" + ("s" if dias > 1 else "")
    return ts.strftime("%d/%m/%Y")


def mascarar_cpf(cpf):
    d = "".join(ch for ch in str(cpf or "") if ch.isdigit())[:11]
    partes = [d[:3], d[3:6], d[6:9], d[9:11]]
    return ".".join(partes[:3]) + ("-" + partes[3] if partes[3] else "")
