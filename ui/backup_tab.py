import customtkinter as ctk
from tkinter import messagebox, filedialog
from database.db_manager import DatabaseManager
from excel_io.excel_handler import (
    exportar_excel, gerar_backup_json, restaurar_backup_json,
    importar_planilha_conferencia,
)
from ui import theme
from ui import historico

db = DatabaseManager()


class BackupTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # ---------------------- Header com cor de destaque
        header = theme.card(scroll)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.grid_columnconfigure(0, weight=1)

        body = ctk.CTkFrame(header, fg_color="transparent")
        body.pack(fill="x", padx=22, pady=18)
        body.grid_columnconfigure(0, weight=1)

        # Faixa colorida de gradiente
        ctk.CTkFrame(body, height=4, fg_color=theme.ROXO,
                     corner_radius=2).pack(fill="x", pady=(0, 12))

        linha = ctk.CTkFrame(body, fg_color="transparent")
        linha.pack(fill="x")
        linha.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            linha, text="", image=theme.icono("backup", 34),
            font=ctk.CTkFont(family=theme.FONTE, size=34),
        ).grid(row=0, column=0, padx=(0, 14))

        info = ctk.CTkFrame(linha, fg_color="transparent")
        info.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(
            info, text="Backup e Restauração",
            font=ctk.CTkFont(family=theme.FONTE, size=24, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            info, text="  Proteja seus dados com backup periódico e restaure sempre que precisar", image=theme.icono("escudo", 14), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=13),
            text_color=theme.TEXTO_SEC, anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # ---------------------- 4 cards de ação
        frame = ctk.CTkFrame(scroll, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        frame.grid_columnconfigure((0, 1), weight=1, uniform="acao")

        self._criar_acao(
            frame, "exportacao", "Exportar Excel",
            "Salva todos os dados em uma planilha .xlsx editável",
            theme.GRADIENTE_AZUL, self._exportar_excel, 0, 0,
        )
        self._criar_acao(
            frame, "exportacao", "Exportar JSON",
            "Salva todos os dados em arquivo JSON estruturado",
            theme.GRADIENTE_CIANO, self._exportar_json, 0, 1,
        )
        self._criar_acao(
            frame, "importacao", "Restaurar Backup",
            "Importa dados de um backup JSON anterior",
            theme.GRADIENTE_LARANJA, self._restaurar_json, 1, 0,
        )
        self._criar_acao(
            frame, "deletar", "Limpar Dados",
            "Remove permanentemente todos os registros",
            theme.GRADIENTE_ROSA, self._limpar_dados, 1, 1,
        )

        # ---------------------- Planilhas para Conferência
        card_conf = theme.card(scroll)
        card_conf.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        card_conf.grid_columnconfigure(0, weight=1)

        corpo_conf = ctk.CTkFrame(card_conf, fg_color="transparent")
        corpo_conf.pack(fill="x", padx=22, pady=18)
        corpo_conf.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(corpo_conf, height=4, fg_color=theme.LARANJA,
                     corner_radius=2).pack(fill="x", pady=(0, 12))

        topo_conf = ctk.CTkFrame(corpo_conf, fg_color="transparent")
        topo_conf.pack(fill="x")
        ctk.CTkLabel(
            topo_conf, text="", image=theme.icono("alerta", 28),
        ).pack(side="left", padx=(0, 12))

        info_conf = ctk.CTkFrame(topo_conf, fg_color="transparent")
        info_conf.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            info_conf, text="Planilhas para Conferência",
            font=ctk.CTkFont(family=theme.FONTE, size=20, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            info_conf,
            text="Importa planilhas de processos (um processo por linha, agrupados por CPF) ou "
                 "de CPFs sem processo vinculado — o sistema identifica o formato automaticamente "
                 "e vincula os dados à secretaria ou órgão informado",
            font=ctk.CTkFont(family=theme.FONTE, size=12),
            text_color=theme.TEXTO_SEC, anchor="w", justify="left",
            wraplength=560,
        ).pack(anchor="w", pady=(2, 0))

        form_conf = ctk.CTkFrame(corpo_conf, fg_color="transparent")
        form_conf.pack(fill="x", pady=(16, 0))
        form_conf.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            form_conf, text="Secretaria / Órgão *",
            font=ctk.CTkFont(family=theme.FONTE, size=12, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        linha_conf = ctk.CTkFrame(form_conf, fg_color="transparent")
        linha_conf.grid(row=1, column=0, sticky="ew")
        linha_conf.grid_columnconfigure(0, weight=1)

        self.entry_secretaria = ctk.CTkEntry(
            linha_conf, placeholder_text="Ex: SEDUC, SEFAZ, PGE...",
            font=ctk.CTkFont(family=theme.FONTE, size=14), height=42,
            corner_radius=10, fg_color=theme.FIELD, border_color=theme.FIELD_BORDER,
        )
        self.entry_secretaria.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            linha_conf, text="Importar Planilha", command=self._importar_conferencia,
            width=190, height=42,
            image=theme.icono_branco("importacao", 16), compound="left",
            font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
            corner_radius=10, fg_color=theme.LARANJA, hover_color=theme.LARANJA_HOVER,
            text_color="white",
        ).grid(row=0, column=1)

        # ---------------------- Status
        self.lbl_status = ctk.CTkLabel(
            scroll, text="", font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
        )
        self.lbl_status.grid(row=3, column=0, sticky="w", pady=(0, 16))

    def _criar_acao(self, parent, icone, titulo, descricao, gradiente, comando, linha, coluna):
        card = theme.card(parent)
        card.grid(row=linha, column=coluna, sticky="nsew",
                   padx=(0, 12) if coluna == 0 else (12, 0), pady=8)

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=18, pady=(16, 8))

        # Ícone com cor de destaque
        ctk.CTkLabel(
            topo, text="", image=theme.icono(icone, 24),
            font=ctk.CTkFont(family=theme.FONTE, size=24),
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            topo, text=titulo,
            font=ctk.CTkFont(family=theme.FONTE, size=15, weight="bold"),
            text_color=theme.TEXTO, anchor="w",
        ).pack(side="left", padx=(0, 12))

        # Tag de cor
        ctk.CTkFrame(
            topo, width=8, height=24, fg_color=gradiente[0],
            corner_radius=2, border_width=0,
        ).pack(side="right")

        ctk.CTkLabel(
            card, text=descricao,
            font=ctk.CTkFont(family=theme.FONTE, size=12),
            text_color=theme.TEXTO_SEC, anchor="w",
            wraplength=300, justify="left",
        ).pack(fill="x", padx=18, pady=(0, 14))

        ctk.CTkButton(
            card, text="Executar  →", command=comando,
            height=42, font=ctk.CTkFont(family=theme.FONTE, size=13, weight="bold"),
            corner_radius=10, fg_color=gradiente[0], hover_color=gradiente[1],
            text_color="white",
        ).pack(fill="x", padx=18, pady=(0, 18))

    def _exportar_excel(self):
        caminho = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                               filetypes=[("Excel", "*.xlsx")],
                                               title="Salvar backup Excel")
        if not caminho:
            return
        sucesso, msg = exportar_excel(caminho)
        if sucesso:
            historico.registrar_evento("backup", "Backup Excel exportado",
                                       caminho.replace("\\", "/").rsplit("/", 1)[-1])
        self.lbl_status.configure(
            text=("✅  " if sucesso else "❌  ") + msg,
            text_color=theme.VERDE if sucesso else theme.VERMELHO,
        )

    def _exportar_json(self):
        caminho = filedialog.asksaveasfilename(defaultextension=".json",
                                               filetypes=[("JSON", "*.json")],
                                               title="Salvar backup JSON")
        if not caminho:
            return
        sucesso, msg = gerar_backup_json(caminho)
        if sucesso:
            historico.registrar_evento("backup", "Backup JSON criado",
                                       caminho.replace("\\", "/").rsplit("/", 1)[-1])
        self.lbl_status.configure(
            text=("✅  " if sucesso else "❌  ") + msg,
            text_color=theme.VERDE if sucesso else theme.VERMELHO,
        )

    def _restaurar_json(self):
        caminho = filedialog.askopenfilename(filetypes=[("JSON", "*.json")],
                                             title="Selecionar backup JSON")
        if not caminho:
            return
        if messagebox.askyesno("Confirmar", "Isso substituirá TODOS os dados atuais. Deseja continuar?"):
            sucesso, msg = restaurar_backup_json(caminho)
            if sucesso:
                historico.registrar_evento("restauracao", "Backup restaurado",
                                           caminho.replace("\\", "/").rsplit("/", 1)[-1])
            self.lbl_status.configure(
                text=("✅  " if sucesso else "❌  ") + msg,
                text_color=theme.VERDE if sucesso else theme.VERMELHO,
            )

    def _importar_conferencia(self):
        secretaria = self.entry_secretaria.get().strip()
        if not secretaria:
            messagebox.showwarning(
                "Secretaria obrigatória",
                "Informe o nome da secretaria ou órgão antes de importar a planilha.",
            )
            self.entry_secretaria.focus_set()
            return

        caminho = filedialog.askopenfilename(
            filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")],
            title="Selecionar planilha de conferência",
        )
        if not caminho:
            return
        if not messagebox.askyesno(
            "Confirmar",
            f"Isso vinculará os processos da planilha à secretaria \"{secretaria}\". Continuar?",
        ):
            return

        janela = self.winfo_toplevel()
        progress = ctk.CTkToplevel(janela)
        progress.title("Importando...")
        progress.geometry("500x130")
        progress.transient(janela)
        progress.grab_set()
        progress.resizable(False, False)
        theme.preparar_popup(progress)

        ctk.CTkLabel(progress, text="Importando processos, aguarde...",
                     font=ctk.CTkFont(family=theme.FONTE, size=14, weight="bold")).pack(pady=(25, 10))
        progress_bar = ctk.CTkProgressBar(progress, width=400)
        progress_bar.pack(pady=10)
        progress_bar.set(0)
        lbl_progress = ctk.CTkLabel(progress, text="0/0",
                                    font=ctk.CTkFont(family=theme.FONTE, size=12))
        lbl_progress.pack(pady=(0, 15))
        theme.exibir_popup(progress)
        janela.update()

        def callback(inseridos, total, mensagem=None):
            if total > 0:
                progress_bar.set(inseridos / total)
            lbl_progress.configure(text=mensagem or f"{inseridos}/{total}")
            progress.update()

        sucesso, msg = importar_planilha_conferencia(caminho, secretaria, callback_progresso=callback)
        progress_bar.set(1)
        lbl_progress.configure(text="Concluído!")
        progress.after(500, progress.destroy)

        if sucesso:
            nome_arquivo = caminho.replace("\\", "/").rsplit("/", 1)[-1]
            historico.registrar_evento("conferencia", f"Conferência importada — {secretaria}", nome_arquivo)
            if hasattr(janela, "dashboard_tab"):
                janela.dashboard_tab.recarregar()

        self.lbl_status.configure(
            text=("✅  " if sucesso else "❌  ") + msg,
            text_color=theme.VERDE if sucesso else theme.VERMELHO,
        )

    def _limpar_dados(self):
        if messagebox.askyesno("Perigo!", "Isso apagará TODOS os registros permanentemente. Continuar?"):
            db.limpar_todos()
            historico.registrar_evento("limpeza", "Todos os dados foram removidos")
            self.lbl_status.configure(
                text="⚠️  Todos os dados foram removidos.",
                text_color=theme.LARANJA,
            )
