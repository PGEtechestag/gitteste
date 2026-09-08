"""Teste de fumaça: valida a inicialização e as principais telas sem loop de eventos."""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from ui.main_window import MainWindow
from ui.consulta_tab import formatar_cpf_digitado
from ui import historico


def main():
    # --- funções puras
    assert formatar_cpf_digitado("136280178") == "136.280.178"
    assert formatar_cpf_digitado("13628017801") == "136.280.178-01"
    assert formatar_cpf_digitado("136.280.178-01") == "136.280.178-01"
    assert historico.mascarar_cpf("00001362801") == "000.013.628-01"
    print("helpers OK")

    app = MainWindow()
    app.update()

    # --- consulta com CPF sem máscara (busca flexível)
    consulta = app.consulta_tab
    consulta.entry_cpf.delete(0, "end")
    consulta.entry_cpf.insert(0, "00001362801")
    consulta._buscar()
    app.update()
    assert consulta.dados_atuais is not None, "busca sem máscara falhou"
    assert consulta.dados_atuais["nome"].startswith("IRAIDES")
    print("busca sem máscara OK:", consulta.dados_atuais["nome"])

    # --- volta para a pesquisa e busca com máscara
    consulta._voltar_pesquisa()
    consulta.entry_cpf.delete(0, "end")
    consulta.entry_cpf.insert(0, "000.013.628-01")
    consulta._buscar()
    app.update()
    assert consulta.dados_atuais is not None, "busca com máscara falhou"
    print("busca com máscara OK")

    # --- histórico de consultas gravado
    consultas = historico.obter_consultas(5)
    assert any(c["cpf"] == "00001362801" for c in consultas), "histórico vazio"
    print("consultas recentes OK:", len(consultas), "registro(s)")

    # --- dashboard: recarregar (reconstrói a view atual)
    dash = app.dashboard_tab
    dash.recarregar()
    app.update()
    print("dashboard OK")

    # --- backup tab instanciada dentro das abas
    assert app.backup_tab is not None
    print("todas as telas OK")

    app.destroy()


if __name__ == "__main__":
    main()
    print("SMOKE TEST PASSED")
