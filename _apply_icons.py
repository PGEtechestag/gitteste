# -*- coding: utf-8 -*-
"""Substitúe emojis por iconos PNG profesionais na UI completa.

Este script percorre todos os ficheiros da UI e sustitúye emojis decorativos
por iconos PNG definidos en assets/icons/{light,dark,white}/*.png, usando a
función theme.icono() que xestiona o cambio automático entre temas claro/escuro.

Uso:
    python _apply_icons.py
"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))


def aplicar(path, substs):
    """Aplica pares de (old, new) por reemplazo de cadena exacta."""
    with io.open(path, "r", encoding="utf-8", newline=None) as f:
        texto = f.read()
    orixinal = texto
    for old, new in substs:
        n = texto.count(old)
        if n:
            texto = texto.replace(old, new)
            print(f"  {path}: {n}x aplicado: {old[:55]!r}")
        else:
            print(f"  {path}: NON ENCONTRADO: {old[:55]!r}")
    if texto != orixinal:
        with io.open(path, "w", encoding="utf-8", newline=None) as f:
            f.write(texto)
    else:
        print(f"  !! {path}: sen cambios")


# ================================================================
# consulta_tab.py
# ================================================================
SUBS_CONSULTA = [
    # Título do card de busca con icono
    ('text="🔍  Consultar por CPF",',
     'text="  Consultar por CPF",\n            image=theme.icono("consulta", 20), compound="left",'),
    # Botón buscar
    ('text="🔍   Buscar", command=self._buscar,',
     'text="  Buscar", command=self._buscar,\n            image=theme.icono("busca", 15), compound="left",'),
    # Botón volver a búsqueda
    ('text="←   Voltar à pesquisa", width=140, height=32,',
     'text="  Voltar à pesquisa", width=165, height=32,\n            image=theme.icono("voltar", 14), compound="left",'),
    # Botón ver proceso
    ('row, text="👁", width=32, height=28,',
     'row, text="", width=32, height=28,\n                image=theme.icono("olho", 14),'),
    # Dica con icono
    ('text="💡  Dica: Você pode digitar com ou sem máscara",',
     'text="  Dica: Você pode digitar com ou sem máscara",\n            image=theme.icono("info", 14), compound="left",'),
    # Estado vacío
    ('text="📭  Nenhuma consulta realizada ainda.\\nAs consultas que você fizer aparecerão aqui.",',
     'text="  Nenhuma consulta realizada ainda.\\nAs consultas que você fizer aparecerão aqui.",\n            image=theme.icono("relojo", 14), compound="left",'),
    # Título sección recentes
    ('text="🕘  Consultas Recentes"',
     'text="  Consultas Recentes", image=theme.icono("relojo", 14), compound="left"'),
    # Label de linha recente (emoji standalone)
    ('ctk.CTkLabel(row, text="🕘", font=ctk.CTkFont(family=theme.FONTE, size=12), text_color=theme.TEXTO_SEC),',
     'ctk.CTkLabel(row, text="", image=theme.icono("relojo", 12),\n                     font=ctk.CTkFont(family=theme.FONTE, size=12), text_color=theme.TEXTO_SEC),'),
     # Metric card render: text=icone -> image=
    ('ctk.CTkLabel(\n            icone_frame, text=icone,\n            font=ctk.CTkFont(family=theme.FONTE, size=16), text_color="white",\n        ).pack(expand=True)',
     'ctk.CTkLabel(\n            icone_frame, text="", image=theme.icono(icone, 16),\n            font=ctk.CTkFont(family=theme.FONTE, size=16), text_color="white",\n        ).pack(expand=True)'),
    # Metric card data: emoji -> nome do icono
    ('self._card_metrica(cards_metricas, 0, "👥", "Servidores"',
     'self._card_metrica(cards_metricas, 0, "usuarios", "Servidores"'),
    ('self._card_metrica(cards_metricas, 1, "📋", "Processos"',
     'self._card_metrica(cards_metricas, 1, "processos", "Processos"'),
    ('self._card_metrica(cards_metricas, 2, "🕒", "Atualizado em"',
     'self._card_metrica(cards_metricas, 2, "relojo", "Atualizado em"'),
    # Clear button: ✕ -> icon
    ('text="✕", width=36, height=36,\n            font=ctk.CTkFont(family=theme.FONTE, size=14, weight="bold"),',
     'text="", image=theme.icono("erro", 14), width=40, height=36,\n            font=ctk.CTkFont(family=theme.FONTE, size=14, weight="bold"),'),
]


# ================================================================
# dashboard_tab.py
# ================================================================
SUBS_DASHBOARD = [
    # Metric card render: text=icone -> image=
    ('ctk.CTkLabel(\n                quadro, text=icone,\n                font=ctk.CTkFont(family=theme.FONTE, size=17),\n                text_color="white",\n            ).pack(expand=True)',
     'ctk.CTkLabel(\n                quadro, text="", image=theme.icono(icone, 17),\n                font=ctk.CTkFont(family=theme.FONTE, size=17),\n                text_color="white",\n            ).pack(expand=True)'),
    # Metric card data
    ('("👥", "Servidores", total_servidores,',
     '("usuarios", "Servidores", total_servidores,'),
    ('("📋", "Processos Total", total_processos,',
     '("processos", "Processos Total", total_processos,'),
    ('("🏛️", "Processos Fazenda", total_fazenda,',
     '("fazenda", "Processos Fazenda", total_fazenda,'),
    ('("📁", "Outros Processos", total_outros,',
     '("arquivo", "Outros Processos", total_outros,'),
    # Headers co icono
    ('text="🍩  Processos por Origem"',
     'text="  Processos por Origem", image=theme.icono("rosca", 15), compound="left"'),
    ('text="📊  Servidores por Status"',
     'text="  Servidores por Status", image=theme.icono("grafico", 15), compound="left"'),
    ('text="📥  Últimas Importações"',
     'text="  Últimas Importações", image=theme.icono("importacao", 15), compound="left"'),
    ('text="📜  Atividades Recentes"',
     'text="  Atividades Recentes", image=theme.icono("logs", 15), compound="left"'),
    # Empty states
    ('text="📭  Nenhuma importação registrada.\\nUse o botão Importar Planilha no topo.",',
     'text="  Nenhuma importação registrada.\\nUse o botão Importar Planilha no topo.",\n            image=theme.icono("importacao", 14), compound="left",'),
    ('text="📭  Nenhuma atividade registrada ainda.",',
     'text="  Nenhuma atividade registrada ainda.", image=theme.icono("logs", 14), compound="left",'),
]


# ================================================================
# admin_tab.py
# ================================================================
SUBS_ADMIN = [
    # Icono de inicio de sesión (label grande)
    ('ctk.CTkLabel(\n            card, text="🔐", font=ctk.CTkFont(family=theme.FONTE, size=46),\n        ).pack(pady=(20, 6))',
     'ctk.CTkLabel(\n            card, text="", image=theme.icono("clave", 46),\n            font=ctk.CTkFont(family=theme.FONTE, size=46),\n        ).pack(pady=(20, 6))'),
    # Subtítulo de inicio de sesión
    ('text="🛡️  Área restrita para gestão de registros e configurações"',
     'text="  Área restrita para gestão de registros e configurações", image=theme.icono("escudo", 14), compound="left"'),
    # Avatar administrador
    ('ctk.CTkLabel(\n            av, text="🛡️", text_color="white",\n            font=ctk.CTkFont(family=theme.FONTE, size=24, weight="bold"),\n        ).pack(expand=True)',
     'ctk.CTkLabel(\n            av, text="", image=theme.icono("escudo", 24),\n            font=ctk.CTkFont(family=theme.FONTE, size=24, weight="bold"),\n            text_color="white",\n        ).pack(expand=True)'),
    # Título do panel
    ('text="⚙️  Painel Administrativo"',
     'text="  Painel Administrativo", image=theme.icono("admin", 16), compound="left"'),
    # Subtítulo do panel
    ('text="👋  Bem-vindo! Gerencie registros, configurações e monitore o sistema"',
     'text="  Bem-vindo! Gerencie registros, configurações e monitore o sistema", image=theme.icono("pessoa", 14), compound="left"'),
    # Botón saír
    ('text="🚪  Sair", command=self._logout,',
     'text="  Sair", command=self._logout, image=theme.icono("sair", 14), compound="left",'),
    # Etiqueta senha
    ('text="🔑  Senha de administrador"',
     'text="  Senha de administrador", image=theme.icono("clave", 14), compound="left"'),
    # Pista busca na pestana editar
    ('text="🔎  Busque um servidor pelo CPF para carregar e editar os dados"',
     'text="  Busque um servidor pelo CPF para carregar e editar os dados", image=theme.icono("busca", 14), compound="left"'),
    # Botón cargar
    ('text="📥  Carregar", command=self._carregar_edicao,',
     'text="  Carregar", command=self._carregar_edicao, image=theme.icono("importacao", 14), compound="left",'),
    # Botón borrar
    ('text="🗑️  Deletar", command=self._deletar_registro,',
     'text="  Deletar", command=self._deletar_registro, image=theme.icono("deletar", 14), compound="left",'),
    # Título formulario
    ('text="📝  Dados do Registro"',
     'text="  Dados do Registro", image=theme.icono("nota", 14), compound="left"'),
    # Pista busca na pestana buscar
    ('text="🔎  Pesquise servidores pelo nome (máx. 30 resultados)"',
     'text="  Pesquise servidores pelo nome (máx. 30 resultados)", image=theme.icono("busca", 14), compound="left"'),
    # Botón buscar
    ('text="🔎  Buscar", command=self._buscar_pessoas,',
     'text="  Buscar", command=self._buscar_pessoas, image=theme.icono("busca", 14), compound="left",'),
    # Pista na pestana buscar (ambas las ocurrencias)
    ('text="💡  Digite um nome para pesquisar.",',
     'text="  Digite um nome para pesquisar.",\n            image=theme.icono("info", 14), compound="left",'),
    # Empty state en resultados de busca
    ('text="📭  Nenhum servidor encontrado.",',
     'text="  Nenhum servidor encontrado.",\n            image=theme.icono("pessoa", 14), compound="left",'),
    # Header na pestana de acoes
    ('text="⚡  Ações administrativas do sistema"',
     'text="  Ações administrativas do sistema", image=theme.icono("raio", 14), compound="left"'),
    # Botón salvar
    ('text="💾  Salvar Alterações", command=self._salvar_alteracoes,',
     'text="  Salvar Alterações", command=self._salvar_alteracoes,\n            image=theme.icono("salvar", 14), compound="left",'),
    # Botón limpar formulario
    ('text="🔄  Limpar", command=self._limpar_form,',
     'text="  Limpar", command=self._limpar_form,\n            image=theme.icono("atualizar", 14), compound="left",'),
    # Título actividades
    ('text="📜  Histórico de eventos administrativos do sistema"',
     'text="  Histórico de eventos administrativos do sistema", image=theme.icono("logs", 14), compound="left"'),
    # Estado vacío actividades
    ('text="📭  Nenhuma atividade registrada ainda.",',
     'text="  Nenhuma atividade registrada ainda.", image=theme.icono("logs", 14), compound="left",'),
    # Título stats popup (popup.title)
    ('popup.title("📊 Estatísticas do Sistema")',
     'popup.title("Estatísticas do Sistema")'),
    # Título stats popup (label)
    ('text="📊  Estatísticas do Sistema"',
     'text="  Estatísticas do Sistema", image=theme.icono("dashboard", 16), compound="left"'),
    # Metric card render: text=icon -> image=
    ('ctk.CTkLabel(box, text=icon, text_color="white",\n                         font=ctk.CTkFont(family=theme.FONTE, size=16)).pack(expand=True)',
     'ctk.CTkLabel(box, text="", image=theme.icono(icon, 16), text_color="white",\n                         font=ctk.CTkFont(family=theme.FONTE, size=16)).pack(expand=True)'),
    # Metric card data
    ('("👥", "Servidores", theme.fmt_num(total), "Total na base"',
     '("usuarios", "Servidores", theme.fmt_num(total), "Total na base"'),
    ('("📋", "Processos", theme.fmt_num(total_proc),',
     '("processos", "Processos", theme.fmt_num(total_proc),'),
    ('("🏛️", "Fazenda", theme.fmt_num(fazenda),',
     '("fazenda", "Fazenda", theme.fmt_num(fazenda),'),
    ('("📁", "Outros", theme.fmt_num(outros),',
     '("arquivo", "Outros", theme.fmt_num(outros),'),
    # Action card render: text=icon -> image=
    ('ctk.CTkLabel(topo, text=icon,\n                     font=ctk.CTkFont(family=theme.FONTE, size=24)\n                     ).pack(side="left", padx=(0, 10))',
     'ctk.CTkLabel(topo, text="", image=theme.icono(icon, 24),\n                     font=ctk.CTkFont(family=theme.FONTE, size=24)\n                     ).pack(side="left", padx=(0, 10))'),
    # Action card data
    ('("🔑", "Alterar Senha Admin"',
     '("clave", "Alterar Senha Admin"'),
    ('("📊", "Ver Estatísticas"',
     '("dashboard", "Ver Estatísticas"'),
    ('("🔄", "Recarregar Dados"',
     '("atualizar", "Recarregar Dados"'),
    ('("⚠️", "Limpar Todos os Dados"',
     '("alerta", "Limpar Todos os Dados"'),
    # Event icon dict
    ('"importacao": ("📥", theme.AZUL_CLARO),',
     '"importacao": ("importacao", theme.AZUL_CLARO),'),
    ('"backup": ("💾", theme.CIANO),',
     '"backup": ("backup", theme.CIANO),'),
    ('"restauracao": ("♻️", theme.LARANJA),',
     '"restauracao": ("importacao", theme.LARANJA),'),
    ('"limpeza": ("🗑️", theme.VERMELHO),',
     '"limpeza": ("deletar", theme.VERMELHO),'),
    ('"admin_login": ("🔐", theme.ROXO)',
     '"admin_login": ("clave", theme.ROXO)'),
    # Fallback icono
    ('("📌", theme.TEXTO_SEC)',
     '("estrela", theme.TEXTO_SEC)'),
    # Label con icono de evento
    ('ctk.CTkLabel(\n                box, text=icone,\n                font=ctk.CTkFont(family=theme.FONTE, size=14),\n            ).pack(expand=True)',
     'ctk.CTkLabel(\n                box, text="", image=theme.icono(icone, 14),\n                font=ctk.CTkFont(family=theme.FONTE, size=14),\n            ).pack(expand=True)'),
    # Labels do formulario (emoji -> nome do icono)
    ('("cpf", "CPF (somente leitura)", "👤")',
     '("cpf", "CPF (somente leitura)", "pessoa")'),
    ('("nome", "Nome", "📛")',
     '("nome", "Nome", "nota")'),
    ('("rg", "RG", "🆔")',
     '("rg", "RG", "documento")'),
    ('("matricula", "Matrícula", "🔢")',
     '("matricula", "Matrícula", "calendario")'),
    ('("status", "Status", "📊")',
     '("status", "Status", "grafico")'),
    ('("origem_info", "Origem Info", "📍")',
     '("origem_info", "Origem Info", "pessoa")'),
    ('("lista_apeo", "Lista APEO", "📋")',
     '("lista_apeo", "Lista APEO", "processos")'),
    ('("especificidade", "Especificidade", "🏷️")',
     '("especificidade", "Especificidade", "etiqueta")'),
    ('("qtdade_processos_fazenda", "Qtd. Processos Fazenda", "🏛️")',
     '("qtdade_processos_fazenda", "Qtd. Processos Fazenda", "fazenda")'),
    ('("qtdade_processos_outros", "Qtd. Processos Outros", "📁")',
     '("qtdade_processos_outros", "Qtd. Processos Outros", "arquivo")'),
    ('("qtdade_total_processos", "Qtd. Total Processos", "🔢")',
     '("qtdade_total_processos", "Qtd. Total Processos", "calendario")'),
    ('("status_coleta_processos", "Status Coleta", "✓")',
     '("status_coleta_processos", "Status Coleta", "check")'),
    # Render das labels do formulario: f"{icone}  {label}" -> image + text
    ('text=f"{icone}  {label}",',
     'text=f"  {label}", image=theme.icono(icone, 12), compound="left",'),
    # Título "Distribuição por Status"
    ('text="📊 Distribuição por Status"',
     'text="  Distribuição por Status", image=theme.icono("grafico", 14), compound="left"'),
    # Dialog title: remove decorative emoji
    ('title="🔑 Alterar Senha"',
     'title="Alterar Senha"'),
    # Table headers: remove emojis from column titles
    ('for txt, col in (("👤 Nome", 0), ("🔢 CPF", 1), ("📊 Status", 2), ("⚙️ Ações", 3)):',
     'for txt, col in (("Nome", 0), ("CPF", 1), ("Status", 2), ("Ações", 3)):'),
    # Editar button: emoji -> icon
    ('row, text="✏️  Editar", width=90, height=28,',
     'row, text="  Editar", image=theme.icono("editar", 14), compound="left", width=100, height=28,'),
    # Stats labels: remove emojis from text
    ('("👥 Servidores cadastrados", theme.fmt_num(total), theme.GRADIENTE_AZUL[0]),',
     '("Servidores cadastrados", theme.fmt_num(total), theme.GRADIENTE_AZUL[0]),'),
    ('("📋 Total de processos", theme.fmt_num(total_proc), theme.GRADIENTE_ROXO[0]),',
     '("Total de processos", theme.fmt_num(total_proc), theme.GRADIENTE_ROXO[0]),'),
    ('("🏛️ Processos Fazenda", theme.fmt_num(fazenda), theme.GRADIENTE_CIANO[0]),',
     '("Processos Fazenda", theme.fmt_num(fazenda), theme.GRADIENTE_CIANO[0]),'),
    ('("📁 Outros processos", theme.fmt_num(outros), theme.GRADIENTE_LARANJA[0]),',
     '("Outros processos", theme.fmt_num(outros), theme.GRADIENTE_LARANJA[0]),'),
]


# ================================================================
# backup_tab.py
# ================================================================
SUBS_BACKUP = [
    # Icono de cabeceira
    ('ctk.CTkLabel(\n            linha, text="💾",\n            font=ctk.CTkFont(family=theme.FONTE, size=34),\n        ).grid(row=0, column=0, padx=(0, 14))',
     'ctk.CTkLabel(\n            linha, text="", image=theme.icono("backup", 34),\n            font=ctk.CTkFont(family=theme.FONTE, size=34),\n        ).grid(row=0, column=0, padx=(0, 14))'),
    # Subtítulo cabeceira
    ('text="🛡️  Proteja seus dados com backup periódico e restaure sempre que precisar"',
     'text="  Proteja seus dados com backup periódico e restaure sempre que precisar", image=theme.icono("escudo", 14), compound="left"'),
    # Action card render: text=icone -> image=
    ('ctk.CTkLabel(\n            topo, text=icone,\n            font=ctk.CTkFont(family=theme.FONTE, size=24),\n        ).pack(side="left", padx=(0, 12))',
     'ctk.CTkLabel(\n            topo, text="", image=theme.icono(icone, 24),\n            font=ctk.CTkFont(family=theme.FONTE, size=24),\n        ).pack(side="left", padx=(0, 12))'),
    # Action card data (emoji is second arg, not in a tuple)
    ('"📤", "Exportar Excel"',
     '"exportacao", "Exportar Excel"'),
    ('"📋", "Exportar JSON"',
     '"exportacao", "Exportar JSON"'),
    ('"♻️", "Restaurar Backup"',
     '"importacao", "Restaurar Backup"'),
    ('"🗑️", "Limpar Dados"',
     '"deletar", "Limpar Dados"'),
]


# ================================================================
# Dashboard: transformación de _icone_evento
# ================================================================
def transformar_dashboard_iconos_evento(texto):
    """Cambia a función _icone_evento para devolver nomes de iconos e usa image=."""
    texto = texto.replace(
        'return {\n'
        '            "importacao": "📥",\n'
        '            "backup": "💾",\n'
        '            "restauracao": "♻️",\n'
        '            "limpeza": "🗑️",\n'
        '        }.get(tipo, "📌")',
        'return {\n'
        '            "importacao": "importacao",\n'
        '            "backup": "backup",\n'
        '            "restauracao": "importacao",\n'
        '            "limpeza": "deletar",\n'
        '        }.get(tipo, "estrela")'
    )
    texto = texto.replace(
        'ctk.CTkLabel(\n'
        '            linha, text=self._icone_evento(evento.get("tipo")),\n'
        '            font=ctk.CTkFont(family=theme.FONTE, size=14),\n'
        '            text_color=theme.TEXTO_SEC,\n'
        '        ).grid(row=0, column=0, padx=(0, 12))',
        'ctk.CTkLabel(\n'
        '            linha, text="", image=theme.icono(self._icone_evento(evento.get("tipo")), 14),\n'
        '            font=ctk.CTkFont(family=theme.FONTE, size=14),\n'
        '            text_color=theme.TEXTO_SEC,\n'
        '        ).grid(row=0, column=0, padx=(0, 12))'
    )
    return texto


# ================================================================
# Admin: transformación de abas (tabs)
# ================================================================
def transformar_tabs_admin(texto):
    """Remove emojis dos nomes de abas e engade iconos aos botóns."""
    # Remove emojis dos .add()
    texto = texto.replace('self.abas.add("✏️  Editar Registro")',
                          'self.abas.add("Editar Registro")')
    texto = texto.replace('self.abas.add("🔍  Buscar Pessoas")',
                          'self.abas.add("Buscar Pessoas")')
    texto = texto.replace('self.abas.add("⚡  Ações Rápidas")',
                          'self.abas.add("Ações Rápidas")')
    texto = texto.replace('self.abas.add("📜  Atividades Recentes")',
                          'self.abas.add("Atividades Recentes")')
    # Remove emojis dos .tab() e .set()
    texto = texto.replace('self.abas.tab("✏️  Editar Registro")',
                          'self.abas.tab("Editar Registro")')
    texto = texto.replace('self.abas.tab("🔍  Buscar Pessoas")',
                          'self.abas.tab("Buscar Pessoas")')
    texto = texto.replace('self.abas.tab("⚡  Ações Rápidas")',
                          'self.abas.tab("Ações Rápidas")')
    texto = texto.replace('self.abas.tab("📜  Atividades Recentes")',
                          'self.abas.tab("Atividades Recentes")')
    texto = texto.replace('self.abas.set("✏️  Editar Registro")',
                          'self.abas.set("Editar Registro")')

    # Anadir configuración de iconos despois de crear as abas
    old_tabs = '        aba_ativ = self.abas.tab("Atividades Recentes")'
    new_tabs = (
        '        aba_ativ = self.abas.tab("Atividades Recentes")\n\n'
        '        # Iconos nas abas\n'
        '        for nome_aba, icon_nome in [\n'
        '            ("Editar Registro", "editar"),\n'
        '            ("Buscar Pessoas", "busca"),\n'
        '            ("Ações Rápidas", "raio"),\n'
        '            ("Atividades Recentes", "logs"),\n'
        '        ]:\n'
        '            try:\n'
        '                boto = self.abas._segmented_button._buttons_dict.get(nome_aba)\n'
        '                if boto is not None:\n'
        '                    boto.configure(\n'
        '                        image=theme.icono(icon_nome, 14),\n'
        '                        compound="left",\n'
        '                        text=nome_aba,\n'
        '                    )\n'
        '            except Exception:\n'
        '                pass'
    )
    texto = texto.replace(old_tabs, new_tabs)
    return texto


def aplicar_transformacion(path, func):
    """Aplica unha transformación personalizada a un arquivo."""
    with io.open(path, "r", encoding="utf-8", newline=None) as f:
        texto = f.read()
    novo = func(texto)
    if novo != texto:
        with io.open(path, "w", encoding="utf-8", newline=None) as f:
            f.write(novo)
        print(f"  {path}: transformación aplicada")
    else:
        print(f"  !! {path}: sen cambios (transformación)")


# ================================================================
# Execución
# ================================================================
print("=== Optimización de Iconos ===")
print()

aplicar(os.path.join(BASE, "ui", "consulta_tab.py"), SUBS_CONSULTA)
print()

aplicar(os.path.join(BASE, "ui", "dashboard_tab.py"), SUBS_DASHBOARD)
aplicar_transformacion(os.path.join(BASE, "ui", "dashboard_tab.py"), transformar_dashboard_iconos_evento)
print()

aplicar(os.path.join(BASE, "ui", "admin_tab.py"), SUBS_ADMIN)
aplicar_transformacion(os.path.join(BASE, "ui", "admin_tab.py"), transformar_tabs_admin)
print()

aplicar(os.path.join(BASE, "ui", "backup_tab.py"), SUBS_BACKUP)
print()

print("=== Listo! ===")
