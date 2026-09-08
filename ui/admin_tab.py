import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from database import cache as metricas
from ui import theme
from ui import historico

db = DatabaseManager()


class AdminTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.dados_editando = None
        self._criar_login()

    # ============================================================= LOGIN
    def _criar_login(self):
        self.frame_login = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_login.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        self.frame_login.grid_columnconfigure(0, weight=1)

        card = theme.card(self.frame_login)
        card.pack(expand=True, fill="both", padx=20, pady=10)
        card.grid_columnconfigure(0, weight=1)

        # Faixa colorida superior
        ctk.CTkFrame(
            card, height=4, fg_color=theme.ROXO, corner_radius=2, border_width=0,
        ).pack(fill="x", padx=20, pady=(20, 0))

        # Ícone grande + título
        ctk.CTkLabel(
            card, text="", image=theme.icono("clave", 46),
            font=ctk.CTkFont(family=theme.FONTE, size=46),
        ).pack(pady=(20, 6))
        ctk.CTkLabel(
            card, text="Acesso Administrativo",
            font=ctk.CTkFont(family=theme.FONTE, size=26, weight="bold"),
            text_color=theme.TEXTO,
        ).pack(pady=(0, 4))
        ctk.CTkLabel(
            card, text="  Área restrita para gestão de registros e configurações", image=theme.icono("escudo", 14), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=13),
            text_color=theme.TEXTO_SEC,
        ).pack(pady=(0, 24))

        # Formulário central
        frame_center = ctk.CTkFrame(card, fg_color="transparent")
        frame_center.pack(expand=True, fill="both", padx=40, pady=(0, 30))
        frame_center.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame_center, text="  Senha de administrador", image=theme.icono("clave", 14), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=14, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(anchor="w", pady=(0, 8))

        self.entry_senha = ctk.CTkEntry(
            frame_center, show="*", placeholder_text="Digite sua senha",
            font=ctk.CTkFont(family=theme.FONTE, size=15), height=46,
            corner_radius=10, fg_color=theme.FIELD, border_color=theme.FIELD_BORDER,
            text_color=theme.TEXTO,
        )
        self.entry_senha.pack(fill="x", pady=(0, 14))
        self.entry_senha.bind("<Return>", lambda e: self._verificar_login())

        self.btn_login = ctk.CTkButton(
            frame_center, text="Entrar  →", command=self._verificar_login,
            height=46, font=ctk.CTkFont(family=theme.FONTE, size=15, weight="bold"),
            corner_radius=10, fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white",
        )
        self.btn_login.pack(fill="x")

        self.lbl_login_status = ctk.CTkLabel(
            frame_center, text="",
            font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
        )
        self.lbl_login_status.pack(pady=12)

    def _verificar_login(self):
        senha = self.entry_senha.get().strip()
        if senha == db.get_admin_senha():
            self.frame_login.destroy()
            historico.registrar_evento("admin_login", "Login administrativo realizado")
            self._criar_painel_admin()
        else:
            self.lbl_login_status.configure(
                text="❌  Senha incorreta!", text_color=theme.VERMELHO,
            )

    # ====================================================== PAINEL ADMIN
    def _criar_painel_admin(self):
        self.frame_admin = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_admin.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.frame_admin.grid_columnconfigure(0, weight=1)
        self.frame_admin.grid_rowconfigure(0, weight=1)

        # Scrollable para comportar todo o conteúdo
        scroll = ctk.CTkScrollableFrame(self.frame_admin, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        self._criar_header_admin(scroll)
        self._criar_metricas_admin(scroll)
        self._criar_abas_admin(scroll)

    def _criar_header_admin(self, scroll):
        header = theme.card(scroll)
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(12, 16))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(
            header, height=4, fg_color=theme.ACCENT, corner_radius=2, border_width=0,
        ).pack(fill="x", padx=20, pady=(18, 0))

        body = ctk.CTkFrame(header, fg_color="transparent")
        body.pack(fill="x", padx=22, pady=14)
        body.grid_columnconfigure(1, weight=1)

        # Avatar / ícone
        av = ctk.CTkFrame(
            body, width=56, height=56, corner_radius=28, fg_color=theme.GRADIENTE_AZUL[0],
        )
        av.grid(row=0, column=0, padx=(0, 14))
        av.pack_propagate(False)
        ctk.CTkLabel(
            av, text="", image=theme.icono("escudo", 24),
            font=ctk.CTkFont(family=theme.FONTE, size=24, weight="bold"),
            text_color="white",
        ).pack(expand=True)

        info = ctk.CTkFrame(body, fg_color="transparent")
        info.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(
            info, text="  Painel Administrativo", image=theme.icono("admin", 16), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=22, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            info, text="  Bem-vindo! Gerencie registros, configurações e monitore o sistema", image=theme.icono("pessoa", 14), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=13),
            text_color=theme.TEXTO_SEC, anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Botão de logout
        ctk.CTkButton(
            body, text="  Sair", command=self._logout, image=theme.icono("sair", 14), compound="left",
            width=110, height=38,
            font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
            corner_radius=10, fg_color=theme.VERMELHO, hover_color=theme.VERMELHO_HOVER,
            text_color="white",
        ).grid(row=0, column=2, padx=(12, 0))

    def _logout(self):
        if messagebox.askyesno("Sair", "Deseja encerrar a sessão administrativa?"):
            self.frame_admin.destroy()
            self.dados_editando = None
            self._criar_login()

    def _criar_metricas_admin(self, scroll):
        frame = ctk.CTkFrame(scroll, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 16))
        for i in range(4):
            frame.grid_columnconfigure(i, weight=1, uniform="m")

        m = metricas.obter_metricas()
        total = m["total"]
        total_proc = m["geral"]
        fazenda = m["fazenda"]
        outros = m["outros"]

        dados = [
            ("usuarios", "Servidores", theme.fmt_num(total), "Total na base", theme.GRADIENTE_AZUL),
            ("processos", "Processos", theme.fmt_num(total_proc),
             f"{(total_proc / total if total else 0):.1f} por servidor", theme.GRADIENTE_ROXO),
            ("fazenda", "Fazenda", theme.fmt_num(fazenda),
             theme.fmt_pct(fazenda, total_proc) + " do total", theme.GRADIENTE_CIANO),
            ("arquivo", "Outros", theme.fmt_num(outros),
             theme.fmt_pct(outros, total_proc) + " do total", theme.GRADIENTE_LARANJA),
        ]
        for i, (icon, titulo, valor, sub, grad) in enumerate(dados):
            c = theme.card(frame)
            c.grid(row=0, column=i, sticky="ew", padx=(0, 12) if i < 3 else 0, pady=4)
            ctk.CTkFrame(c, height=3, fg_color=grad[0], corner_radius=2,
                         border_width=0).pack(fill="x")
            topo = ctk.CTkFrame(c, fg_color="transparent")
            topo.pack(fill="x", padx=16, pady=(14, 0))
            box = ctk.CTkFrame(topo, width=36, height=36, corner_radius=10, fg_color=grad[0])
            box.pack(side="left")
            box.pack_propagate(False)
            ctk.CTkLabel(box, text="", image=theme.icono(icon, 16), text_color="white",
                         font=ctk.CTkFont(family=theme.FONTE, size=16)).pack(expand=True)
            ctk.CTkLabel(topo, text=titulo,
                         font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
                         text_color=theme.TEXTO, anchor="w").pack(side="left", padx=(10, 0))
            ctk.CTkLabel(c, text=valor,
                         font=ctk.CTkFont(family=theme.FONTE, size=22, weight="bold"),
                         text_color=theme.TEXTO, anchor="w").pack(fill="x", padx=16, pady=(6, 0))
            ctk.CTkLabel(c, text=sub,
                         font=ctk.CTkFont(family=theme.FONTE, size=11, weight="bold"),
                         text_color=grad[0], anchor="w").pack(fill="x", padx=16, pady=(0, 14))

    def _criar_abas_admin(self, scroll):
        # Abas internas para organizar o painel
        self.abas = ctk.CTkTabview(
            scroll, corner_radius=14,
            fg_color=theme.CARD, border_width=1, border_color=theme.CARD_BORDER,
            segmented_button_selected_color=theme.ACCENT,
            segmented_button_selected_hover_color=theme.ACCENT_HOVER,
            segmented_button_fg_color=theme.FIELD,
            segmented_button_unselected_color=theme.FIELD,
            text_color=theme.TEXTO,
        )
        self.abas.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 16))
        self.abas.add("Editar Registro")
        self.abas.add("Buscar Pessoas")
        self.abas.add("Ações Rápidas")
        self.abas.add("Atividades Recentes")

        aba_editar = self.abas.tab("Editar Registro")
        aba_busca = self.abas.tab("Buscar Pessoas")
        aba_acoes = self.abas.tab("Ações Rápidas")
        aba_ativ = self.abas.tab("Atividades Recentes")

        # Iconos nas abas
        for nome_aba, icon_nome in [
            ("Editar Registro", "editar"),
            ("Buscar Pessoas", "busca"),
            ("Ações Rápidas", "raio"),
            ("Atividades Recentes", "logs"),
        ]:
            try:
                boto = self.abas._segmented_button._buttons_dict.get(nome_aba)
                if boto is not None:
                    boto.configure(
                        image=theme.icono(icon_nome, 14),
                        compound="left",
                        text=nome_aba,
                    )
            except Exception:
                pass

        # Iconos nas abas
        for nome_aba, icon_nome in [
            ("Editar Registro", "editar"),
            ("Buscar Pessoas", "busca"),
            ("Ações Rápidas", "raio"),
            ("Atividades Recentes", "logs"),
        ]:
            try:
                boto = self.abas._segmented_button._buttons_dict.get(nome_aba)
                if boto is not None:
                    boto.configure(
                        image=theme.icono(icon_nome, 14),
                        compound="left",
                        text=nome_aba,
                    )
            except Exception:
                pass

        # Iconos nas abas
        for nome_aba, icon_nome in [
            ("Editar Registro", "editar"),
            ("Buscar Pessoas", "busca"),
            ("Ações Rápidas", "raio"),
            ("Atividades Recentes", "logs"),
        ]:
            try:
                boto = self.abas._segmented_button._buttons_dict.get(nome_aba)
                if boto is not None:
                    boto.configure(
                        image=theme.icono(icon_nome, 14),
                        compound="left",
                        text=nome_aba,
                    )
            except Exception:
                pass

        # Iconos nas abas
        for nome_aba, icon_nome in [
            ("Editar Registro", "editar"),
            ("Buscar Pessoas", "busca"),
            ("Ações Rápidas", "raio"),
            ("Atividades Recentes", "logs"),
        ]:
            try:
                boto = self.abas._segmented_button._buttons_dict.get(nome_aba)
                if boto is not None:
                    boto.configure(
                        image=theme.icono(icon_nome, 14),
                        compound="left",
                        text=nome_aba,
                    )
            except Exception:
                pass

        # Iconos nas abas
        for nome_aba, icon_nome in [
            ("Editar Registro", "editar"),
            ("Buscar Pessoas", "busca"),
            ("Ações Rápidas", "raio"),
            ("Atividades Recentes", "logs"),
        ]:
            try:
                boto = self.abas._segmented_button._buttons_dict.get(nome_aba)
                if boto is not None:
                    boto.configure(
                        image=theme.icono(icon_nome, 14),
                        compound="left",
                        text=nome_aba,
                    )
            except Exception:
                pass

        for aba in (aba_editar, aba_busca, aba_acoes, aba_ativ):
            aba.grid_columnconfigure(0, weight=1)

        self._criar_aba_editar(aba_editar)
        self._criar_aba_busca(aba_busca)
        self._criar_aba_acoes(aba_acoes)
        self._criar_aba_atividades(aba_ativ)

    # ======================================================== ABA EDITAR
    def _criar_aba_editar(self, aba):
        wrapper = ctk.CTkFrame(aba, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew", padx=18, pady=14)
        wrapper.grid_columnconfigure(0, weight=1)

        # Instruções
        ctk.CTkLabel(
            wrapper,
            text="  Busque um servidor pelo CPF para carregar e editar os dados", image=theme.icono("busca", 14), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=13),
            text_color=theme.TEXTO_SEC, anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        # Barra de busca
        busca = ctk.CTkFrame(wrapper, fg_color="transparent")
        busca.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        busca.grid_columnconfigure(0, weight=1)

        self.entry_busca_cpf = ctk.CTkEntry(
            busca, placeholder_text="000.000.000-00",
            font=ctk.CTkFont(family=theme.FONTE, size=14), height=42,
            corner_radius=10, fg_color=theme.FIELD, border_color=theme.FIELD_BORDER,
        )
        self.entry_busca_cpf.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_busca_cpf.bind("<Return>", lambda e: self._carregar_edicao())

        ctk.CTkButton(
            busca, text="  Carregar", command=self._carregar_edicao, image=theme.icono("importacao", 14), compound="left",
            width=140, height=42,
            font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
            corner_radius=10, fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white",
        ).grid(row=0, column=1, padx=(0, 8))

        ctk.CTkButton(
            busca, text="  Deletar", command=self._deletar_registro, image=theme.icono("deletar", 14), compound="left",
            width=130, height=42,
            font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
            corner_radius=10, fg_color=theme.VERMELHO, hover_color=theme.VERMELHO_HOVER,
            text_color="white",
        ).grid(row=0, column=2)

        # Formulário
        self.form_card = theme.card(wrapper)
        self.form_card.grid(row=2, column=0, sticky="ew")
        self.form_card.grid_columnconfigure(0, weight=1)
        ctk.CTkFrame(
            self.form_card, height=3, fg_color=theme.GRADIENTE_VERDE[0],
            corner_radius=2, border_width=0,
        ).pack(fill="x")

        ctk.CTkLabel(
            self.form_card, text="  Dados do Registro", image=theme.icono("nota", 14), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=15, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(anchor="w", padx=22, pady=(14, 6))

        self.frame_form = ctk.CTkScrollableFrame(self.form_card, fg_color="transparent", height=380)
        self.frame_form.pack(fill="x", padx=20, pady=(0, 12))
        self.frame_form.grid_columnconfigure(1, weight=1)

        self.campos_form = {}
        labels = [
            ("cpf", "CPF (somente leitura)", "pessoa"),
            ("nome", "Nome", "nota"),
            ("rg", "RG", "documento"),
            ("matricula", "Matrícula", "calendario"),
            ("status", "Status", "grafico"),
            ("origem_info", "Origem Info", "pessoa"),
            ("lista_apeo", "Lista APEO", "processos"),
            ("especificidade", "Especificidade", "etiqueta"),
            ("qtdade_processos_fazenda", "Qtd. Processos Fazenda", "fazenda"),
            ("qtdade_processos_outros", "Qtd. Processos Outros", "arquivo"),
            ("qtdade_total_processos", "Qtd. Total Processos", "calendario"),
            ("status_coleta_processos", "Status Coleta", "check"),
        ]
        for i, (key, label, icone) in enumerate(labels):
            ctk.CTkLabel(
                self.frame_form, text=f"  {label}", image=theme.icono(icone, 12), compound="left",
                font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
                text_color=theme.TEXTO_SEC, anchor="w",
            ).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            entry = ctk.CTkEntry(
                self.frame_form, font=ctk.CTkFont(family=theme.FONTE, size=12),
                height=36, corner_radius=8, fg_color=theme.FIELD,
                border_color=theme.FIELD_BORDER,
            )
            entry.grid(row=i, column=1, sticky="ew", padx=10, pady=5)
            self.campos_form[key] = entry

        self.campos_form["cpf"].configure(state="disabled")

        # Botões
        btn_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=22, pady=(0, 16))
        ctk.CTkButton(
            btn_frame, text="  Salvar Alterações", command=self._salvar_alteracoes,
            image=theme.icono("salvar", 14), compound="left",
            height=42, font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
            corner_radius=10, fg_color=theme.VERDE, hover_color=theme.VERDE_HOVER,
            text_color="white",
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            btn_frame, text="  Limpar", command=self._limpar_form,
            image=theme.icono("atualizar", 14), compound="left",
            width=130, height=42,
            font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
            corner_radius=10, fg_color=theme.FIELD, hover_color=theme.CARD_BORDER,
            text_color=theme.TEXTO, border_width=1, border_color=theme.CARD_BORDER,
        ).pack(side="left")

        self.lbl_admin_status = ctk.CTkLabel(
            self.form_card, text="",
            font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
        )
        self.lbl_admin_status.pack(pady=(0, 14))

    def _limpar_form(self):
        self.dados_editando = None
        for key, entry in self.campos_form.items():
            if key == "cpf":
                entry.configure(state="normal")
            entry.delete(0, "end")
            if key == "cpf":
                entry.configure(state="disabled")
        self.lbl_admin_status.configure(text="", text_color=theme.TEXTO_SEC)

    # ======================================================== ABA BUSCA
    def _criar_aba_busca(self, aba):
        wrapper = ctk.CTkFrame(aba, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew", padx=18, pady=14)
        wrapper.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            wrapper,
            text="  Pesquise servidores pelo nome (máx. 30 resultados)", image=theme.icono("busca", 14), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=13),
            text_color=theme.TEXTO_SEC, anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        busca = ctk.CTkFrame(wrapper, fg_color="transparent")
        busca.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        busca.grid_columnconfigure(0, weight=1)

        self.entry_busca_nome = ctk.CTkEntry(
            busca, placeholder_text="Digite parte do nome e pressione Enter",
            font=ctk.CTkFont(family=theme.FONTE, size=14), height=42,
            corner_radius=10, fg_color=theme.FIELD, border_color=theme.FIELD_BORDER,
        )
        self.entry_busca_nome.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_busca_nome.bind("<Return>", lambda e: self._buscar_pessoas())

        ctk.CTkButton(
            busca, text="  Buscar", command=self._buscar_pessoas, image=theme.icono("busca", 14), compound="left",
            width=130, height=42,
            font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
            corner_radius=10, fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white",
        ).grid(row=0, column=1)

        self.frame_resultados = ctk.CTkScrollableFrame(
            wrapper, fg_color=theme.CARD, corner_radius=10,
            border_width=1, border_color=theme.CARD_BORDER, height=420,
        )
        self.frame_resultados.grid(row=2, column=0, sticky="nsew", pady=(0, 4))
        self.frame_resultados.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.frame_resultados,
            text="  Digite um nome para pesquisar.",
            image=theme.icono("info", 14), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=12),
            text_color=theme.TEXTO_SEC,
        ).grid(row=0, column=0, pady=24)

    def _buscar_pessoas(self):
        termo = self.entry_busca_nome.get().strip()
        for w in self.frame_resultados.winfo_children():
            w.destroy()
        if not termo:
            ctk.CTkLabel(
                self.frame_resultados, text="  Digite um nome para pesquisar.",
            image=theme.icono("info", 14), compound="left",
                font=ctk.CTkFont(family=theme.FONTE, size=12),
                text_color=theme.TEXTO_SEC,
            ).grid(row=0, column=0, pady=24)
            return

        resultados = db.buscar_por_nome(termo)[:30]
        if not resultados:
            ctk.CTkLabel(
                self.frame_resultados, text="  Nenhum servidor encontrado.",
            image=theme.icono("pessoa", 14), compound="left",
                font=ctk.CTkFont(family=theme.FONTE, size=12),
                text_color=theme.TEXTO_SEC,
            ).grid(row=0, column=0, pady=24)
            return

        # Cabeçalho
        header = ctk.CTkFrame(self.frame_resultados, fg_color=theme.FIELD, corner_radius=8)
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        for txt, col in (("Nome", 0), ("CPF", 1), ("Status", 2), ("Ações", 3)):
            ctk.CTkLabel(
                header, text=txt,
                font=ctk.CTkFont(family=theme.FONTE, size=11, weight="bold"),
                text_color=theme.TEXTO_SEC, anchor="w",
            ).grid(row=0, column=col, sticky="ew", padx=12, pady=8)
        header.grid_columnconfigure(0, weight=2)
        header.grid_columnconfigure(1, weight=1)

        for i, p in enumerate(resultados):
            row = ctk.CTkFrame(
                self.frame_resultados, fg_color=theme.FIELD if i % 2 == 0 else "transparent",
                corner_radius=8,
            )
            row.grid(row=i + 1, column=0, sticky="ew", padx=8, pady=1)
            row.grid_columnconfigure(0, weight=2)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row, text=p.get("nome", ""),
                font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
                text_color=theme.TEXTO, anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=12, pady=8)

            ctk.CTkLabel(
                row, text=historico.mascarar_cpf(p.get("cpf", "")),
                font=ctk.CTkFont(family=theme.FONTE, size=11),
                text_color=theme.TEXTO_SEC, anchor="w",
            ).grid(row=0, column=1, sticky="w", padx=12, pady=8)

            status_texto, cor_txt, cor_bg = theme.status_badge_cores(p.get("status"))
            theme.badge(row, status_texto, cor_txt, cor_bg, tamanho=10).grid(
                row=0, column=2, padx=10, pady=8,
            )

            ctk.CTkButton(
                row, text="  Editar", image=theme.icono("editar", 14), compound="left", width=100, height=28,
                font=ctk.CTkFont(family=theme.FONTE, size=11, weight="bold"),
                corner_radius=8, fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
                text_color="white",
                command=lambda cpf=p.get("cpf"): self._carregar_por_cpf(cpf),
            ).grid(row=0, column=3, padx=10, pady=8)

    def _carregar_por_cpf(self, cpf):
        self.abas.set("Editar Registro")
        self.entry_busca_cpf.delete(0, "end")
        self.entry_busca_cpf.insert(0, cpf)
        self._carregar_edicao()

    # ======================================================= ABA AÇÕES
    def _criar_aba_acoes(self, aba):
        wrapper = ctk.CTkFrame(aba, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew", padx=18, pady=14)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            wrapper,
            text="  Ações administrativas do sistema", image=theme.icono("raio", 14), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=13),
            text_color=theme.TEXTO_SEC, anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        acoes = [
            ("clave", "Alterar Senha Admin",
             "Defina uma nova senha para o painel administrativo",
             theme.GRADIENTE_AZUL, self._alterar_senha, 0, 0),
            ("dashboard", "Ver Estatísticas",
             "Resumo detalhado dos dados do sistema",
             theme.GRADIENTE_ROXO, self._popup_stats, 0, 1),
            ("atualizar", "Recarregar Dados",
             "Atualiza os dados da tela atual",
             theme.GRADIENTE_CIANO, self._recarregar_metricas, 1, 0),
            ("alerta", "Limpar Todos os Dados",
             "Remove permanentemente todos os registros",
             theme.GRADIENTE_ROSA, self._limpar_tudo, 1, 1),
        ]
        for icon, titulo, desc, grad, cmd, linha, coluna in acoes:
            self._criar_card_acao(wrapper, icon, titulo, desc, grad, cmd, linha, coluna)

    def _criar_card_acao(self, parent, icon, titulo, desc, grad, cmd, linha, coluna):
        c = theme.card(parent)
        c.grid(row=linha + 1, column=coluna, sticky="nsew",
               padx=(0, 12) if coluna == 0 else (12, 0), pady=6)
        ctk.CTkFrame(c, height=3, fg_color=grad[0], corner_radius=2,
                     border_width=0).pack(fill="x")
        topo = ctk.CTkFrame(c, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(topo, text="", image=theme.icono(icon, 24),
                     font=ctk.CTkFont(family=theme.FONTE, size=24)
                     ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(topo, text=titulo,
                     font=ctk.CTkFont(family=theme.FONTE, size=14, weight="bold"),
                     text_color=theme.TEXTO, anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkFrame(topo, width=8, height=22, fg_color=grad[0],
                     corner_radius=2, border_width=0).pack(side="right")
        ctk.CTkLabel(c, text=desc,
                     font=ctk.CTkFont(family=theme.FONTE, size=12),
                     text_color=theme.TEXTO_SEC, anchor="w",
                     wraplength=280, justify="left").pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkButton(
            c, text="Executar  →", command=cmd, height=40,
            font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
            corner_radius=10, fg_color=grad[0], hover_color=grad[1], text_color="white",
        ).pack(fill="x", padx=16, pady=(0, 14))

    def _recarregar_metricas(self):
        for w in self.frame_admin.winfo_children():
            w.destroy()
        self._criar_painel_admin()
        messagebox.showinfo("Atualizado", "✅ Dados recarregados com sucesso.")

    def _limpar_tudo(self):
        if messagebox.askyesno("⚠️ PERIGO", "Isso apagará TODOS os registros permanentemente!\n\nDeseja continuar?"):
            db.limpar_todos()
            historico.registrar_evento("limpeza", "Todos os dados foram removidos via painel admin")
            messagebox.showwarning("Limpeza", "🗑️  Todos os dados foram removidos.")
            self._recarregar_metricas()

    def _popup_stats(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Estatísticas do Sistema")
        popup.geometry("520x540")
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        theme.preparar_popup(popup)

        popup.grid_columnconfigure(0, weight=1)
        popup.grid_rowconfigure(1, weight=1)

        ctk.CTkFrame(
            popup, height=4, fg_color=theme.ROXO, corner_radius=2, border_width=0,
        ).grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            popup, text="  Estatísticas do Sistema", image=theme.icono("dashboard", 16), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=20, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 12))

        card = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        card.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        card.grid_columnconfigure(0, weight=1)

        m = metricas.obter_metricas()
        total = m["total"]
        total_proc = m["geral"]
        fazenda = m["fazenda"]
        outros = m["outros"]
        status = m["status"]

        stats = [
            ("Servidores cadastrados", theme.fmt_num(total), theme.GRADIENTE_AZUL[0]),
            ("Total de processos", theme.fmt_num(total_proc), theme.GRADIENTE_ROXO[0]),
            ("Processos Fazenda", theme.fmt_num(fazenda), theme.GRADIENTE_CIANO[0]),
            ("Outros processos", theme.fmt_num(outros), theme.GRADIENTE_LARANJA[0]),
        ]
        for i, (lbl, val, cor) in enumerate(stats):
            linha = theme.card(card)
            linha.grid(row=i, column=0, sticky="ew", pady=4)
            ctk.CTkFrame(linha, height=3, fg_color=cor, corner_radius=2,
                         border_width=0).pack(fill="x")
            ctk.CTkLabel(
                linha, text=lbl,
                font=ctk.CTkFont(family=theme.FONTE, size=13),
                text_color=theme.TEXTO, anchor="w",
            ).pack(side="left", padx=16, pady=12)
            ctk.CTkLabel(
                linha, text=val,
                font=ctk.CTkFont(family=theme.FONTE, size=18, weight="bold"),
                text_color=cor, anchor="e",
            ).pack(side="right", padx=16, pady=12)

        if status:
            ctk.CTkLabel(
                card, text="  Distribuição por Status", image=theme.icono("grafico", 14), compound="left",
                font=ctk.CTkFont(family=theme.FONTE, size=14, weight="bold"),
                text_color=theme.TEXTO, anchor="w",
            ).grid(row=len(stats), column=0, sticky="w", pady=(14, 6))
            for j, (s, q) in enumerate(status.items()):
                linha = ctk.CTkFrame(card, fg_color=theme.FIELD, corner_radius=8)
                linha.grid(row=len(stats) + 1 + j, column=0, sticky="ew", pady=2, padx=4)
                txt, cor_t, cor_bg = theme.status_badge_cores(s)
                theme.badge(linha, txt, cor_t, cor_bg, tamanho=10).pack(side="left", padx=10, pady=6)
                ctk.CTkLabel(
                    linha, text=theme.fmt_num(q),
                    font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
                    text_color=theme.TEXTO,
                ).pack(side="right", padx=14, pady=6)

        theme.exibir_popup(popup)

    # ================================================ ABA ATIVIDADES
    def _criar_aba_atividades(self, aba):
        wrapper = ctk.CTkFrame(aba, fg_color="transparent")
        wrapper.grid(row=0, column=0, sticky="nsew", padx=18, pady=14)
        wrapper.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            wrapper,
            text="  Histórico de eventos administrativos do sistema", image=theme.icono("logs", 14), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=13),
            text_color=theme.TEXTO_SEC, anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        lista_card = theme.card(wrapper)
        lista_card.grid(row=1, column=0, sticky="nsew")
        lista_card.grid_columnconfigure(0, weight=1)
        ctk.CTkFrame(
            lista_card, height=3, fg_color=theme.GRADIENTE_ROXO[0],
            corner_radius=2, border_width=0,
        ).grid(row=0, column=0, sticky="ew")

        eventos = historico.obter_eventos(None, 20)
        if not eventos:
            ctk.CTkLabel(
                lista_card, text="  Nenhuma atividade registrada ainda.", image=theme.icono("logs", 14), compound="left",
                font=ctk.CTkFont(family=theme.FONTE, size=12),
                text_color=theme.TEXTO_SEC,
            ).grid(row=1, column=0, pady=30)
            return

        for i, ev in enumerate(eventos):
            linha = ctk.CTkFrame(lista_card, fg_color="transparent")
            linha.grid(row=i + 1, column=0, sticky="ew", padx=16, pady=4)
            linha.grid_columnconfigure(1, weight=1)

            tipo = ev.get("tipo", "")
            icones = {
                "importacao": ("importacao", theme.AZUL_CLARO),
                "backup": ("backup", theme.CIANO),
                "restauracao": ("importacao", theme.LARANJA),
                "limpeza": ("deletar", theme.VERMELHO),
                "admin_login": ("clave", theme.ROXO),
            }
            icone, cor = icones.get(tipo, ("estrela", theme.TEXTO_SEC))

            box = ctk.CTkFrame(linha, width=32, height=32, corner_radius=8, fg_color=theme.FIELD)
            box.grid(row=0, column=0, padx=(0, 12))
            box.pack_propagate(False)
            ctk.CTkLabel(
                box, text="", image=theme.icono(icone, 14),
                font=ctk.CTkFont(family=theme.FONTE, size=14),
            ).pack(expand=True)

            info = ctk.CTkFrame(linha, fg_color="transparent")
            info.grid(row=0, column=1, sticky="w")
            ctk.CTkLabel(
                info, text=ev.get("titulo", ""),
                font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
                text_color=theme.TEXTO, anchor="w",
            ).pack(anchor="w")
            if ev.get("detalhe"):
                ctk.CTkLabel(
                    info, text=ev.get("detalhe", ""),
                    font=ctk.CTkFont(family=theme.FONTE, size=11),
                    text_color=theme.TEXTO_SEC, anchor="w",
                ).pack(anchor="w")

            ctk.CTkLabel(
                linha, text=historico.tempo_relativo(ev.get("ts")),
                font=ctk.CTkFont(family=theme.FONTE, size=11),
                text_color=cor, anchor="e",
            ).grid(row=0, column=2, sticky="e", padx=(12, 0))

    # =============================================== AÇÕES DO FORMULÁRIO
    def _carregar_edicao(self):
        cpf = self.entry_busca_cpf.get().strip()
        if not cpf:
            self.lbl_admin_status.configure(
                text="⚠️  Digite um CPF para buscar.",
                text_color=theme.LARANJA,
            )
            return
        dados = db.buscar_por_cpf_flexivel(cpf)
        if not dados:
            self.lbl_admin_status.configure(
                text="❌  Registro não encontrado.",
                text_color=theme.VERMELHO,
            )
            return
        self.dados_editando = dados
        for key, entry in self.campos_form.items():
            valor = dados.get(key, "")
            if key == "cpf":
                entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, str(valor) if valor is not None else "")
            if key == "cpf":
                entry.configure(state="disabled")
        self.lbl_admin_status.configure(
            text=f"✅  Registro carregado: {dados.get('nome', '')}",
            text_color=theme.VERDE,
        )

    def _salvar_alteracoes(self):
        if not self.dados_editando:
            self.lbl_admin_status.configure(
                text="⚠️  Carregue um registro primeiro.",
                text_color=theme.LARANJA,
            )
            return
        dados = {key: entry.get() for key, entry in self.campos_form.items() if key != "cpf"}
        for k in ["qtdade_processos_fazenda", "qtdade_processos_outros", "qtdade_total_processos"]:
            try:
                dados[k] = int(dados[k]) if dados[k] else 0
            except ValueError:
                self.lbl_admin_status.configure(
                    text=f"❌  Campo {k} deve ser numérico.",
                    text_color=theme.VERMELHO,
                )
                return
        db.atualizar_pessoa(self.dados_editando["cpf"], dados)
        self.dados_editando = db.buscar_por_cpf(self.dados_editando["cpf"])
        self.lbl_admin_status.configure(
            text="✅  Alterações salvas com sucesso!",
            text_color=theme.VERDE,
        )
        historico.registrar_evento(
            "admin_login",
            f"Registro atualizado: {self.dados_editando.get('nome', '')}",
            f"CPF: {historico.mascarar_cpf(self.dados_editando.get('cpf', ''))}",
        )

    def _deletar_registro(self):
        if not self.dados_editando:
            self.lbl_admin_status.configure(
                text="⚠️  Carregue um registro primeiro.",
                text_color=theme.LARANJA,
            )
            return
        nome = self.dados_editando.get("nome", "")
        cpf = self.dados_editando.get("cpf", "")
        if messagebox.askyesno("Confirmar exclusão",
                               f"❗  Excluir permanentemente:\n\n{nome}\n{historico.mascarar_cpf(cpf)}"):
            db.deletar_pessoa(cpf)
            historico.registrar_evento("limpeza", f"Registro excluído: {nome}")
            self._limpar_form()
            self.lbl_admin_status.configure(
                text="🗑️  Registro excluído com sucesso.",
                text_color=theme.LARANJA,
            )

    def _alterar_senha(self):
        dialog = ctk.CTkInputDialog(
            text="Digite a nova senha de administrador:",
            title="Alterar Senha",
        )
        nova = dialog.get_input()
        if nova:
            db.set_admin_senha(nova)
            historico.registrar_evento("admin_login", "Senha de administrador alterada")
            messagebox.showinfo("Sucesso", "✅ Senha alterada com sucesso.")
