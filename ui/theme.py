"""Paleta de cores e helpers visuais compartilhados por todas as telas.

Todas as cores de interface usam tuplas (claro, escuro), padrão CustomTkinter.
Paleta moderna, profissional e com mais identidade visual.
"""

import os
import sys
import weakref

import customtkinter as ctk
from PIL import Image

# ---------------------------------------------------------------- Paleta base
# Identidade visual: Procuradoria Geral do Estado de São Paulo
# Vermelho Sampa (carmesí institucional) + Ouro Paulista + neutros cálidos,
# con alto contraste para lectura cómoda en modo claro e escuro.
BG = ("#F4F2EC", "#16233D")            # fundo xeral (marfil papel / azul marinho)
CARD = ("#FFFFFF", "#1E2F4E")          # fondo dos cards
CARD_HOVER = ("#FAF8F2", "#263A5C")    # hover dos cards
CARD_BORDER = ("#E4DFD3", "#34496A")   # bordo dos cards
FIELD = ("#EFEBE2", "#1A2A46")         # fondo de campos/entradas
FIELD_BORDER = ("#D8D2C3", "#34496A")
ROW_ALT = ("#F8F5EF", "#223454")       # liñas alternadas en tablas

# Accent institucional (Vermello Sampa da bandeira do Estado)
ACCENT = ("#8F1A2A", "#C83846")        # carmesí PGE
ACCENT_HOVER = ("#7A1220", "#E5484D")
ACCENT_DARK = "#6E1120"
ACCENT_LIGHT = "#E7A7B1"

# Ouro Paulista — acento secundario de prestixio
ORO = ("#A97E1B", "#E8BC4A")           # ouro principal
ORO_HOVER = ("#8F6A14", "#F2C14E")
ORO_CLARO = ("#C9A13B", "#F2CB66")
ORO_FONDO = ("#F5E7C0", "#3E3218")     # fondo para badges dourados

# Texto
TEXTO = ("#232831", "#F2EFE9")         # texto principal
TEXTO_SEC = ("#6B7280", "#93A4C2")     # texto secundario (tom azulado)
TEXTO_MUTED = ("#9AA0A6", "#7488A8")

# ===== Paleta expandida de status / categorias =====
# Cores sólidas (mesmo valor nos dous temas)
VERDE = "#10B981"
VERDE_HOVER = "#059669"
VERDE_CLARO = "#34D399"
VERDE_ESCURO = "#065F46"
VERDE_FONDO = "#D1FAE5"

VERMELHO = "#EF4444"
VERMELHO_HOVER = "#DC2626"
VERMELHO_CLARO = "#FCA5A5"
VERMELHO_FONDO = "#FEE2E2"

LARANJA = "#F59E0B"
LARANJA_HOVER = "#D97706"
LARANJA_CLARO = "#FCD34D"
LARANJA_FONDO = "#FEF3C7"

AMARELO = "#FBBF24"
AMARELO_FONDO = "#FEF9C3"

ROXO = "#8B5CF6"
ROXO_HOVER = "#7C3AED"
ROXO_CLARO = "#C4B5FD"
ROXO_FONDO = "#EDE9FE"
ROXO_ESCURO = "#3B2A63"

CIANO = "#06B6D4"
CIANO_HOVER = "#0891B2"
CIANO_CLARO = "#67E8F9"
CIANO_FONDO = "#CFFAFE"

ROSA = "#EC4899"
ROSA_CLARO = "#F9A8D4"
ROSA_FONDO = "#FCE7F3"

# Azul servizo — uso semántico: información, inactivos, enlaces
AZUL_CLARO = "#3A6BCC"
AZUL_MEDIO = "#2D52A8"
AZUL_ESCURO = "#1B3A74"

CINZA_GRAFICO = "#6B7280"
CINZA_CLARO = "#D8D2C3"

# Gradientes pre-definidos (para cards de destaque)
GRADIENTE_AZUL = ("#3A6BCC", "#1B3A74")
GRADIENTE_VERMELHO = ("#C83846", "#6E1120")
GRADIENTE_ORO = ("#E8BC4A", "#8F6A14")
GRADIENTE_GRANATE = ("#9E1F2F", "#5C0E1C")
GRADIENTE_VERDE = ("#1FBF87", "#04875D")
GRADIENTE_LARANJA = ("#F5A623", "#B26000")
GRADIENTE_CIANO = ("#0FB7D0", "#0A6E84")
GRADIENTE_ROXO = ("#8B5CF6", "#5B2D8C")
GRADIENTE_ROSA = ("#EC6390", "#AD1E44")

# Cores sólidas para fondos de gráficos (Canvas non acepta tuplas)
CHART_BG = {"Light": "#FFFFFF", "Dark": "#1E2F4E"}
CHART_GRID = {"Light": "#E4DFD3", "Dark": "#34496A"}
CHART_TEXT = {"Light": "#6B7280", "Dark": "#8DA0C4"}

FONTE = "Segoe UI"



# ============================================================== FONTES
# O CustomTkinter registra uma fonte Tk nomeada para cada instância de CTkFont.
# Como o app cria dezenas de instâncias idênticas sempre que reconstrói uma tela
# (dashboard, resultados de busca, popups…), reutilizar a mesma instância para os
# mesmos parâmetros reduz bastante o custo de criação/registro de fontes.
# WeakValueDictionary evita segurar widgets vivos na memória (retorna None quando
# a fonte deixa de ser usada, recriando-a na próxima chamada).
_CTKFONT_ORIGINAL = ctk.CTkFont
_CTKFONT_CACHE = weakref.WeakValueDictionary()


def _ctkfont_cacheado(*args, **kwargs):
    """Cria/retorna um CTkFont reaproveitando instâncias equivalentes."""
    try:
        chave = (args, frozenset(kwargs.items()))
    except TypeError:
        return _CTKFONT_ORIGINAL(*args, **kwargs)
    try:
        fonte = _CTKFONT_CACHE.get(chave)
    except TypeError:
        fonte = None
    if fonte is None:
        fonte = _CTKFONT_ORIGINAL(*args, **kwargs)
        try:
            _CTKFONT_CACHE[chave] = fonte
        except TypeError:
            pass
    return fonte


# Todos os ctk.CTkFont(...) do app passam a reutilizar fontes equivalentes.
ctk.CTkFont = _ctkfont_cacheado


# ============================================================== ICONES
# Ícones vetoriais (Lucide, licencia ISC) convertidos a PNG nas cores:
#   assets/icons/light/*.png  — cor escura, para os temas claros
#   assets/icons/dark/*.png   — cor clara, para os temas escuros
#   assets/icons/white/*.png  — branco puro, para fondos de gradiente
# O CTkImage alterna automaticamente entre light_image e dark_image ao
# mudar o tema, e as instancias ficam em cache para non recrealas.
_ICONO_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "icons",
)
_ICONO_CACHE = {}


def icono(nome, tamanho=18):
    """Retorna un CTkImage cun icono PNG (cambia de cor co tema)."""
    chave = ("auto", nome, tamanho)
    img = _ICONO_CACHE.get(chave)
    if img is None:
        try:
            light = Image.open(os.path.join(_ICONO_DIR, "light", nome + ".png")).convert("RGBA")
            dark = Image.open(os.path.join(_ICONO_DIR, "dark", nome + ".png")).convert("RGBA")
            if light.size[0] != tamanho:
                light = light.resize((tamanho, tamanho), Image.Resampling.LANCZOS)
                dark = dark.resize((tamanho, tamanho), Image.Resampling.LANCZOS)
            img = ctk.CTkImage(light_image=light, dark_image=dark, size=(tamanho, tamanho))
        except OSError:
            return None
        _ICONO_CACHE[chave] = img
    return img


def icono_branco(nome, tamanho=18):
    """Retorna un CTkImage en branco (para usar sobre gradientes de cor)."""
    chave = ("white", nome, tamanho)
    img = _ICONO_CACHE.get(chave)
    if img is None:
        try:
            white = Image.open(os.path.join(_ICONO_DIR, "white", nome + ".png")).convert("RGBA")
            if white.size[0] != tamanho:
                white = white.resize((tamanho, tamanho), Image.Resampling.LANCZOS)
            img = ctk.CTkImage(light_image=white, dark_image=white, size=(tamanho, tamanho))
        except OSError:
            return None
        _ICONO_CACHE[chave] = img
    return img


# ============================================================== POPUPS
def preparar_popup(popup):
    """Prepara um CTkToplevel para abrir sem a animação nativa do Windows.

    Chamar logo após criar o popup (antes de montar o conteúdo): a janela é
    mantida invisível durante a construção e só aparece ao chamar exibir_popup().
    """
    try:
        if sys.platform == "win32":
            popup.attributes("-alpha", 0.0)
    except Exception:
        pass
    return popup


def exibir_popup(popup):
    """Exibe um popup preparado com preparar_popup() de forma instantânea."""
    try:
        popup.update()  # garante janela mapeada (ainda invisível) antes de revelar
        if sys.platform == "win32":
            popup.attributes("-alpha", 1.0)
    except Exception:
        try:
            popup.deiconify()
        except Exception:
            pass
    try:
        popup.lift()
        popup.focus_force()
    except Exception:
        pass
    return popup


def fmt_num(n):
    """Formata inteiros com separador de milhar no padrão pt-BR (40.425)."""
    try:
        return f"{int(n):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(n)


def fmt_pct(valor, total, casas=1):
    """Percentual de valor/total como string pt-BR (57,1%)."""
    if not total:
        return "0%"
    return f"{(valor / total * 100):.{casas}f}".replace(".", ",") + "%"


def cor_tema(chave):
    """Retorna cor sólida para Canvas conforme o modo de aparência atual."""
    modo = "Dark" if ctk.get_appearance_mode().lower() == "dark" else "Light"
    return chave[modo]


def badge(parent, texto, cor_texto, cor_fundo, tamanho=11):
    """Cria um badge (etiqueta pill colorida) e retorna o CTkLabel."""
    return ctk.CTkLabel(
        parent, text=texto,
        font=ctk.CTkFont(family=FONTE, size=tamanho, weight="bold"),
        text_color=cor_texto, fg_color=cor_fundo,
        corner_radius=10, padx=10, pady=2, height=22,
    )


def badge_gradiente(parent, texto, cor1, cor2, tamanho=11):
    """Badge com gradiente visual (cor sólida usada)."""
    return ctk.CTkLabel(
        parent, text=texto,
        font=ctk.CTkFont(family=FONTE, size=tamanho, weight="bold"),
        text_color="white", fg_color=cor1,
        corner_radius=10, padx=10, pady=2, height=22,
    )


def card(parent, **kwargs):
    """Cria um card padrão (fundo, borda e cantos arredondados)."""
    kwargs.setdefault("fg_color", CARD)
    kwargs.setdefault("corner_radius", 14)
    kwargs.setdefault("border_width", 1)
    kwargs.setdefault("border_color", CARD_BORDER)
    return ctk.CTkFrame(parent, **kwargs)


def icone_box(parent, emoji, cor_fundo, cor_emoji="white", tamanho=36):
    """Caixa quadrada com emoji/ícone colorido de fundo."""
    frame = ctk.CTkFrame(parent, width=tamanho, height=tamanho,
                         corner_radius=10, fg_color=cor_fundo)
    frame.pack_propagate(False)
    ctk.CTkLabel(
        frame, text=emoji, text_color=cor_emoji,
        font=ctk.CTkFont(family=FONTE, size=int(tamanho * 0.45), weight="bold"),
    ).pack(expand=True)
    return frame


class ToolTip:
    """Tooltip (dica flutuante) para qualquer widget Tk/CTk.

    Aparece após um pequeno delay quando o mouse entra no widget.
    """

    def __init__(self, widget, texto, cor_fundo=None, cor_texto="white",
                 delay=250, wraplength=320):
        self.widget = widget
        self.texto = texto
        self.delay = delay
        self.wraplength = wraplength
        self.cor_fundo = cor_fundo or ("#2A3240", "#152438")
        self.cor_texto = cor_texto
        self._tip = None
        self._after_id = None
        widget.bind("<Enter>", self._ao_entrar, add="+")
        widget.bind("<Leave>", self._ao_sair, add="+")
        widget.bind("<Button-1>", self._ao_sair, add="+")

    def _ao_entrar(self, _event=None):
        self._cancelar_agendado()
        self._after_id = self.widget.after(self.delay, self._mostrar)

    def _ao_sair(self, _event=None):
        self._cancelar_agendado()
        self._esconder()

    def _cancelar_agendado(self):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _mostrar(self):
        if self._tip is not None:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        # Tenta posicionar acima se não couber embaixo
        try:
            screen_h = self.widget.winfo_screenheight()
            if y + 60 > screen_h:
                y = self.widget.winfo_rooty() - 50
        except Exception:
            pass
        self._tip = ctk.CTkToplevel(self.widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        try:
            self._tip.attributes("-topmost", True)
        except Exception:
            pass
        frame = ctk.CTkFrame(
            self._tip, fg_color=self.cor_fundo, corner_radius=8,
            border_width=1, border_color=("#D8D2C3", "#34496A"),
        )
        frame.pack(fill="both", expand=True, padx=0, pady=0)
        label = ctk.CTkLabel(
            frame, text=self.texto,
            font=ctk.CTkFont(family=FONTE, size=11),
            text_color=self.cor_texto,
            wraplength=self.wraplength, justify="left",
            padx=10, pady=6,
        )
        label.pack(fill="both", expand=True)

    def _esconder(self):
        if self._tip is not None:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None


def tooltip(widget, texto, **kwargs):
    """Atalho para criar um ToolTip em um widget."""
    return ToolTip(widget, texto, **kwargs)


def status_badge_cores(status_texto):
    """Mapeia um texto de status para (texto_exibido, cor_texto, cor_fundo)."""
    s = str(status_texto or "").lower()
    if "pensionista" in s:
        return "Pensionista", ROXO_CLARO, ROXO_ESCURO
    if "inativo" in s:
        return "Inativo", AZUL_CLARO, "#1B3A74"
    if "ativo" in s:
        return "Ativo", VERDE_CLARO, VERDE_ESCURO
    if s in ("ok", "concluída", "concluida", "concluído", "concluido", "concluído!"):
        return "Concluído", VERDE_CLARO, VERDE_ESCURO
    if s in ("erro", "falha"):
        return "Erro", VERMELHO_CLARO, "#7f1d1d"
    if "pendente" in s or "andamento" in s:
        return "Pendente", LARANJA_CLARO, "#78350f"
    if status_texto:
        return str(status_texto).title(), "#e5e7eb", "#374151"
    return "Não informado", "#9ca3af", "#374151"


# ============================================================== ÍCONES
# Conjunto padronizado de emojis para usar em todas as telas
ICONES = {
    "dashboard": "📊",
    "consulta": "🔍",
    "admin": "⚙️",
    "backup": "💾",
    "usuarios": "👥",
    "processos": "📋",
    "importacao": "📥",
    "exportacao": "📤",
    "logs": "📜",
    "config": "🔧",
    "senha": "🔑",
    "deletar": "🗑️",
    "editar": "✏️",
    "salvar": "💾",
    "sucesso": "✓",
    "erro": "✕",
    "alerta": "⚠️",
    "info": "ℹ️",
    "sair": "⏻",
    "voltar": "←",
    "avancar": "→",
    "atualizar": "🔄",
    "olho": "👁",
    "pessoa": "👤",
    "relogio": "🕒",
    "calendario": "📅",
    "arquivo": "📄",
    "tabela": "📊",
    "grafico_barra": "📊",
    "grafico_rosca": "🍩",
    "fazenda": "🏛️",
    "tempo": "⏱️",
    "busca": "🔎",
    "filtrar": "🗂️",
    "download": "⬇️",
    "upload": "⬆️",
    "novo": "➕",
    "check": "✅",
    "estrela": "⭐",
    "raio": "⚡",
    "escudo": "🛡️",
    "alvo": "🎯",
}


def icone(chave):
    """Retorna o emoji/ícone pelo nome."""
    return ICONES.get(chave, "•")
