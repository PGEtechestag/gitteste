import re
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from database.db_manager import DatabaseManager
from database import cache as metricas
from excel_io.excel_handler import importar_excel
from ui import theme
from ui import historico

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
    ABA_INICIAL = "consulta"

    def __init__(self):
        super().__init__()

        img_sp = Image.open("assets/sp_brasao.png")
        ctk_img_sp = ctk.CTkImage(img_sp, size=(44, 51))
        icon_img = ImageTk.PhotoImage(Image.open("assets/sp_icon.png"))
        self.iconphoto(True, icon_img)
        self._img_sp = ctk_img_sp
        self._icon_img = icon_img

        self.title("Paritários SPPrev — Consulta e Gerenciamento")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.configure(fg_color=theme.BG)

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
        ctk.CTkLabel(logo_row, text="Paritários",
                     font=ctk.CTkFont(family=theme.FONTE, size=20, weight="bold"),
                     text_color=theme.TEXTO).pack(side="left")
        ctk.CTkLabel(logo_row, text=" SPPrev",
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

        btn_importar = ctk.CTkButton(
            frame_acoes, text="Importar Planilha",
            command=self._importar_planilha,
            width=190, height=40,
            image=theme.icono_branco("importacao", 18), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
            corner_radius=12, border_width=0,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="white",
        )
        btn_importar.pack(side="left", padx=(0, 12))
        theme.tooltip(btn_importar, "Seleciona um arquivo Excel para importar dados para o sistema")

        self.btn_tema = ctk.CTkButton(
            frame_acoes, text="", width=44, height=44,
            image=theme.icono("moon", 18),
            font=ctk.CTkFont(family=theme.FONTE, size=15),
            corner_radius=12, fg_color=theme.FIELD,
            hover_color=(theme.CARD_BORDER[0], theme.CARD_HOVER[1]),
            text_color=theme.TEXTO, command=self._alternar_tema,
            border_width=1, border_color=theme.CARD_BORDER,
        )
        self.btn_tema.pack(side="left")
        theme.tooltip(self.btn_tema, "Alterna entre modo claro e escuro")

        pill_total = ctk.CTkFrame(
            frame_info, fg_color=theme.FIELD, corner_radius=18,
            border_width=1, border_color=theme.CARD_BORDER, height=40,
        )
        pill_total.pack(side="right", padx=(0, 16))
        ctk.CTkLabel(
            pill_total, image=theme.icono("usuarios", 16), text="",
        ).pack(side="left", padx=(12, 6), pady=8)
        self.lbl_total = ctk.CTkLabel(
            pill_total, text=f"{theme.fmt_num(metricas.total())} registros",
            font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
            text_color=theme.TEXTO,
        )
        self.lbl_total.pack(side="left", padx=(0, 14), pady=8)

    # ============================================================ ABAS
    def _criar_abas(self):
        self.tab_view = ctk.CTkTabview(
            self, width=800, height=600, corner_radius=14,
            fg_color="transparent",
            segmented_button_fg_color=theme.CARD,
            segmented_button_selected_color=theme.ACCENT,
            segmented_button_selected_hover_color=theme.ACCENT_HOVER,
            segmented_button_unselected_color=theme.CARD,
            text_color=theme.TEXTO,
            text_color_disabled=theme.TEXTO_SEC,
            border_width=0,
        )
        self.tab_view.pack(fill="both", expand=True, padx=16, pady=(12, 0))

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
        # 1) Carrega a aba Consulta (inicial) imediatamente
        from ui.consulta_tab import ConsultaTab
        self.consulta_tab = ConsultaTab(self.tab_consulta)
        self.consulta_tab.pack(fill="both", expand=True, padx=8, pady=8)
        self._abas_widgets["consulta"] = self.consulta_tab
        self.tab_view.set("Consulta")
        self.update_idletasks()

        # 2) Carrega o Dashboard em background (50ms depois)
        self.after(10, self._carregar_dashboard_bg)

    def _carregar_dashboard_bg(self):
        from ui.dashboard_tab import DashboardTab
        self.dashboard_tab = DashboardTab(self.tab_dashboard)
        self.dashboard_tab.pack(fill="both", expand=True, padx=8, pady=8)
        self._abas_widgets["dashboard"] = self.dashboard_tab
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

    # ============================================================ TEMA
    def _alternar_tema(self):
        if ctk.get_appearance_mode().lower() == "dark":
            ctk.set_appearance_mode("light")
            self.btn_tema.configure(image=theme.icono("moon", 18))
        else:
            ctk.set_appearance_mode("dark")
            self.btn_tema.configure(image=theme.icono("sun", 18))

    # ============================================================ IMPORTAR
    def _importar_planilha(self):
        caminho = filedialog.askopenfilename(
            filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")],
            title="Selecionar planilha",
        )
        if not caminho:
            return
        if messagebox.askyesno("Confirmar", "Isso adicionará/atualizará os dados da planilha no banco. Continuar?"):
            progress = ctk.CTkToplevel(self)
            progress.title("Importando...")
            progress.geometry("500x130")
            progress.transient(self)
            progress.grab_set()
            progress.resizable(False, False)
            theme.preparar_popup(progress)

            ctk.CTkLabel(progress, text="Importando dados, aguarde...",
                         font=ctk.CTkFont(family=theme.FONTE, size=14, weight="bold")).pack(pady=(25, 10))
            self.progress_bar = ctk.CTkProgressBar(progress, width=400)
            self.progress_bar.pack(pady=10)
            self.progress_bar.set(0)
            self.lbl_progress = ctk.CTkLabel(progress, text="0/0",
                                             font=ctk.CTkFont(family=theme.FONTE, size=12))
            self.lbl_progress.pack(pady=(0, 15))
            theme.exibir_popup(progress)
            self.update()

            def callback(inseridos, total):
                if total > 0:
                    self.progress_bar.set(inseridos / total)
                    self.lbl_progress.configure(text=f"{inseridos}/{total}")
                progress.update()

            sucesso, msg = importar_excel(caminho, callback_progresso=callback)
            self.progress_bar.set(1)
            self.lbl_progress.configure(text="Concluído!")
            progress.after(500, progress.destroy)

            if sucesso:
                nome_arquivo = caminho.replace("\\", "/").rsplit("/", 1)[-1]
                m = re.search(r"(\d+)/(\d+) registros", msg)
                detalhe = f"{m.group(1)} registros" if m else ""
                historico.registrar_evento("importacao", nome_arquivo, detalhe)

            # Atualiza a pílula de total
            self.lbl_total.configure(text=f"{theme.fmt_num(metricas.total())} registros")
            # Atualiza as abas
            self.consulta_tab.atualizar_metricas()
            self.dashboard_tab.recarregar()
            messagebox.showinfo("Importação", msg)
