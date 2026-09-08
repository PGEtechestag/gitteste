import re
from datetime import datetime
import customtkinter as ctk
from database.db_manager import DatabaseManager
from database import cache as metricas
from ui import theme
from ui import historico

db = DatabaseManager()

REGEX_PROCESSO = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")


def formatar_cpf_digitado(texto):
    """Aplica a máscara 000.000.000-00 conforme o usuário digita."""
    d = "".join(ch for ch in texto if ch.isdigit())[:11]
    partes = [d[:3]]
    if len(d) > 3:
        partes.append(d[3:6])
    if len(d) > 6:
        partes.append(d[6:9])
    if len(d) > 9:
        partes.append("-" + d[9:11])
    return ".".join(partes[:3]) + partes[3] if len(partes) > 3 else ".".join(partes)


def datetime_br(ts):
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")


class ConsultaTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.dados_atuais = None
        self._ver_todas = False

        self._criar_view_busca()
        self._criar_view_resultado()
        self.view_busca.grid(row=0, column=0, sticky="nsew")

    # ================================================================ BUSCA
    def _criar_view_busca(self):
        self.view_busca = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.view_busca.grid_columnconfigure(0, weight=1)
        self._conteudo_busca = None
        self._montar_conteudo_busca()

    def _montar_conteudo_busca(self):
        if self._conteudo_busca is not None:
            self._conteudo_busca.destroy()

        conteudo = ctk.CTkFrame(self.view_busca, fg_color="transparent")
        conteudo.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        conteudo.grid_columnconfigure(0, weight=1)
        self._conteudo_busca = conteudo

        # ------------------------------------------------------- card busca
        card_busca = theme.card(conteudo)
        card_busca.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        card_busca.grid_columnconfigure(0, weight=1)

        # Faixa colorida superior
        ctk.CTkFrame(
            card_busca, height=4, fg_color=theme.AZUL_CLARO,
            corner_radius=2, border_width=0,
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 0))

        ctk.CTkLabel(
            card_busca, text="  Consultar por CPF",
            image=theme.icono("consulta", 20), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=20, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=22, pady=(12, 2))

        ctk.CTkLabel(
            card_busca, text="Digite o CPF para buscar as informações do servidor",
            font=ctk.CTkFont(family=theme.FONTE, size=13),
            text_color=theme.TEXTO_SEC, anchor="w",
        ).grid(row=2, column=0, sticky="w", padx=22, pady=(0, 14))

        linha_busca = ctk.CTkFrame(card_busca, fg_color="transparent")
        linha_busca.grid(row=3, column=0, sticky="ew", padx=22, pady=(0, 4))
        linha_busca.grid_columnconfigure(0, weight=1)

        self.entry_cpf = ctk.CTkEntry(
            linha_busca, placeholder_text="000.000.000-00",
            font=ctk.CTkFont(family=theme.FONTE, size=15), height=46,
            corner_radius=10, fg_color=theme.FIELD, border_color=theme.FIELD_BORDER,
            text_color=theme.TEXTO,
        )
        self.entry_cpf.grid(row=0, column=0, sticky="ew")
        self.entry_cpf.bind("<Return>", lambda e: self._buscar())
        self.entry_cpf.bind("<KeyRelease>", self._ao_digitar_cpf)

        self.btn_limpar = ctk.CTkButton(
            linha_busca, text="", image=theme.icono("erro", 14), width=40, height=36,
            font=ctk.CTkFont(family=theme.FONTE, size=14, weight="bold"),
            fg_color=theme.FIELD, hover_color=theme.CARD_BORDER,
            text_color=theme.TEXTO_SEC, corner_radius=8, border_width=1,
            border_color=theme.FIELD_BORDER, command=self._limpar_campo,
        )
        self.btn_limpar.place(relx=1.0, rely=0.5, x=-160, anchor="e")
        theme.tooltip(self.btn_limpar, "Limpa o campo de CPF para digitar um novo número")

        self.btn_buscar = ctk.CTkButton(
            linha_busca, text="  Buscar", command=self._buscar,
            image=theme.icono("busca", 15), compound="left",
            width=140, height=46,
            font=ctk.CTkFont(family=theme.FONTE, size=14, weight="bold"),
            corner_radius=10, fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white",
        )
        self.btn_buscar.grid(row=0, column=1, padx=(12, 0))
        theme.tooltip(self.btn_buscar, "Busca o servidor pelo CPF digitado e exibe seus dados")

        ctk.CTkLabel(
            card_busca, text="  Dica: Você pode digitar com ou sem máscara",
            image=theme.icono("info", 14), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=11),
            text_color=theme.TEXTO_SEC, anchor="w",
        ).grid(row=4, column=0, sticky="w", padx=22, pady=(2, 10))

        self.lbl_status = ctk.CTkLabel(
            card_busca, text="", font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
            anchor="w",
        )
        self.lbl_status.grid(row=5, column=0, sticky="w", padx=22, pady=(0, 12))

        # ---------------------------------------------------------- métricas
        ultima = metricas.ultima()
        try:
            ultima_fmt = datetime_br(ultima) if ultima else "—"
        except ValueError:
            ultima_fmt = ultima

        cards_metricas = ctk.CTkFrame(conteudo, fg_color="transparent")
        cards_metricas.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        cards_metricas.grid_columnconfigure((0, 1, 2), weight=1, uniform="metric")

        self._card_metrica(cards_metricas, 0, "usuarios", "Servidores",
                            theme.fmt_num(metricas.total()),
                            "Total cadastrado", theme.GRADIENTE_AZUL)
        self._card_metrica(cards_metricas, 1, "processos", "Processos",
                            theme.fmt_num(metricas.geral()),
                            "Total de processos", theme.GRADIENTE_ROXO)
        self._card_metrica(cards_metricas, 2, "relojo", "Atualizado em", ultima_fmt,
                            "Última atualização", theme.GRADIENTE_CIANO)

        # --------------------------------------------------------- recentes
        card_recentes = theme.card(conteudo)
        card_recentes.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        card_recentes.grid_columnconfigure(0, weight=1)
        self._card_recentes_widget = card_recentes
        self._linhas_recentes = []

        ctk.CTkFrame(
            card_recentes, height=3, fg_color=theme.ROXO, corner_radius=2,
            border_width=0,
        ).grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        header_rec = ctk.CTkFrame(card_recentes, fg_color="transparent")
        header_rec.grid(row=1, column=0, sticky="ew", padx=20, pady=(14, 4))

        ctk.CTkLabel(
            header_rec, text="  Consultas Recentes", image=theme.icono("relojo", 14), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=15, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(side="left")

        limite = None if self._ver_todas else 3
        consultas = historico.obter_consultas(limite)
        if consultas:
            texto_btn = "Ver menos" if self._ver_todas else "Ver todas"
            btn_ver = ctk.CTkButton(
                header_rec, text=texto_btn, width=90, height=30,
                font=ctk.CTkFont(family=theme.FONTE, size=12),
                corner_radius=9, fg_color=theme.FIELD,
                hover_color=theme.CARD_BORDER,
                text_color=theme.ACCENT, border_width=1, border_color=theme.CARD_BORDER,
                command=self._alternar_todas,
            )
            btn_ver.pack(side="right")
            theme.tooltip(btn_ver, "Mostra ou oculta as consultas recentes antigas")

            for i, c in enumerate(consultas):
                self._linha_recente(card_recentes, i + 2, c)
        else:
            vazio = ctk.CTkLabel(
                card_recentes,
                text="  Nenhuma consulta realizada ainda.\nAs consultas que você fizer aparecerão aqui.",
            image=theme.icono("relojo", 14), compound="left",
                font=ctk.CTkFont(family=theme.FONTE, size=12),
                text_color=theme.TEXTO_SEC, justify="center",
            )
            vazio.grid(row=2, column=0, pady=20)
            self._vazio_widget = vazio

    def _card_metrica(self, parent, col, icone, titulo, valor, subtitulo, gradiente):
        card = theme.card(parent)
        card.grid(row=0, column=col, sticky="ew",
                  padx=(0, 12) if col < 2 else 0, pady=4)

        # Faixa colorida
        ctk.CTkFrame(
            card, height=3, fg_color=gradiente[0], corner_radius=2, border_width=0,
        ).pack(fill="x")

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(14, 0))

        icone_frame = ctk.CTkFrame(
            topo, width=36, height=36, corner_radius=10, fg_color=gradiente[0],
        )
        icone_frame.pack(side="left")
        icone_frame.pack_propagate(False)
        ctk.CTkLabel(
            icone_frame, text="", image=theme.icono(icone, 16),
            font=ctk.CTkFont(family=theme.FONTE, size=16), text_color="white",
        ).pack(expand=True)

        ctk.CTkLabel(
            topo, text=titulo, font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            card, text=valor, font=ctk.CTkFont(family=theme.FONTE, size=22, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(fill="x", padx=16, pady=(6, 0))

        ctk.CTkLabel(
            card, text=subtitulo, font=ctk.CTkFont(family=theme.FONTE, size=11),
            text_color=gradiente[0], anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 14))

    def _linha_recente(self, parent, row_index, consulta):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=row_index, column=0, sticky="ew", padx=20, pady=1)
        row.grid_columnconfigure(1, weight=1)

        widgets = [
            row,
            ctk.CTkLabel(row, text="", image=theme.icono("relojo", 12),
                     font=ctk.CTkFont(family=theme.FONTE, size=12), text_color=theme.TEXTO_SEC),
            ctk.CTkLabel(
                row, text=historico.mascarar_cpf(consulta.get("cpf")),
                font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
                text_color=theme.TEXTO, anchor="w",
            ),
            ctk.CTkLabel(
                row, text=consulta.get("nome", ""), anchor="w",
                font=ctk.CTkFont(family=theme.FONTE, size=12), text_color=theme.TEXTO_SEC,
            ),
            ctk.CTkLabel(
                row, text=historico.tempo_relativo(consulta.get("ts")),
                font=ctk.CTkFont(family=theme.FONTE, size=11), text_color=theme.TEXTO_SEC,
            ),
        ]
        widgets[1].grid(row=0, column=0, padx=(0, 10))
        widgets[2].grid(row=0, column=1, sticky="w")
        widgets[3].grid(row=0, column=2, sticky="w", padx=(24, 0))
        widgets[4].grid(row=0, column=3, sticky="e", padx=(24, 0))

        # Registra a linha para atualização rápida
        if hasattr(self, "_linhas_recentes"):
            self._linhas_recentes.append({"frame": row, "consulta": consulta})

        cpf = consulta.get("cpf")

        def _abrir(_e, cpf=cpf):
            self.entry_cpf.delete(0, "end")
            self.entry_cpf.insert(0, historico.mascarar_cpf(cpf))
            self._buscar()

        for w in widgets:
            w.configure(cursor="hand2")
            w.bind("<Button-1>", _abrir)

    # ============================================================= HANDLERS
    def _alternar_todas(self):
        self._ver_todas = not self._ver_todas
        self._montar_conteudo_busca()

    def _ao_digitar_cpf(self, evento=None):
        if evento and evento.keysym in ("BackSpace", "Delete", "Left", "Right", "Up", "Down", "Home", "End"):
            return
        atual = self.entry_cpf.get()
        formatado = formatar_cpf_digitado(atual)
        if formatado != atual:
            self.entry_cpf.delete(0, "end")
            self.entry_cpf.insert(0, formatado)

    def _limpar_campo(self):
        self.entry_cpf.delete(0, "end")
        self.entry_cpf.focus_set()

    def atualizar_metricas(self):
        """Recarrega métricas e consultas recentes (após importações etc.)."""
        self._montar_conteudo_busca()

    def _buscar(self):
        cpf = self.entry_cpf.get().strip()
        if not cpf:
            self.lbl_status.configure(text="⚠  Digite um CPF para buscar.", text_color=theme.LARANJA)
            return

        dados = db.buscar_por_cpf_flexivel(cpf)
        if not dados:
            self.lbl_status.configure(text="Nenhum registro encontrado.", text_color=theme.VERMELHO)
            return

        self.lbl_status.configure(text="", text_color=theme.TEXTO_SEC)
        self.dados_atuais = dados
        historico.registrar_consulta(dados.get("cpf"), dados.get("nome"))
        self._atualizar_consultas_recentes()
        self._montar_resultado(dados)
        self.view_busca.grid_forget()
        self.view_resultado.grid(row=0, column=0, sticky="nsew")

    def _atualizar_consultas_recentes(self):
        """Atualiza apenas a lista de consultas recentes (sem reconstruir a tela toda)."""
        if not hasattr(self, "_card_recentes_widget") or self._card_recentes_widget is None:
            return
        # Remove a mensagem de "vazio" se existir
        if hasattr(self, "_vazio_widget") and self._vazio_widget is not None:
            try:
                self._vazio_widget.destroy()
            except Exception:
                pass
            self._vazio_widget = None
        # Destroi apenas as linhas antigas
        for linha_info in self._linhas_recentes:
            try:
                linha_info["frame"].destroy()
            except Exception:
                pass
        self._linhas_recentes = []
        # Recria apenas as linhas
        limite = None if self._ver_todas else 3
        consultas = historico.obter_consultas(limite)
        if consultas:
            for i, c in enumerate(consultas):
                self._linha_recente(self._card_recentes_widget, i + 2, c)
        else:
            self._vazio_widget = ctk.CTkLabel(
                self._card_recentes_widget,
                text="  Nenhuma consulta realizada ainda.\nAs consultas que você fizer aparecerão aqui.",
            image=theme.icono("relojo", 14), compound="left",
                font=ctk.CTkFont(family=theme.FONTE, size=12),
                text_color=theme.TEXTO_SEC, justify="center",
            )
            self._vazio_widget.grid(row=2, column=0, pady=20)

    # ============================================================ RESULTADO
    def _criar_view_resultado(self):
        self.view_resultado = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.view_resultado.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            self.view_resultado, text="  Voltar à pesquisa", width=165, height=32,
            image=theme.icono("voltar", 14), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=12),
            corner_radius=8, fg_color="transparent",
            hover_color=(theme.CARD_BORDER[0], "#2E3542"),
            text_color=theme.AZUL_CLARO, anchor="w",
            command=self._voltar_pesquisa,
        ).grid(row=0, column=0, sticky="w", padx=4, pady=(4, 10))

    def _voltar_pesquisa(self):
        self.view_resultado.grid_forget()
        self._conteudo_resultado.destroy()
        self._conteudo_resultado = None
        self.view_busca.grid(row=0, column=0, sticky="nsew")

    def _montar_resultado(self, d):
        self._conteudo_resultado = ctk.CTkFrame(self.view_resultado, fg_color="transparent")
        self._conteudo_resultado.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 12))
        self._conteudo_resultado.grid_columnconfigure(0, weight=1)

        self._criar_header_resultado(d)
        self._criar_cards_resumo(d)
        self._criar_abas_resultado(d)

    def _criar_header_resultado(self, d):
        header = theme.card(self._conteudo_resultado)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.grid_columnconfigure(0, weight=1)

        corpo = ctk.CTkFrame(header, fg_color="transparent")
        corpo.pack(fill="x", padx=20, pady=18)
        corpo.grid_columnconfigure(1, weight=1)

        # avatar com iniciais
        nome = d.get("nome") or "?"
        iniciais = "".join(p[0] for p in nome.split()[:2]).upper() or "?"
        ctk.CTkLabel(
            corpo, text=iniciais, width=64, height=64, corner_radius=32,
            fg_color=theme.ROXO, font=ctk.CTkFont(family=theme.FONTE, size=20, weight="bold"),
            text_color="white",
        ).grid(row=0, column=0, rowspan=2, padx=(0, 16))

        info = ctk.CTkFrame(corpo, fg_color="transparent")
        info.grid(row=0, column=1, sticky="ew")
        info.grid_columnconfigure(0, weight=1)

        linha_nome = ctk.CTkFrame(info, fg_color="transparent")
        linha_nome.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            linha_nome, text=nome,
            font=ctk.CTkFont(family=theme.FONTE, size=18, weight="bold"),
            text_color=theme.TEXTO,
        ).pack(side="left", padx=(0, 10))

        texto_status, cor_txt, cor_bg = theme.status_badge_cores(d.get("status"))
        theme.badge(linha_nome, texto_status, cor_txt, cor_bg).pack(side="left", padx=(0, 6))
        if str(d.get("status_coleta_processos", "")).lower() == "ok":
            theme.badge(linha_nome, "Coletado", "#86efac", "#14532d").pack(side="left")

        sub = f"CPF: {historico.mascarar_cpf(d.get('cpf'))}"
        if d.get("matricula"):
            sub += f"      Matrícula: {d.get('matricula')}"
        ctk.CTkLabel(
            info, text=sub, font=ctk.CTkFont(family=theme.FONTE, size=12),
            text_color=theme.TEXTO_SEC, anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        # totais à direita
        totais = ctk.CTkFrame(corpo, fg_color="transparent")
        totais.grid(row=0, column=2, sticky="e", padx=(16, 0))

        ctk.CTkLabel(
            totais, text="Total de Processos",
            font=ctk.CTkFont(family=theme.FONTE, size=11), text_color=theme.TEXTO_SEC,
        ).grid(row=0, column=0, sticky="e")
        ctk.CTkLabel(
            totais, text=f"{int(d.get('qtdade_total_processos') or 0):02d}",
            font=ctk.CTkFont(family=theme.FONTE, size=24, weight="bold"),
            text_color=theme.TEXTO,
        ).grid(row=1, column=0, sticky="e")

        atualizado = d.get("data_atualizacao") or ""
        try:
            atualizado_fmt = datetime_br(atualizado) if atualizado else "—"
        except ValueError:
            atualizado_fmt = atualizado
        ctk.CTkLabel(
            totais, text=f"Atualizado em\n{atualizado_fmt}",
            font=ctk.CTkFont(family=theme.FONTE, size=11), text_color=theme.TEXTO_SEC,
            justify="right",
        ).grid(row=0, column=1, sticky="e", padx=(28, 0), rowspan=2)

    def _criar_cards_resumo(self, d):
        total = int(d.get("qtdade_total_processos") or 0)
        fazenda = int(d.get("qtdade_processos_fazenda") or 0)
        outros = int(d.get("qtdade_processos_outros") or 0)
        coleta_ok = str(d.get("status_coleta_processos", "")).lower() == "ok"

        frame = ctk.CTkFrame(self._conteudo_resultado, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="resumo")

        dados_cards = [
            ("Processos Fazenda", theme.fmt_num(fazenda), theme.fmt_pct(fazenda, total) + " do total"),
            ("Outros Processos", theme.fmt_num(outros), theme.fmt_pct(outros, total) + " do total"),
        ]
        for i, (titulo, valor, sub) in enumerate(dados_cards):
            card = theme.card(frame)
            card.grid(row=0, column=i, sticky="ew", padx=(0, 12) if i < 2 else 0)
            ctk.CTkLabel(
                card, text=titulo, font=ctk.CTkFont(family=theme.FONTE, size=11),
                text_color=theme.TEXTO_SEC, anchor="w",
            ).pack(fill="x", padx=16, pady=(14, 0))
            ctk.CTkLabel(
                card, text=valor, font=ctk.CTkFont(family=theme.FONTE, size=22, weight="bold"),
                text_color=theme.TEXTO, anchor="w",
            ).pack(fill="x", padx=16)
            ctk.CTkLabel(
                card, text=sub, font=ctk.CTkFont(family=theme.FONTE, size=11),
                text_color=theme.TEXTO_SEC, anchor="w",
            ).pack(fill="x", padx=16, pady=(0, 14))

        card_coleta = theme.card(frame)
        card_coleta.grid(row=0, column=2, sticky="ew")
        ctk.CTkLabel(
            card_coleta, text="Status da Coleta",
            font=ctk.CTkFont(family=theme.FONTE, size=11),
            text_color=theme.TEXTO_SEC, anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 0))
        ctk.CTkLabel(
            card_coleta, text="Concluída" if coleta_ok else "Pendente",
            font=ctk.CTkFont(family=theme.FONTE, size=18, weight="bold"),
            text_color=theme.VERDE if coleta_ok else theme.LARANJA, anchor="w",
        ).pack(fill="x", padx=16)
        ctk.CTkLabel(
            card_coleta, text="100% dos dados" if coleta_ok else "Coleta em andamento",
            font=ctk.CTkFont(family=theme.FONTE, size=11),
            text_color=theme.TEXTO_SEC, anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 14))





    # ================================================================= ABAS
    def _criar_abas_resultado(self, d):
        total_proc = int(d.get("qtdade_total_processos") or 0)
        abas = ctk.CTkTabview(
            self._conteudo_resultado, corner_radius=14,
            fg_color=theme.CARD, border_width=1, border_color=theme.CARD_BORDER,
            segmented_button_selected_color=theme.ACCENT,
            segmented_button_selected_hover_color=theme.ACCENT_HOVER,
            segmented_button_fg_color=theme.FIELD,
            segmented_button_unselected_color=theme.FIELD,
            text_color=theme.TEXTO,
        )
        abas.grid(row=2, column=0, sticky="ew")
        aba_dados = abas.add("Dados Pessoais")
        aba_proc = abas.add(f"Processos ({total_proc})")
        aba_resumo = abas.add("Resumo Geral")

        for aba in (aba_dados, aba_proc, aba_resumo):
            aba.grid_columnconfigure(0, weight=1)

        self._preencher_aba_dados(aba_dados, d)
        self._preencher_aba_processos(aba_proc, d)
        self._preencher_aba_resumo(aba_resumo, d)

    def _preencher_aba_dados(self, aba, d):
        conteudo = ctk.CTkFrame(aba, fg_color="transparent")
        conteudo.grid(row=0, column=0, sticky="nsew", padx=18, pady=14)
        conteudo.grid_columnconfigure(0, weight=1)
        conteudo.grid_columnconfigure(1, weight=1)
        conteudo.grid_columnconfigure(2, weight=1)

        col_esq = [
            ("Nome Completo", d.get("nome")),
            ("RG", d.get("rg")),
            ("Status", d.get("status")),
            ("Especificidade", d.get("especificidade")),
        ]
        col_meio = [
            ("CPF", historico.mascarar_cpf(d.get("cpf"))),
            ("Matrícula", d.get("matricula")),
            ("Origem da Informação", d.get("origem_info")),
            ("Lista APEO", d.get("lista_apeo")),
        ]

        for col, campos in ((0, col_esq), (1, col_meio)):
            frame_col = ctk.CTkFrame(conteudo, fg_color="transparent")
            frame_col.grid(row=0, column=col, sticky="new", padx=(0, 14))
            frame_col.grid_columnconfigure(1, weight=1)
            for i, (label, valor) in enumerate(campos):
                ctk.CTkLabel(
                    frame_col, text=label, font=ctk.CTkFont(family=theme.FONTE, size=11),
                    text_color=theme.TEXTO_SEC, anchor="w",
                ).grid(row=i * 2, column=0, columnspan=2, sticky="w", pady=(8, 1))
                texto_valor = str(valor) if valor else "Não informado"
                cor_valor = theme.TEXTO if valor else theme.TEXTO_SEC
                if label == "Status" and valor:
                    texto_valor, cor_txt, cor_bg = theme.status_badge_cores(valor)
                    theme.badge(frame_col, texto_valor, cor_txt, cor_bg, tamanho=10)\
                        .grid(row=i * 2 + 1, column=0, sticky="w")
                else:
                    ctk.CTkLabel(
                        frame_col, text=texto_valor,
                        font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
                        text_color=cor_valor, anchor="w",
                    ).grid(row=i * 2 + 1, column=0, columnspan=2, sticky="w")

        # card de resumo à direita
        card_resumo = ctk.CTkFrame(
            conteudo, fg_color=theme.FIELD, corner_radius=12,
            border_width=1, border_color=theme.CARD_BORDER,
        )
        card_resumo.grid(row=0, column=2, sticky="new")
        ctk.CTkLabel(
            card_resumo, text="Resumo",
            font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 6))

        total = int(d.get("qtdade_total_processos") or 0)
        coleta_ok = str(d.get("status_coleta_processos", "")).lower() == "ok"
        linhas = [
            ("Total de Processos", f"{total:02d}"),
            ("Processos Fazenda", theme.fmt_num(d.get("qtdade_processos_fazenda") or 0)),
            ("Outros Processos", theme.fmt_num(d.get("qtdade_processos_outros") or 0)),
            ("Coleta", "Concluída" if coleta_ok else "Pendente"),
        ]
        for label, valor in linhas:
            linha = ctk.CTkFrame(card_resumo, fg_color="transparent")
            linha.pack(fill="x", padx=16, pady=3)
            ctk.CTkLabel(
                linha, text=label, font=ctk.CTkFont(family=theme.FONTE, size=11),
                text_color=theme.TEXTO_SEC, anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                linha, text=valor, font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
                text_color=theme.TEXTO, anchor="e",
            ).pack(side="right")
        ctk.CTkLabel(card_resumo, text="").pack(pady=(0, 8))


    def _extrair_processos(self, texto, origem):
        numeros = REGEX_PROCESSO.findall(str(texto or ""))
        return [{"numero": n, "origem": origem} for n in numeros]

    def _preencher_aba_processos(self, aba, d):
        processos = self._extrair_processos(d.get("processos_fazenda"), "Fazenda")
        processos += self._extrair_processos(d.get("processos_outros"), "Outros")

        conteudo = ctk.CTkFrame(aba, fg_color="transparent")
        conteudo.grid(row=0, column=0, sticky="nsew", padx=18, pady=14)
        conteudo.grid_columnconfigure(0, weight=1)

        if not processos:
            ctk.CTkLabel(
                conteudo, text="Nenhum processo relacionado a este servidor.",
                font=ctk.CTkFont(family=theme.FONTE, size=12),
                text_color=theme.TEXTO_SEC,
            ).grid(row=1, column=0, pady=24)
            return

        # cabeçalho da tabela
        header = ctk.CTkFrame(conteudo, fg_color=theme.FIELD, corner_radius=10)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        for texto, ancor, col in [("Nº do Processo", "w", 0), ("Origem", "center", 1), ("Resumo", "w", 2), ("Ações", "e", 3)]:
            ctk.CTkLabel(
                header, text=texto,
                font=ctk.CTkFont(family=theme.FONTE, size=11, weight="bold"),
                text_color=theme.TEXTO_SEC, anchor=ancor,
            ).grid(row=0, column=col, sticky="ew",
                   padx=14 if col in (0, 3) else 6, pady=8)

        for i, proc in enumerate(processos):
            row = ctk.CTkFrame(
                conteudo, fg_color=theme.FIELD if i % 2 == 0 else "transparent",
                corner_radius=10,
            )
            row.grid(row=i + 1, column=0, sticky="ew", pady=1)
            row.grid_columnconfigure(0, weight=3)
            row.grid_columnconfigure(2, weight=2)

            ctk.CTkLabel(
                row, text=proc["numero"],
                font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
                text_color=theme.TEXTO, anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=14, pady=7)

            if proc["origem"] == "Fazenda":
                theme.badge(row, "Fazenda", "#7FB0EA", "#1B3A74", tamanho=10)\
                    .grid(row=0, column=1, padx=6)
            else:
                theme.badge(row, "Outros", "#fcd34d", "#78350f", tamanho=10)\
                    .grid(row=0, column=1, padx=6)

            ctk.CTkLabel(
                row, text=f"Processo {proc['origem'].lower()} do servidor",
                font=ctk.CTkFont(family=theme.FONTE, size=11),
                text_color=theme.TEXTO_SEC, anchor="w",
            ).grid(row=0, column=2, sticky="w", padx=6)

            btn_ver_proc = ctk.CTkButton(
                row, text="", width=32, height=28,
                image=theme.icono("olho", 14),
                font=ctk.CTkFont(family=theme.FONTE, size=12),
                corner_radius=8, fg_color="transparent",
                hover_color=theme.CARD_BORDER, text_color=theme.AZUL_CLARO,
                command=lambda n=proc["numero"], o=proc["origem"]: self._detalhe_processo(n, o),
            )
            btn_ver_proc.grid(row=0, column=3, sticky="e", padx=10)
            theme.tooltip(btn_ver_proc, "Exibe os detalhes do processo")

        btn_todos = ctk.CTkButton(
            conteudo, text="  Ver todos os processos",
            image=theme.icono("procesos", 14), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=11, weight="bold"),
            height=30, corner_radius=8, fg_color="transparent",
            hover_color=(theme.CARD_BORDER[0], "#2E3542"),
            text_color=theme.AZUL_CLARO,
            command=lambda: self._popup_processos(processos),
        )
        btn_todos.grid(row=len(processos) + 1, column=0, pady=(12, 2))
        theme.tooltip(btn_todos, "Abre uma janela com todos os processos listados")

    def _detalhe_processo(self, numero, origem):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Processo {numero}")
        popup.geometry("440x220")
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        popup.resizable(False, False)
        theme.preparar_popup(popup)

        popup.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            popup, text=numero,
            font=ctk.CTkFont(family=theme.FONTE, size=16, weight="bold"),
            text_color=theme.TEXTO,
        ).grid(row=0, column=0, pady=(24, 6))
        theme.badge(
            popup, "Origem: " + origem,
            "#7FB0EA" if origem == "Fazenda" else "#fcd34d",
            "#1B3A74" if origem == "Fazenda" else "#78350f",
        ).grid(row=1, column=0, pady=4)
        ctk.CTkLabel(
            popup, text="Detalhes completos do processo não constam na base.\nSomente o número é armazenado na planilha importada.",
            font=ctk.CTkFont(family=theme.FONTE, size=11),
            text_color=theme.TEXTO_SEC, justify="center",
        ).grid(row=2, column=0, pady=(10, 18), padx=24)
        theme.exibir_popup(popup)

    def _popup_processos(self, processos):
        popup = ctk.CTkToplevel(self)
        popup.title("Todos os processos")
        popup.geometry("520x420")
        theme.preparar_popup(popup)
        popup.transient(self.winfo_toplevel())

        popup.grid_rowconfigure(1, weight=1)
        popup.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            popup, text=f"{len(processos)} processo(s) relacionado(s)",
            font=ctk.CTkFont(family=theme.FONTE, size=14, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 8))

        scroll = ctk.CTkScrollableFrame(popup, fg_color=theme.FIELD, corner_radius=10)
        scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 16))
        for proc in processos:
            linha = ctk.CTkFrame(scroll, fg_color="transparent")
            linha.pack(fill="x", pady=2, padx=8)
            ctk.CTkLabel(
                linha, text=proc["numero"],
                font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
                text_color=theme.TEXTO, anchor="w",
            ).pack(side="left")
            cor_txt, cor_bg = (("#7FB0EA", "#1B3A74") if proc["origem"] == "Fazenda" else ("#fcd34d", "#78350f"))
            theme.badge(linha, proc["origem"], cor_txt, cor_bg, tamanho=10).pack(side="right")

        theme.exibir_popup(popup)

    def _preencher_aba_resumo(self, aba, d):
        qtd_fazenda = int(d.get("qtdade_processos_fazenda") or 0)
        qtd_outros = int(d.get("qtdade_processos_outros") or 0)
        qtd_total = int(d.get("qtdade_total_processos") or 0)

        conteudo = ctk.CTkFrame(aba, fg_color="transparent")
        conteudo.grid(row=0, column=0, sticky="nsew", padx=18, pady=14)
        conteudo.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            conteudo,
            text=(
                f"Resumo: {qtd_fazenda} processo(s) na Fazenda  |  "
                f"{qtd_outros} outro(s)  |  Total: {qtd_total}"
            ),
            font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
            text_color=theme.AZUL_CLARO, anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        blocos = [
            ("Processos na Fazenda", d.get("processos_fazenda"), qtd_fazenda, 1),
            ("Outros Processos", d.get("processos_outros"), qtd_outros, 4),
        ]
        for titulo, texto, qtd, linha_base in blocos:
            header = ctk.CTkFrame(conteudo, fg_color="transparent")
            header.grid(row=linha_base, column=0, sticky="w", pady=(8, 4))
            ctk.CTkLabel(
                header, text=titulo,
                font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
                text_color=theme.TEXTO, anchor="w",
            ).pack(side="left")
            theme.badge(header, theme.fmt_num(qtd), "#7FB0EA", "#1B3A74", tamanho=10)\
                .pack(side="left", padx=(8, 0))

            caixa = ctk.CTkTextbox(
                conteudo, height=110, wrap="word",
                font=ctk.CTkFont(family=theme.FONTE, size=12),
                corner_radius=10, fg_color=theme.FIELD,
                border_width=1, border_color=theme.CARD_BORDER,
                text_color=theme.TEXTO,
            )
            caixa.grid(row=linha_base + 1, column=0, sticky="ew", pady=(0, 8))
            caixa.insert("1.0", str(texto) if texto else "Nenhum processo.")
            caixa.configure(state="disabled")

