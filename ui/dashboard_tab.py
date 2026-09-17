import customtkinter as ctk
from tkinter import Canvas
from database import cache as metricas
from ui import theme

PALETA_SECRETARIAS = [
    theme.AZUL_CLARO, theme.LARANJA, theme.ROXO, theme.CIANO,
    theme.VERDE, theme.VERMELHO, theme.ROXO_CLARO, theme.LARANJA_CLARO,
]


class DonutChart(Canvas):
    """Gráfico de rosca com percentual central."""

    def __init__(self, master, data, colors, tamanho=180, **kwargs):
        bg = theme.cor_tema(theme.CHART_BG)
        super().__init__(master, width=tamanho, height=tamanho, bg=bg,
                         highlightthickness=0, **kwargs)
        self.data = data
        self.colors = colors
        self.tamanho = tamanho
        self._desenhar()

    def _desenhar(self):
        self.delete("all")
        t = self.tamanho
        c = t / 2
        total = sum(v for _, v in self.data if v > 0)
        if total == 0:
            self.create_text(c, c, text="Sem dados",
                             fill=theme.cor_tema(theme.CHART_TEXT),
                             font=(theme.FONTE, 12))
            return

        raio = t / 2 - 14
        fatias = [(label, valor, cor) for (label, valor), cor in zip(self.data, self.colors) if valor > 0]

        if len(fatias) == 1:
            # Uma única categoria com 100%: um arco de 360° degenera no Tk Canvas,
            # então desenha-se o círculo cheio diretamente.
            _, _, cor = fatias[0]
            self.create_oval(c - raio, c - raio, c + raio, c + raio, fill=cor,
                             outline=theme.cor_tema(theme.CHART_BG), width=3)
        else:
            start = -90
            for label, valor, cor in fatias:
                extent = (valor / total) * 360
                self.create_arc(c - raio, c - raio, c + raio, c + raio, start=start,
                                extent=extent, fill=cor,
                                outline=theme.cor_tema(theme.CHART_BG), width=3)
                start += extent

        raio_interno = raio * 0.45
        self.create_oval(c - raio_interno, c - raio_interno,
                         c + raio_interno, c + raio_interno,
                         fill=theme.cor_tema(theme.CHART_BG), outline="")


class DashboardTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._criar_conteudo()

    def _criar_conteudo(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        # Esconde a barra de rolagem (fica sempre visível por padrão no CTk);
        # a rolagem pelo mouse continua funcionando normalmente.
        scroll._scrollbar.grid_remove()

        self._criar_metricas(scroll)
        self._criar_grafico_secretarias(scroll)

    def recarregar(self):
        """Reconstrói a view (usado após importações)."""
        for w in self.winfo_children():
            w.destroy()
        self._criar_conteudo()

    def _criar_metricas(self, scroll):
        m = metricas.obter_metricas()
        conferencia_cpfs = m["conferencia_cpfs"]
        conferencia_pendente = m["conferencia_pendente"]
        sem_processo_cpfs = m["sem_processo_cpfs"]
        cpfs_totais = m["cpfs_totais"]

        cards_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        cards_frame.grid(row=0, column=0, sticky="ew", pady=(8, 18))

        dados_cards = [
            ("usuarios", "Total de CPFs", cpfs_totais,
             "Com ou sem processo vinculado", theme.GRADIENTE_AZUL),
            ("pessoa", "CPFs - Processos Fazenda", conferencia_cpfs,
             "* Indivíduos com processos contra a fazenda pública do Estado de São Paulo",
             theme.GRADIENTE_LARANJA),
            ("check_circle", "CPFs - SEM Processos", sem_processo_cpfs,
             "Sem processos vinculados", theme.GRADIENTE_VERDE),
            ("alerta", "Processos p/ Conferir", conferencia_pendente,
             "Aguardando conferência", theme.GRADIENTE_VERMELHO),
        ]
        for i in range(len(dados_cards)):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="card")

        for i, (icone, titulo, valor, sub, gradiente) in enumerate(dados_cards):
            card = theme.card(cards_frame)
            card.grid(row=0, column=i, sticky="ew",
                      padx=(0, 12) if i < len(dados_cards) - 1 else 0, pady=4)

            # Faixa colorida no topo do card
            ctk.CTkFrame(
                card, height=3, fg_color=gradiente[0], corner_radius=2,
                border_width=0,
            ).pack(fill="x", padx=0, pady=0)

            topo = ctk.CTkFrame(card, fg_color="transparent")
            topo.pack(fill="x", padx=16, pady=(14, 0))

            # Ícone com fundo gradiente
            quadro = ctk.CTkFrame(
                topo, width=38, height=38, corner_radius=10,
                fg_color=gradiente[0],
            )
            quadro.pack(side="left")
            quadro.pack_propagate(False)
            ctk.CTkLabel(
                quadro, text="", image=theme.icono(icone, 17),
                font=ctk.CTkFont(family=theme.FONTE, size=17),
                text_color="white",
            ).pack(expand=True)

            ctk.CTkLabel(
                topo, text=titulo,
                font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
                text_color=theme.TEXTO, anchor="w",
            ).pack(side="left", padx=(10, 0))

            ctk.CTkLabel(
                card, text=theme.fmt_num(valor),
                font=ctk.CTkFont(family=theme.FONTE, size=26, weight="bold"),
                text_color=theme.TEXTO, anchor="w",
            ).pack(fill="x", padx=16, pady=(8, 0))
            ctk.CTkLabel(
                card, text=sub,
                font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
                text_color=gradiente[0], anchor="w", justify="left",
                wraplength=260,
            ).pack(fill="x", padx=16, pady=(0, 14))

    def _criar_grafico_secretarias(self, scroll):
        dados_detalhados = metricas.secretarias()  # [(secretaria, total, com_processo, sem_processo), ...]
        dados = [(secretaria, total) for secretaria, total, _, _ in dados_detalhados]

        card = theme.card(scroll)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(
            card, height=3, fg_color=theme.CIANO, corner_radius=2,
            border_width=0,
        ).pack(fill="x")

        ctk.CTkLabel(
            card, text="  CPFs por Secretaria", image=theme.icono("rosca", 15), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=15, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(fill="x", padx=18, pady=(14, 6))

        corpo = ctk.CTkFrame(card, fg_color="transparent")
        corpo.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        if not dados:
            ctk.CTkLabel(
                corpo,
                text="  Nenhuma planilha de conferência importada ainda.\nUse a seção \"Planilhas para Conferência\" na aba Backup.",
                image=theme.icono("alerta", 14), compound="left",
                font=ctk.CTkFont(family=theme.FONTE, size=12),
                text_color=theme.TEXTO_SEC, justify="center",
            ).pack(pady=22)
            return

        cores = [PALETA_SECRETARIAS[i % len(PALETA_SECRETARIAS)] for i in range(len(dados))]

        DonutChart(corpo, data=dados, colors=cores, tamanho=200).pack(
            side="left", padx=(4, 24), pady=8
        )

        legenda = ctk.CTkFrame(corpo, fg_color="transparent")
        legenda.pack(side="left", fill="both", expand=True, pady=8)
        total_geral = sum(v for _, v in dados)
        for (secretaria, total, com, sem), cor in zip(dados_detalhados, cores):
            linha = ctk.CTkFrame(legenda, fg_color="transparent")
            linha.pack(anchor="w", pady=6, fill="x")

            topo_linha = ctk.CTkFrame(linha, fg_color="transparent")
            topo_linha.pack(anchor="w", fill="x")
            ctk.CTkFrame(topo_linha, width=14, height=14, corner_radius=4,
                         fg_color=cor).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(
                topo_linha, text=f"{secretaria}  —  {theme.fmt_num(total)} CPF(s)  ({theme.fmt_pct(total, total_geral)})",
                font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
                text_color=theme.TEXTO, anchor="w",
            ).pack(side="left")

            ctk.CTkLabel(
                linha,
                text=f"     Com processo: {theme.fmt_num(com)} ({theme.fmt_pct(com, total)})   ·   "
                     f"Sem processo: {theme.fmt_num(sem)} ({theme.fmt_pct(sem, total)})",
                font=ctk.CTkFont(family=theme.FONTE, size=11),
                text_color=theme.TEXTO_SEC, anchor="w",
            ).pack(anchor="w", pady=(2, 0))
