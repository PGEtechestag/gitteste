import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
from database.db_manager import DatabaseManager
from ui import theme

db = DatabaseManager()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class MainWindow(ctk.CTk):
    """Janela principal com inicialização otimizada e cache de abas."""

    NOMES = {
        "dashboard": "Dashboard",
        "consulta": "Consulta",
        "admin": "Administrativo",
        "backup": "Backup",
    }
    ICONES_ABAS = {
        "dashboard": "dashboard",
        "consulta": "consulta",
        "admin": "admin",
        "backup": "backup",
    }
    ABA_INICIAL = "dashboard"

    def __init__(self):
        super().__init__()

        img_sp = Image.open("assets/sp_brasao.png")
        ctk_img_sp = ctk.CTkImage(img_sp, size=(44, 51))
        icon_img = ImageTk.PhotoImage(Image.open("assets/sp_icon.png"))
        self.iconphoto(True, icon_img)
        self._img_sp = ctk_img_sp
        self._icon_img = icon_img

        self.title("Acompanhamento Coletivas — Consulta e Gerenciamento")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.after(10, lambda: self.state("zoomed"))
        self.configure(fg_color=theme.BG)

        self.acao_atual = None
        self._mostrar_tela_acoes()

    # ============================================================ TELA DE AÇÕES COLETIVAS
    def _limpar_janela(self):
        for w in self.winfo_children():
            w.destroy()

    def _mostrar_tela_acoes(self):
        self._limpar_janela()

        frame_topo = ctk.CTkFrame(
            self, height=78, fg_color=theme.CARD,
            corner_radius=0, border_width=0,
        )
        frame_topo.pack(side="top", fill="x")
        frame_topo.pack_propagate(False)

        ctk.CTkFrame(
            self, height=3, fg_color=theme.ORO,
            corner_radius=0, border_width=0,
        ).pack(side="top", fill="x")

        frame_logo = ctk.CTkFrame(frame_topo, fg_color="transparent")
        frame_logo.pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(frame_logo, image=self._img_sp, text="").pack(side="left", padx=(0, 10))

        logo_row = ctk.CTkFrame(frame_logo, fg_color="transparent")
        logo_row.pack(side="top", anchor="w")
        ctk.CTkLabel(logo_row, text="Acompanhamento",
                     font=ctk.CTkFont(family=theme.FONTE, size=20, weight="bold"),
                     text_color=theme.TEXTO).pack(side="left")
        ctk.CTkLabel(logo_row, text=" Coletivas",
                     font=ctk.CTkFont(family=theme.FONTE, size=20, weight="bold"),
                     text_color=theme.ORO,
                     ).pack(side="left")
        ctk.CTkLabel(frame_logo, text="Procuradoria Geral do Estado de São Paulo",
                     font=ctk.CTkFont(family=theme.FONTE, size=12),
                     text_color=theme.TEXTO_SEC).pack(side="top", anchor="w")

        corpo = ctk.CTkScrollableFrame(self, fg_color="transparent")
        corpo.pack(fill="both", expand=True, padx=40, pady=30)
        corpo.grid_columnconfigure(0, weight=1)
        corpo._scrollbar.grid_remove()

        ctk.CTkLabel(
            corpo, text="Ações Coletivas",
            font=ctk.CTkFont(family=theme.FONTE, size=26, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))
        ctk.CTkLabel(
            corpo, text="Selecione uma ação para acompanhar o cumprimento",
            font=ctk.CTkFont(family=theme.FONTE, size=14),
            text_color=theme.TEXTO_SEC, anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(0, 20))

        acoes = db.listar_acoes_coletivas()
        linha = 2
        for acao in acoes:
            self._criar_card_acao(corpo, acao, linha)
            linha += 1

        self._criar_card_nova_acao(corpo, linha)

    def _criar_card_acao(self, parent, acao, linha):
        card = theme.card(parent)
        card.grid(row=linha, column=0, sticky="ew", pady=8)
        card.grid_columnconfigure(1, weight=1)

        quadro = ctk.CTkFrame(
            card, width=48, height=48, corner_radius=12,
            fg_color=theme.GRADIENTE_AZUL[0],
        )
        quadro.grid(row=0, column=0, padx=(18, 14), pady=18)
        quadro.grid_propagate(False)
        ctk.CTkLabel(
            quadro, text="", image=theme.icono("escudo", 22),
            text_color="white",
        ).pack(expand=True)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=0, column=1, sticky="w", pady=18)
        ctk.CTkLabel(
            info, text=acao["titulo"],
            font=ctk.CTkFont(family=theme.FONTE, size=16, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            info, text=f"Processo nº {acao['numero_processo']}",
            font=ctk.CTkFont(family=theme.FONTE, size=13),
            text_color=theme.TEXTO_SEC, anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(
            card, text="", image=theme.icono("avancar", 18),
        ).grid(row=0, column=2, padx=18)

        self._tornar_clicavel(card, lambda: self._abrir_acao(acao))

    def _criar_card_nova_acao(self, parent, linha):
        card = theme.card(parent)
        card.configure(border_color=theme.ACCENT)
        card.grid(row=linha, column=0, sticky="ew", pady=8)
        card.grid_columnconfigure(0, weight=1)

        conteudo = ctk.CTkFrame(card, fg_color="transparent")
        conteudo.grid(row=0, column=0, pady=22)
        ctk.CTkLabel(
            conteudo, text="", image=theme.icono("plus", 20),
        ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            conteudo, text="Cadastrar Nova Ação",
            font=ctk.CTkFont(family=theme.FONTE, size=15, weight="bold"),
            text_color=theme.ACCENT,
        ).pack(side="left")

        self._tornar_clicavel(card, self._cadastrar_nova_acao)

    def _tornar_clicavel(self, widget, comando):
        """Torna um widget (e seus filhos) clicável, com cursor de mão."""
        widget.configure(cursor="hand2")
        widget.bind("<Button-1>", lambda e: comando())
        for filho in widget.winfo_children():
            self._tornar_clicavel(filho, comando)

    def _cadastrar_nova_acao(self):
        messagebox.showinfo(
            "Em breve",
            "O cadastro de novas ações coletivas será implementado em uma próxima etapa.",
        )

    def _abrir_acao(self, acao):
        self.acao_atual = acao
        self._limpar_janela()
        self._criar_topo()
        self._criar_abas()

    # ============================================================ HEADER
    def _criar_topo(self):
        frame_topo = ctk.CTkFrame(
            self, height=78, fg_color=theme.CARD,
            corner_radius=0, border_width=0,
        )
        frame_topo.pack(side="top", fill="x")
        frame_topo.pack_propagate(False)

        ctk.CTkFrame(
            self, height=3, fg_color=theme.ORO,
            corner_radius=0, border_width=0,
        ).pack(side="top", fill="x")

        frame_logo = ctk.CTkFrame(frame_topo, fg_color="transparent")
        frame_logo.pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(frame_logo, image=self._img_sp, text="").pack(side="left", padx=(0, 10))

        logo_row = ctk.CTkFrame(frame_logo, fg_color="transparent")
        logo_row.pack(side="top", anchor="w")
        ctk.CTkLabel(logo_row, text="Acompanhamento",
                     font=ctk.CTkFont(family=theme.FONTE, size=20, weight="bold"),
                     text_color=theme.TEXTO).pack(side="left")
        ctk.CTkLabel(logo_row, text=" Coletivas",
                     font=ctk.CTkFont(family=theme.FONTE, size=20, weight="bold"),
                     text_color=theme.ORO,
                     ).pack(side="left")
        ctk.CTkLabel(frame_logo, text="Procuradoria Geral do Estado de São Paulo",
                     font=ctk.CTkFont(family=theme.FONTE, size=12),
                     text_color=theme.TEXTO_SEC).pack(side="top", anchor="w")

        frame_info = ctk.CTkFrame(frame_topo, fg_color="transparent")
        frame_info.pack(side="right", padx=24, pady=10)

        frame_acoes = ctk.CTkFrame(frame_info, fg_color="transparent")
        frame_acoes.pack(side="right")

        btn_inicial = ctk.CTkButton(
            frame_acoes, text="Tela Inicial",
            command=self._mostrar_tela_acoes,
            width=128, height=34,
            image=theme.icono_branco("voltar", 15), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
            corner_radius=10, border_width=0,
            fg_color=theme.AZUL_CLARO, hover_color=theme.AZUL_MEDIO,
            text_color="white",
        )
        btn_inicial.pack(side="left")
        theme.tooltip(btn_inicial, "Volta para a tela de seleção de ações coletivas")

    # ============================================================ ABAS
    def _criar_abas(self):
        self.tab_view = ctk.CTkTabview(
            self, width=800, height=600, corner_radius=14,
            fg_color="transparent", anchor="e",
            segmented_button_fg_color=theme.CARD,
            segmented_button_selected_color=theme.AZUL_CLARO,
            segmented_button_selected_hover_color=theme.AZUL_MEDIO,
            segmented_button_unselected_color=theme.CARD,
            text_color=theme.TEXTO,
            text_color_disabled=theme.TEXTO_SEC,
            border_width=0,
        )
        self.tab_view.pack(fill="both", expand=True, padx=16, pady=(12, 0))

        # Título da ação: sobreposto (place) no canto esquerdo da barra de abas,
        # sem afetar o tamanho/altura interna do CTkTabview.
        if self.acao_atual:
            info_acao = ctk.CTkFrame(self.tab_view, fg_color="transparent")
            info_acao.place(x=14, y=2)
            ctk.CTkLabel(
                info_acao, text=self.acao_atual["titulo"],
                font=ctk.CTkFont(family=theme.FONTE, size=15, weight="bold"),
                text_color=theme.TEXTO, anchor="w",
            ).pack(anchor="w")
            ctk.CTkLabel(
                info_acao, text=f"Processo nº {self.acao_atual['numero_processo']}",
                font=ctk.CTkFont(family=theme.FONTE, size=11),
                text_color=theme.TEXTO_SEC, anchor="w",
            ).pack(anchor="w")

        # Cria as 4 abas (sem conteúdo)
        self.tab_dashboard = self.tab_view.add("Dashboard")
        self.tab_consulta = self.tab_view.add("Consulta")
        self.tab_admin = self.tab_view.add("Administrativo")
        self.tab_backup = self.tab_view.add("Backup")

        # Adiciona os ícones profissionais aos botões das abas
        for chave, nome in self.NOMES.items():
            try:
                boto = self.tab_view._segmented_button._buttons_dict.get(nome)
                if boto is not None:
                    boto.configure(
                        image=theme.icono(self.ICONES_ABAS[chave], 15),
                        compound="left",
                        text=nome,
                    )
            except Exception:
                pass

        # Carrega apenas a aba inicial imediatamente; as outras em background
        self._abas_widgets = {}
        self._inicializar_abas_em_background()

    def _inicializar_abas_em_background(self):
        """Inicializa abas de forma progressiva para não travar a UI."""
        # 1) Carrega a aba Dashboard (inicial) imediatamente
        from ui.dashboard_tab import DashboardTab
        self.dashboard_tab = DashboardTab(self.tab_dashboard)
        self.dashboard_tab.pack(fill="both", expand=True, padx=8, pady=8)
        self._abas_widgets["dashboard"] = self.dashboard_tab
        self.tab_view.set("Dashboard")
        self.update_idletasks()

        # 2) Carrega a Consulta em background (50ms depois)
        self.after(10, self._carregar_consulta_bg)

    def _carregar_consulta_bg(self):
        from ui.consulta_tab import ConsultaTab
        self.consulta_tab = ConsultaTab(self.tab_consulta)
        self.consulta_tab.pack(fill="both", expand=True, padx=8, pady=8)
        self._abas_widgets["consulta"] = self.consulta_tab
        # Próxima: Administrativo
        self.after(10, self._carregar_admin_bg)

    def _carregar_admin_bg(self):
        from ui.admin_tab import AdminTab
        self.admin_tab = AdminTab(self.tab_admin)
        self.admin_tab.pack(fill="both", expand=True, padx=8, pady=8)
        self._abas_widgets["admin"] = self.admin_tab
        # Próxima: Backup
        self.after(10, self._carregar_backup_bg)

    def _carregar_backup_bg(self):
        from ui.backup_tab import BackupTab
        self.backup_tab = BackupTab(self.tab_backup)
        self.backup_tab.pack(fill="both", expand=True, padx=8, pady=8)
        self._abas_widgets["backup"] = self.backup_tab

    def _obter_classe_aba(self, chave):
        """Importa o módulo da aba sob demanda e retorna a classe."""
        if chave not in self._modulos:
            if chave == "dashboard":
                from ui.dashboard_tab import DashboardTab
                self._modulos[chave] = DashboardTab
            elif chave == "consulta":
                from ui.consulta_tab import ConsultaTab
                self._modulos[chave] = ConsultaTab
            elif chave == "admin":
                from ui.admin_tab import AdminTab
                self._modulos[chave] = AdminTab
            elif chave == "backup":
                from ui.backup_tab import BackupTab
                self._modulos[chave] = BackupTab
        return self._modulos[chave]

