import pandas as pd
import os
from datetime import datetime
from database.db_manager import DatabaseManager

db = DatabaseManager()

COLUNAS_ESPERADAS = [
    "nome", "rg", "cpf", "matricula", "status", "origem_info",
    "lista_apeo", "especificidade", "processos_fazenda", "processos_outros",
    "qtdade_processos_fazenda", "qtdade_processos_outros",
    "qtdade_total_processos", "status_coleta_processos"
]

def importar_excel(caminho_arquivo, callback_progresso=None):
    try:
        df = pd.read_excel(caminho_arquivo, sheet_name=0)
        df.columns = [c.strip().lower() for c in df.columns]

        faltantes = [c for c in COLUNAS_ESPERADAS if c not in df.columns]
        if faltantes:
            return False, f"Colunas faltantes na planilha: {', '.join(faltantes)}"

        total = len(df)
        erros = []
        dados_lista = []

        for idx, row in df.iterrows():
            try:
                cpf = str(int(row["cpf"])).zfill(11) if pd.notna(row["cpf"]) else ""
                if not cpf:
                    erros.append(f"Linha {idx+2}: CPF vazio")
                    continue

                dados = {
                    "cpf": cpf,
                    "rg": str(row["rg"]) if pd.notna(row["rg"]) else "",
                    "nome": str(row["nome"]) if pd.notna(row["nome"]) else "",
                    "matricula": str(row["matricula"]) if pd.notna(row["matricula"]) else "",
                    "status": str(row["status"]) if pd.notna(row["status"]) else "",
                    "origem_info": str(row["origem_info"]) if pd.notna(row["origem_info"]) else "",
                    "lista_apeo": str(row["lista_apeo"]) if pd.notna(row["lista_apeo"]) else "",
                    "especificidade": str(row["especificidade"]) if pd.notna(row["especificidade"]) else "",
                    "processos_fazenda": str(row["processos_fazenda"]) if pd.notna(row["processos_fazenda"]) else "",
                    "processos_outros": str(row["processos_outros"]) if pd.notna(row["processos_outros"]) else "",
                    "qtdade_processos_fazenda": int(row["qtdade_processos_fazenda"]) if pd.notna(row["qtdade_processos_fazenda"]) else 0,
                    "qtdade_processos_outros": int(row["qtdade_processos_outros"]) if pd.notna(row["qtdade_processos_outros"]) else 0,
                    "qtdade_total_processos": int(row["qtdade_total_processos"]) if pd.notna(row["qtdade_total_processos"]) else 0,
                    "status_coleta_processos": str(row["status_coleta_processos"]) if pd.notna(row["status_coleta_processos"]) else "",
                    "data_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                dados_lista.append(dados)
            except Exception as e:
                erros.append(f"Linha {idx+2}: {str(e)}")

        if dados_lista:
            db.inserir_varios(dados_lista)
            inseridos = len(dados_lista)
            if callback_progresso:
                callback_progresso(inseridos, total)
        else:
            inseridos = 0

        msg = f"Importação concluída: {inseridos}/{total} registros inseridos."
        if erros:
            msg += f" {len(erros)} erro(s): " + "; ".join(erros[:10])
            if len(erros) > 10:
                msg += f"... e mais {len(erros)-10}."
        return True, msg
    except Exception as e:
        return False, f"Erro ao ler arquivo: {str(e)}"

def exportar_excel(caminho_saida):
    try:
        dados = db.backup()
        if not dados:
            return False, "Nenhum dado para exportar."

        colunas = [
            "nome", "rg", "cpf", "matricula", "status", "origem_info",
            "lista_apeo", "especificidade", "processos_fazenda", "processos_outros",
            "qtdade_processos_fazenda", "qtdade_processos_outros",
            "qtdade_total_processos", "status_coleta_processos",
            "data_cadastro", "data_atualizacao"
        ]
        df = pd.DataFrame(dados)
        df = df[[c for c in colunas if c in df.columns]]
        df.to_excel(caminho_saida, index=False, engine="openpyxl")
        return True, f"Backup exportado com sucesso: {len(dados)} registros."
    except Exception as e:
        return False, f"Erro ao exportar: {str(e)}"

def gerar_backup_json(caminho_saida):
    try:
        dados = db.backup()
        if not dados:
            return False, "Nenhum dado para backup."
        import json
        with open(caminho_saida, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return True, f"Backup JSON salvo: {len(dados)} registros."
    except Exception as e:
        return False, f"Erro ao gerar backup: {str(e)}"

def restaurar_backup_json(caminho_arquivo):
    try:
        import json
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if not isinstance(dados, list):
            return False, "Arquivo de backup inválido."
        db.restore(dados)
        return True, f"Backup restaurado com sucesso: {len(dados)} registros."
    except Exception as e:
        return False, f"Erro ao restaurar backup: {str(e)}"
