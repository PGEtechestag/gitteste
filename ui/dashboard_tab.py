import customtkinter as ctk
from tkinter import Canvas
from database import cache as metricas
from ui import theme
from ui import historico


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
        start = -90
        for (label, valor), cor in zip(self.data, self.colors):
            if valor <= 0:
                continue
            extent = (valor / total) * 360
            self.create_arc(c - raio, c - raio, c + raio, c + raio, start=start,
                            extent=extent, fill=cor,
                            outline=theme.cor_tema(theme.CHART_BG), width=3)
            start += extent

        raio_interno = raio * 0.62
        self.create_oval(c - raio_interno, c - raio_interno,
                         c + raio_interno, c + raio_interno,
                         fill=theme.cor_tema(theme.CHART_BG), outline="")
        if self.data and self.data[0][1] > 0:
            pct_txt = theme.fmt_pct(self.data[0][1], total)
            self.create_text(c, c - 8, text=pct_txt,
                             fill=theme.cor_tema({"Light": "#1f2430", "Dark": "#F5F5F5"}),
                             font=(theme.FONTE, 18, "bold"))
            self.create_text(c, c + 12, text=self.data[0][0],
                             fill=theme.cor_tema(theme.CHART_TEXT),
                             font=(theme.FONTE, 10))


def _numero_curto(n):
    if n >= 1000:
        return f"{n / 1000:.0f}k"
    return str(n)


class BarChart(Canvas):
    """Gráfico de barras com eixo Y, linhas de grade e rótulos."""

    def __init__(self, master, data, colors, largura=480, altura=220, **kwargs):
        bg = theme.cor_tema(theme.CHART_BG)
        super().__init__(master, width=largura, height=altura, bg=bg,
                         highlightthickness=0, **kwargs)
        self.data = data
        self.colors = colors
        self._desenhar()

    def _desenhar(self):
        self.delete("all")
        w = int(self.winfo_reqwidth())
        h = int(self.winfo_reqheight())
        if not self.data or all(v == 0 for _, v in self.data):
            self.create_text(w / 2, h / 2, text="Sem dados",
                             fill=theme.cor_tema(theme.CHART_TEXT),
                             font=(theme.FONTE, 12))
            return

        cor_texto = theme.cor_tema(theme.CHART_TEXT)
        cor_grade = theme.cor_tema(theme.CHART_GRID)

        max_val = max(v for _, v in self.data) or 1
        potencia = 10 ** (len(str(int(max_val))) - 1)
        max_escala = ((max_val + potencia - 1) // potencia) * potencia

        margem_esq, margem_dir, topo, base_y = 52, 18, 18, h - 36
        area_larg = w - margem_esq - margem_dir
        area_alt = base_y - topo

        passos = 4
        for i in range(passos + 1):
            frac = i / passos
            y = base_y - frac * area_alt
            self.create_line(margem_esq, y, w - margem_dir, y, fill=cor_grade)
            self.create_text(margem_esq - 10, y, text=_numero_curto(int(max_escala * frac)),
                             fill=cor_texto, font=(theme.FONTE, 10), anchor="e")

        n = len(self.data)
        slot = area_larg / n
        larg_barra = min(60, slot * 0.5)

        for i, ((label, valor), cor) in enumerate(zip(self.data, self.colors)):
            cx = margem_esq + slot * (i + 0.5)
            x0, x1 = cx - larg_barra / 2, cx + larg_barra / 2
            altura_barra = (valor / max_escala) * area_alt if max_escala else 0
            y_top = base_y - altura_barra

            if valor > 0:
                self.create_rectangle(x0, y_top, x1, base_y, fill=cor, outline="")
                texto = theme.fmt_num(valor)
                self.create_text(cx, y_top - 12, text=texto,
                                 fill=theme.cor_tema({"Light": "#1f2430", "Dark": "#F5F5F5"}),
                                 font=(theme.FONTE, 11, "bold"))
            label_curta = str(label)[:10] + "..." if len(str(label)) > 10 else label
            self.create_text(cx, base_y + 14, text=label_curta,
                             fill=cor_texto, font=(theme.FONTE, 10))


class DashboardTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._criar_conteudo()

    def _criar_conteudo(self):
        scroll = ctk.CTkScrollableFrame(self.container_area(), fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        self._criar_header(scroll)
        self._criar_metricas(scroll)
        self._criar_graficos(scroll)
        self._criar_tabelas(scroll)

    def container_area(self):
        return self

    def recarregar(self):
        """Reconstrói a view (usado após importações)."""
        for w in self.winfo_children():
            w.destroy()
        self._criar_conteudo()

    def _criar_header(self, scroll):
        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(8, 14))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="Dashboard",
            font=ctk.CTkFont(family=theme.FONTE, size=28, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header, text="Visão geral do sistema — Paritários SPPrev",
            font=ctk.CTkFont(family=theme.FONTE, size=14),
            text_color=theme.TEXTO_SEC, anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    def _criar_metricas(self, scroll):
        m = metricas.obter_metricas()
        total_servidores = m["total"]
        total_processos = m["geral"]
        total_fazenda = m["fazenda"]
        total_outros = m["outros"]

        cards_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", pady=(0, 18))
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="card")

        dados_cards = [
            ("usuarios", "Servidores", total_servidores,
             f"Ativos: {theme.fmt_num(self._contar_status_grupo('ativo'))}",
             theme.GRADIENTE_AZUL),
            ("processos", "Processos Total", total_processos, "Somatório da base",
             theme.GRADIENTE_ROXO),
            ("fazenda", "Processos Fazenda", total_fazenda,
             theme.fmt_pct(total_fazenda, total_processos) + " do total",
             theme.GRADIENTE_CIANO),
            ("arquivo", "Outros Processos", total_outros,
             theme.fmt_pct(total_outros, total_processos) + " do total",
             theme.GRADIENTE_LARANJA),
        ]

        for i, (icone, titulo, valor, sub, gradiente) in enumerate(dados_cards):
            card = theme.card(cards_frame)
            card.grid(row=0, column=i, sticky="ew",
                      padx=(0, 12) if i < 3 else 0, pady=4)

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
                text_color=gradiente[0], anchor="w",
            ).pack(fill="x", padx=16, pady=(0, 14))

    def _contar_status_grupo(self, grupo):
        status_data = metricas.status()
        total = 0
        for nome, qtd in status_data.items():
            s = str(nome).lower()
            if grupo == "ativo" and "ativo" in s and "inativo" not in s:
                total += qtd
            elif grupo == "inativo" and "inativo" in s and "pensionista" not in s:
                total += qtd
            elif grupo == "pensionista" and "pensionista" in s:
                total += qtd
        return total

    def _criar_graficos(self, scroll):
        m = metricas.obter_metricas()
        graficos = ctk.CTkFrame(scroll, fg_color="transparent")
        graficos.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        graficos.grid_columnconfigure(0, weight=2, uniform="graf")
        graficos.grid_columnconfigure(1, weight=3, uniform="graf")

        card_rosca = theme.card(graficos)
        card_rosca.grid(row=0, column=0, sticky="nsew",
                        padx=(0, 12), pady=4)
        # Faixa colorida
        ctk.CTkFrame(
            card_rosca, height=3, fg_color=theme.CIANO, corner_radius=2,
            border_width=0,
        ).pack(fill="x")

        ctk.CTkLabel(
            card_rosca, text="  Processos por Origem", image=theme.icono("rosca", 15), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=15, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(fill="x", padx=18, pady=(14, 6))

        total_fazenda = m["fazenda"]
        total_outros = m["outros"]
        corpo = ctk.CTkFrame(card_rosca, fg_color="transparent")
        corpo.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        DonutChart(
            corpo,
            data=[("Fazenda", total_fazenda), ("Outros", total_outros)],
            colors=[theme.AZUL_CLARO, theme.LARANJA],
        ).pack(side="left", padx=(4, 16), pady=8)

        legenda = ctk.CTkFrame(corpo, fg_color="transparent")
        legenda.pack(side="left", expand=True, pady=8)
        total = total_fazenda + total_outros
        for nome, valor, cor in (("Fazenda", total_fazenda, theme.AZUL_CLARO),
                                 ("Outros", total_outros, theme.LARANJA)):
            linha = ctk.CTkFrame(legenda, fg_color="transparent")
            linha.pack(anchor="w", pady=6)
            ctk.CTkFrame(linha, width=14, height=14, corner_radius=4,
                         fg_color=cor).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(
                linha, text=f"{nome}  ({theme.fmt_pct(valor, total)})",
                font=ctk.CTkFont(family=theme.FONTE, size=13),
                text_color=theme.TEXTO, anchor="w",
            ).pack(side="left")

        card_barras = theme.card(graficos)
        card_barras.grid(row=0, column=1, sticky="nsew", pady=4)
        # Faixa colorida
        ctk.CTkFrame(
            card_barras, height=3, fg_color=theme.ROXO, corner_radius=2,
            border_width=0,
        ).pack(fill="x")

        ctk.CTkLabel(
            card_barras, text="  Servidores por Status", image=theme.icono("grafico", 15), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=15, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(fill="x", padx=18, pady=(14, 6))

        status_data = m["status"]
        ativos = self._contar_status_grupo("ativo")
        pensionistas = self._contar_status_grupo("pensionista")
        outros = max(sum(status_data.values()) - ativos - pensionistas, 0)

        bar_data = [
            ("Ativo", ativos),
            ("Pensionista", pensionistas),
            ("Outros", outros),
        ]
        cores = [theme.VERDE, theme.VERMELHO, theme.ROXO, theme.CIANO]

        BarChart(card_barras, data=bar_data, colors=cores).pack(
            fill="both", expand=True, padx=12, pady=(0, 12)
        )

    def _criar_tabelas(self, scroll):
        tabelas = ctk.CTkFrame(scroll, fg_color="transparent")
        tabelas.grid(row=3, column=0, sticky="ew", pady=(0, 16))
        tabelas.grid_columnconfigure(0, weight=1)
        tabelas.grid_columnconfigure(1, weight=1)

        card_imp = theme.card(tabelas)
        card_imp.grid(row=0, column=0, sticky="nsew",
                      padx=(0, 12), pady=4)
        card_imp.grid_columnconfigure(0, weight=1)
        ctk.CTkFrame(
            card_imp, height=3, fg_color=theme.VERDE, corner_radius=2,
            border_width=0,
        ).grid(row=0, column=0, sticky="ew")

        header_imp = ctk.CTkFrame(card_imp, fg_color="transparent")
        header_imp.grid(row=1, column=0, sticky="ew", padx=18, pady=(14, 6))
        ctk.CTkLabel(
            header_imp, text="  Últimas Importações", image=theme.icono("importacao", 15), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=15, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(side="left")
        ctk.CTkButton(
            header_imp, text="Ver todas", width=90, height=30,
            font=ctk.CTkFont(family=theme.FONTE, size=12),
            corner_radius=9, fg_color=theme.FIELD,
            hover_color=theme.CARD_BORDER,
            text_color=theme.ACCENT, border_width=1,
            border_color=theme.CARD_BORDER,
            command=lambda: self._popup_eventos("importacao", "Últimas Importações"),
        ).pack(side="right")

        importacoes = historico.obter_eventos("importacao", 4)
        if importacoes:
            for i, imp in enumerate(importacoes):
                self._linha_evento(card_imp, i + 2, imp, com_badge=True)
        else:
            ctk.CTkLabel(
                card_imp,
                text="  Nenhuma importação registrada.\nUse o botão Importar Planilha no topo.",
            image=theme.icono("importacao", 14), compound="left",
                font=ctk.CTkFont(family=theme.FONTE, size=12),
                text_color=theme.TEXTO_SEC, justify="center",
            ).grid(row=2, column=0, pady=22, padx=18)

        card_ativ = theme.card(tabelas)
        card_ativ.grid(row=0, column=1, sticky="nsew", pady=4)
        card_ativ.grid_columnconfigure(0, weight=1)
        ctk.CTkFrame(
            card_ativ, height=3, fg_color=theme.ROXO, corner_radius=2,
            border_width=0,
        ).grid(row=0, column=0, sticky="ew")

        header_ativ = ctk.CTkFrame(card_ativ, fg_color="transparent")
        header_ativ.grid(row=1, column=0, sticky="ew", padx=18, pady=(14, 6))
        ctk.CTkLabel(
            header_ativ, text="  Atividades Recentes", image=theme.icono("logs", 15), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=15, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(side="left")
        ctk.CTkButton(
            header_ativ, text="Ver todas", width=90, height=30,
            font=ctk.CTkFont(family=theme.FONTE, size=12),
            corner_radius=9, fg_color=theme.FIELD,
            hover_color=theme.CARD_BORDER,
            text_color=theme.ACCENT, border_width=1,
            border_color=theme.CARD_BORDER,
            command=lambda: self._popup_eventos(None, "Atividades Recentes"),
        ).pack(side="right")

        atividades = historico.obter_eventos(None, 4)
        if atividades:
            for i, ev in enumerate(atividades):
                self._linha_evento(card_ativ, i + 2, ev, com_badge=False)
        else:
            ctk.CTkLabel(
                card_ativ, text="  Nenhuma atividade registrada ainda.", image=theme.icono("logs", 14), compound="left",
                font=ctk.CTkFont(family=theme.FONTE, size=12),
                text_color=theme.TEXTO_SEC, justify="center",
            ).grid(row=2, column=0, pady=22, padx=18)

    def _icone_evento(self, tipo):
        return {
            "importacao": "importacao",
            "backup": "backup",
            "restauracao": "importacao",
            "limpeza": "deletar",
        }.get(tipo, "estrela")

    def _linha_evento(self, parent, row, evento, com_badge):
        linha = ctk.CTkFrame(parent, fg_color="transparent")
        linha.grid(row=row, column=0, sticky="ew", padx=18, pady=4)
        linha.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            linha, text="", image=theme.icono(self._icone_evento(evento.get("tipo")), 14),
            font=ctk.CTkFont(family=theme.FONTE, size=14),
            text_color=theme.TEXTO_SEC,
        ).grid(row=0, column=0, padx=(0, 12))

        texto = evento.get("titulo", "")
        if evento.get("detalhe"):
            texto += f"\n{evento.get('detalhe')}"
        ctk.CTkLabel(
            linha, text=texto, anchor="w", justify="left",
            font=ctk.CTkFont(family=theme.FONTE, size=12),
            text_color=theme.TEXTO,
        ).grid(row=0, column=1, sticky="w")

        lado = ctk.CTkFrame(linha, fg_color="transparent")
        lado.grid(row=0, column=2, sticky="e", padx=(12, 0))
        if com_badge:
            theme.badge(lado, "Sucesso", "#86efac", "#14532d", tamanho=11).pack(
                side="right", padx=(0, 10))
        ctk.CTkLabel(
            lado, text=historico.tempo_relativo(evento.get("ts")),
            font=ctk.CTkFont(family=theme.FONTE, size=11),
            text_color=theme.TEXTO_SEC,
        ).pack(side="right")

    def _popup_eventos(self, tipo, titulo):
        popup = ctk.CTkToplevel(self)
        popup.title(titulo)
        popup.geometry("560x460")
        popup.transient(self.winfo_toplevel())

        popup.grid_rowconfigure(1, weight=1)
        popup.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            popup, text=titulo,
            font=ctk.CTkFont(family=theme.FONTE, size=17, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(20, 10))

        card = theme.card(popup)
        card.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 20))
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)

        eventos = historico.obter_eventos(tipo)
        if not eventos:
            ctk.CTkLabel(
                card, text="Nenhum registro.",
                font=ctk.CTkFont(family=theme.FONTE, size=13),
                text_color=theme.TEXTO_SEC,
            ).grid(row=0, column=0, pady=40)
            return

        lista = ctk.CTkScrollableFrame(card, fg_color="transparent")
        lista.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        lista.grid_columnconfigure(0, weight=1)
        for i, ev in enumerate(eventos):
            self._linha_evento(lista, i, ev, com_badge=(tipo == "importacao"))
