import re
import sqlite3
import os
import threading
from datetime import datetime

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "paritarios.db",
)


def _invalidar_cache_externo():
    """Invalida o cache de métricas após operações de escrita (silencioso em caso de ciclo)."""
    try:
        from database import cache as _cache
        _cache.invalidar()
    except Exception:
        pass


class DatabaseManager:
    """Gerenciador do banco SQLite com cache de conexão e índices otimizados."""

    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        # Conexão única reusada (thread-safe via lock)
        self._local = threading.local()
        self._init_db()

    # ====================================================== Conexão
    def _get_conn(self):
        """Retorna uma conexão por thread (cached)."""
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10)
            conn.row_factory = sqlite3.Row
            # WAL + cache + memória temporária = leituras muito mais rápidas
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA cache_size=-20000")  # ~20MB de cache
            self._local.conn = conn
        return conn

    # ====================================================== Inicialização
    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pessoas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpf TEXT UNIQUE NOT NULL,
                    rg TEXT,
                    nome TEXT NOT NULL,
                    matricula TEXT,
                    status TEXT,
                    origem_info TEXT,
                    lista_apeo TEXT,
                    especificidade TEXT,
                    processos_fazenda TEXT,
                    processos_outros TEXT,
                    qtdade_processos_fazenda INTEGER DEFAULT 0,
                    qtdade_processos_outros INTEGER DEFAULT 0,
                    qtdade_total_processos INTEGER DEFAULT 0,
                    status_coleta_processos TEXT,
                    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    chave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL
                )
            """)
            conn.execute("""
                INSERT OR IGNORE INTO config (chave, valor) VALUES ('admin_senha', 'admin123')
            """)
            # Índices para acelerar as consultas mais usadas
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pessoas_cpf_digits ON pessoas(REPLACE(REPLACE(cpf,'.',''),'-',''))")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pessoas_nome ON pessoas(nome COLLATE NOCASE)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pessoas_status ON pessoas(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pessoas_atualizacao ON pessoas(data_atualizacao)")

            # Processos para conferência: um processo por linha, várias linhas por CPF
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processos_conferencia (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpf TEXT NOT NULL,
                    nome TEXT,
                    rg TEXT,
                    processo TEXT NOT NULL,
                    secretaria TEXT NOT NULL,
                    cumprido INTEGER NOT NULL DEFAULT 0,
                    data_importacao TEXT DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(cpf, processo, secretaria)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conferencia_cpf ON processos_conferencia(cpf)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conferencia_secretaria ON processos_conferencia(secretaria)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conferencia_cumprido ON processos_conferencia(cumprido)")

            # CPFs sem processo vinculado (planilhas de conferência sem coluna 'processo')
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cpfs_sem_processo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpf TEXT NOT NULL,
                    nome TEXT,
                    rg TEXT,
                    secretaria TEXT NOT NULL,
                    data_importacao TEXT DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(cpf, secretaria)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sem_processo_cpf ON cpfs_sem_processo(cpf)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sem_processo_secretaria ON cpfs_sem_processo(secretaria)")

            # Ações coletivas cadastradas (tela inicial)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS acoes_coletivas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_processo TEXT UNIQUE NOT NULL,
                    titulo TEXT NOT NULL,
                    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                INSERT OR IGNORE INTO acoes_coletivas (numero_processo, titulo)
                VALUES ('0035864-57.2011.8.26.0053', 'Apeoesp - Recálculo Sexta Parte')
            """)
            conn.commit()

    # ====================================================== Config
    def get_admin_senha(self):
        with self._get_conn() as conn:
            row = conn.execute("SELECT valor FROM config WHERE chave = 'admin_senha'").fetchone()
            return row["valor"] if row else "admin123"

    def set_admin_senha(self, nova_senha):
        with self._get_conn() as conn:
            conn.execute("UPDATE config SET valor = ? WHERE chave = 'admin_senha'", (nova_senha,))
            conn.commit()

    # ====================================================== CRUD
    def inserir_pessoa(self, dados):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO pessoas (
                    cpf, rg, nome, matricula, status, origem_info, lista_apeo,
                    especificidade, processos_fazenda, processos_outros,
                    qtdade_processos_fazenda, qtdade_processos_outros,
                    qtdade_total_processos, status_coleta_processos,
                    data_atualizacao
                ) VALUES (
                    :cpf, :rg, :nome, :matricula, :status, :origem_info, :lista_apeo,
                    :especificidade, :processos_fazenda, :processos_outros,
                    :qtdade_processos_fazenda, :qtdade_processos_outros,
                    :qtdade_total_processos, :status_coleta_processos,
                    :data_atualizacao
                )
            """, {**dados, "data_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            conn.commit()
        _invalidar_cache_externo()

    def atualizar_pessoa(self, cpf, dados):
        with self._get_conn() as conn:
            sets = []
            params = {}
            for key, value in dados.items():
                if key != "cpf":
                    sets.append(f"{key} = :{key}")
                    params[key] = value
            sets.append("data_atualizacao = :data_atualizacao")
            params["data_atualizacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            params["cpf"] = cpf
            sql = f"UPDATE pessoas SET {', '.join(sets)} WHERE cpf = :cpf"
            conn.execute(sql, params)
            conn.commit()
            return conn.total_changes
        _invalidar_cache_externo()

    def deletar_pessoa(self, cpf):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM pessoas WHERE cpf = :cpf", {"cpf": cpf})
            conn.commit()
            return conn.total_changes
        _invalidar_cache_externo()

    def buscar_por_cpf(self, cpf):
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM pessoas WHERE cpf = :cpf", {"cpf": cpf}).fetchone()
            return dict(row) if row else None

    def buscar_por_cpf_flexivel(self, cpf):
        """Busca otimizada: índice em cpf_digits faz o trabalho."""
        digitos = re.sub(r"\D", "", cpf or "")
        if not digitos:
            return None
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM pessoas WHERE REPLACE(REPLACE(cpf,'.',''),'-','') = :d",
                {"d": digitos},
            ).fetchone()
            return dict(row) if row else None

    def ultima_atualizacao(self):
        with self._get_conn() as conn:
            row = conn.execute("SELECT MAX(data_atualizacao) AS ultima FROM pessoas").fetchone()
            return row["ultima"] if row else None

    def buscar_por_nome(self, nome, limite=30):
        """Busca por nome com índice COLLATE NOCASE."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT cpf, nome, status FROM pessoas WHERE nome LIKE :nome ORDER BY nome LIMIT :limite",
                {"nome": f"%{nome}%", "limite": limite},
            ).fetchall()
            return [dict(r) for r in rows]

    def listar_todos(self, offset=0, limit=100):
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM pessoas ORDER BY nome LIMIT :limit OFFSET :offset",
                {"limit": limit, "offset": offset},
            ).fetchall()
            return [dict(r) for r in rows]

    # ====================================================== Agregações
    def metricas_dashboard(self):
        """Retorna todas as métricas em UMA única query — mais rápido que várias."""
        with self._get_conn() as conn:
            row = conn.execute("""
                SELECT
                    (SELECT COUNT(*) FROM pessoas) AS total_pessoas,
                    (SELECT COALESCE(SUM(qtdade_processos_fazenda),0) FROM pessoas) AS total_fazenda,
                    (SELECT COALESCE(SUM(qtdade_processos_outros),0) FROM pessoas) AS total_outros,
                    (SELECT COALESCE(SUM(qtdade_total_processos),0) FROM pessoas) AS total_geral,
                    (SELECT MAX(data_atualizacao) FROM pessoas) AS ultima_atualizacao
            """).fetchone()
            return dict(row)

    def contar_total(self):
        with self._get_conn() as conn:
            row = conn.execute("SELECT COUNT(*) as total FROM pessoas").fetchone()
            return row["total"]

    def contar_por_status(self):
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT status, COUNT(*) as total
                FROM pessoas
                WHERE status IS NOT NULL AND status != ''
                GROUP BY status
                ORDER BY total DESC
            """).fetchall()
            return {row["status"]: row["total"] for row in rows}

    def total_processos_fazenda(self):
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT COALESCE(SUM(qtdade_processos_fazenda), 0) as total FROM pessoas"
            ).fetchone()
            return row["total"]

    def total_processos_outros(self):
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT COALESCE(SUM(qtdade_processos_outros), 0) as total FROM pessoas"
            ).fetchone()
            return row["total"]

    def total_processos_geral(self):
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT COALESCE(SUM(qtdade_total_processos), 0) as total FROM pessoas"
            ).fetchone()
            return row["total"]

    def ultimas_importacoes(self, limite=5):
        return []

    def atividades_recentes(self, limite=5):
        return []

    # ====================================================== Backup
    def backup(self):
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM pessoas ORDER BY cpf").fetchall()
            return [dict(r) for r in rows]

    def restore(self, dados):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM pessoas")
            conn.executemany("""
                INSERT INTO pessoas (
                    cpf, rg, nome, matricula, status, origem_info, lista_apeo,
                    especificidade, processos_fazenda, processos_outros,
                    qtdade_processos_fazenda, qtdade_processos_outros,
                    qtdade_total_processos, status_coleta_processos
                ) VALUES (
                    :cpf, :rg, :nome, :matricula, :status, :origem_info, :lista_apeo,
                    :especificidade, :processos_fazenda, :processos_outros,
                    :qtdade_processos_fazenda, :qtdade_processos_outros,
                    :qtdade_total_processos, :status_coleta_processos
                )
            """, dados)
            conn.commit()
        _invalidar_cache_externo()

    def limpar_todos(self):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM pessoas")
            conn.commit()
        _invalidar_cache_externo()

    def inserir_varios(self, dados_lista):
        if not dados_lista:
            return
        with self._get_conn() as conn:
            conn.execute("PRAGMA synchronous = OFF")
            conn.executemany("""
                INSERT OR REPLACE INTO pessoas (
                    cpf, rg, nome, matricula, status, origem_info, lista_apeo,
                    especificidade, processos_fazenda, processos_outros,
                    qtdade_processos_fazenda, qtdade_processos_outros,
                    qtdade_total_processos, status_coleta_processos,
                    data_atualizacao
                ) VALUES (
                    :cpf, :rg, :nome, :matricula, :status, :origem_info, :lista_apeo,
                    :especificidade, :processos_fazenda, :processos_outros,
                    :qtdade_processos_fazenda, :qtdade_processos_outros,
                    :qtdade_total_processos, :status_coleta_processos,
                    :data_atualizacao
                )
            """, dados_lista)
            conn.commit()
        _invalidar_cache_externo()

    # ====================================================== Processos p/ Conferência
    def inserir_processos_conferencia(self, dados_lista):
        """Upsert em lote. Preserva o status 'cumprido' já marcado em reimportações."""
        if not dados_lista:
            return
        with self._get_conn() as conn:
            conn.execute("PRAGMA synchronous = OFF")
            conn.executemany("""
                INSERT INTO processos_conferencia (
                    cpf, nome, rg, processo, secretaria, data_atualizacao
                ) VALUES (
                    :cpf, :nome, :rg, :processo, :secretaria, :data_atualizacao
                )
                ON CONFLICT(cpf, processo, secretaria) DO UPDATE SET
                    nome = excluded.nome,
                    rg = excluded.rg,
                    data_atualizacao = excluded.data_atualizacao
            """, dados_lista)
            conn.commit()
        _invalidar_cache_externo()

    def marcar_conferencia_cumprido(self, id_registro, cumprido):
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE processos_conferencia SET cumprido = :cumprido, data_atualizacao = :data WHERE id = :id",
                {"cumprido": 1 if cumprido else 0, "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "id": id_registro},
            )
            conn.commit()
        _invalidar_cache_externo()

    def listar_conferencia_por_cpf(self, cpf):
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM processos_conferencia WHERE cpf = :cpf ORDER BY secretaria, processo",
                {"cpf": cpf},
            ).fetchall()
            return [dict(r) for r in rows]

    def contar_conferencia_pendentes(self):
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) as total FROM processos_conferencia WHERE cumprido = 0"
            ).fetchone()
            return row["total"]

    def contar_conferencia_total(self):
        with self._get_conn() as conn:
            row = conn.execute("SELECT COUNT(*) as total FROM processos_conferencia").fetchone()
            return row["total"]

    def contar_conferencia_cpfs_unicos(self):
        with self._get_conn() as conn:
            row = conn.execute("SELECT COUNT(DISTINCT cpf) as total FROM processos_conferencia").fetchone()
            return row["total"]

    def inserir_cpfs_sem_processo(self, dados_lista):
        if not dados_lista:
            return
        with self._get_conn() as conn:
            conn.execute("PRAGMA synchronous = OFF")
            conn.executemany("""
                INSERT INTO cpfs_sem_processo (
                    cpf, nome, rg, secretaria, data_atualizacao
                ) VALUES (
                    :cpf, :nome, :rg, :secretaria, :data_atualizacao
                )
                ON CONFLICT(cpf, secretaria) DO UPDATE SET
                    nome = excluded.nome,
                    rg = excluded.rg,
                    data_atualizacao = excluded.data_atualizacao
            """, dados_lista)
            conn.commit()
        _invalidar_cache_externo()

    def contar_cpfs_sem_processo(self):
        with self._get_conn() as conn:
            row = conn.execute("SELECT COUNT(DISTINCT cpf) as total FROM cpfs_sem_processo").fetchone()
            return row["total"]

    # ====================================================== Ações Coletivas
    def listar_acoes_coletivas(self):
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM acoes_coletivas ORDER BY data_cadastro"
            ).fetchall()
            return [dict(r) for r in rows]

    def inserir_acao_coletiva(self, numero_processo, titulo):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO acoes_coletivas (numero_processo, titulo) VALUES (:numero, :titulo)",
                {"numero": numero_processo, "titulo": titulo},
            )
            conn.commit()

    def contar_cpfs_totais(self):
        """CPFs únicos no total, somando os com e sem processo vinculado."""
        with self._get_conn() as conn:
            row = conn.execute("""
                SELECT COUNT(DISTINCT cpf) as total FROM (
                    SELECT cpf FROM processos_conferencia
                    UNION
                    SELECT cpf FROM cpfs_sem_processo
                )
            """).fetchone()
            return row["total"]

    def contar_cpfs_por_secretaria(self):
        """CPFs únicos por secretaria: total combinado, com processo e sem processo.

        Retorna lista de tuplas (secretaria, total, com_processo, sem_processo)
        ordenada por total decrescente.
        """
        with self._get_conn() as conn:
            total_rows = conn.execute("""
                SELECT secretaria, COUNT(DISTINCT cpf) as total FROM (
                    SELECT cpf, secretaria FROM processos_conferencia
                    UNION
                    SELECT cpf, secretaria FROM cpfs_sem_processo
                )
                GROUP BY secretaria
            """).fetchall()
            com_rows = conn.execute(
                "SELECT secretaria, COUNT(DISTINCT cpf) as total FROM processos_conferencia GROUP BY secretaria"
            ).fetchall()
            sem_rows = conn.execute(
                "SELECT secretaria, COUNT(DISTINCT cpf) as total FROM cpfs_sem_processo GROUP BY secretaria"
            ).fetchall()

        com_map = {r["secretaria"]: r["total"] for r in com_rows}
        sem_map = {r["secretaria"]: r["total"] for r in sem_rows}

        resultado = [
            (r["secretaria"], r["total"], com_map.get(r["secretaria"], 0), sem_map.get(r["secretaria"], 0))
            for r in total_rows
        ]
        resultado.sort(key=lambda x: x[1], reverse=True)
        return resultado
