"""
Snake — Edição Premium (Pygame 2)
Visual de nível loja de jogos.

Recursos visuais:
- Fundo animado com estrelas cadentes + grade pulsante
- Cobra com glow dinâmico, trilha de partículas e luz radial
- Comida com efeito de halo + rotação + brilho
- Partículas explosivas + popups com escala + combo
- Shake de ecrã em eventos impactantes
- Transições suaves (fade/scale) entre painéis
- HUD refinado com ícones e animações

Controlos:
Setas/WASD .... mover
ESPAÇO ......... pausar
R .............. reiniciar
Q/ESC .......... sair
"""
import math
import random
import sys
import time

import pygame

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
CELL = 24
GRID_L = 28
GRID_A = 20
HUD = 64
LARGURA = GRID_L * CELL
ALTURA = HUD + GRID_A * CELL
FPS = 60

VEL_INICIAL = 6.0
VEL_MAX = 12.0

# Paleta
BG = (12, 14, 26)
BG_GRADE = (22, 24, 46)
BG_BORDA = (60, 68, 120)
CABECA = (150, 255, 170)
CORPO_A = (70, 220, 120)
CORPO_B = (30, 130, 70)
COMIDA = (255, 80, 100)
BONUS = (255, 215, 60)
TEXTO = (240, 244, 255)
SUBTEXTO = (140, 150, 180)
ACENTO = (80, 200, 255)
VERDE = (120, 255, 150)
AMARELO = (255, 230, 110)
VERMELHO = (255, 100, 115)

DIRECOES = {
    pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
}

OPOSTO = {(0, -1): (0, 1), (0, 1): (0, -1), (-1, 0): (1, 0), (1, 0): (-1, 0)}


class JogoSnakePremium:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake Edição Premium")
        self.ecra = pygame.display.set_mode((LARGURA, ALTURA))
        self.relogio = pygame.time.Clock()

        self.fontes = {
            "titulo": self._criar_fonte(46, True),
            "hud": self._criar_fonte(22, True),
            "normal": self._criar_fonte(18),
            "pequena": self._criar_fonte(14),
        }

        self.sons = self._criar_sons()
        self.estrelas = self._criar_estrelas()
        self.glow_snake = self._criar_glow(40, (80, 255, 130))
        self.glow_comida = self._criar_glow(36, COMIDA)
        self.glow_bonus = self._criar_glow(36, BONUS)
        self.grade_cache = None
        self._renderizar_grade()

        self.estado = "INICIO"
        self.high_score = self._carregar_high_score()
        self.p = 0.0
        self.particulas = []
        self.mensagens = []
        self.trilha = []
        self.flash_tempo = 0.0
        self.flash_cor = None
        self.shake = 0.0
        self.combo = 0
        self.tempo_anim = 0.0
        self.transicao_alpha = 255
        self.transicao_destino = "INICIO"
        self.reset()

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------
    def _criar_fonte(self, tamanho, negrito=False):
        for nome in ("bahnschrift", "segoeui", "consolas", "arial"):
            try:
                return pygame.font.SysFont(nome, tamanho, bold=negrito)
            except Exception:
                continue
        return pygame.font.Font(None, tamanho)

    def _celula_px(self, pos):
        return (pos[0] * CELL + CELL // 2, HUD + pos[1] * CELL + CELL // 2)

    def _dist(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    # ------------------------------------------------------------------
    # Sons procedurais
    # ------------------------------------------------------------------
    def _criar_sons(self):
        sons = {}
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)

            def tom(freq, duracao=0.06, volume=0.22, decaimento=1.0):
                taxa = 22050
                n = int(taxa * duracao)
                amostras = bytearray()
                for i in range(n):
                    env = 1.0 - (i / n) * decaimento
                    v = math.sin(2 * math.pi * freq * i / taxa) * env * volume * 32767
                    amostras += int(v).to_bytes(2, "little", signed=True)
                return pygame.mixer.Sound(buffer=bytes(amostras))

            sons["comer"] = tom(660, 0.07)
            sons["bonus"] = tom(880, 0.12)
            sons["gameover"] = tom(200, 0.35)
            sons["vitoria"] = tom(520, 0.5, 0.3)
            sons["combo"] = tom(990, 0.1, 0.25)
        except Exception:
            sons = {}
        return sons

    def _tocar(self, nome):
        snd = self.sons.get(nome)
        if snd:
            snd.play()

    # ------------------------------------------------------------------
    # Fundo animado (estrelas)
    # ------------------------------------------------------------------
    def _criar_estrelas(self):
        estrelas = []
        for _ in range(180):
            estrelas.append({
                "x": random.uniform(0, LARGURA),
                "y": random.uniform(HUD, ALTURA),
                "r": random.uniform(0.3, 1.8),
                "v": random.uniform(2, 8),
                "b": random.uniform(0.3, 1.0),
                "fase": random.uniform(0, 2 * math.pi),
            })
        return estrelas

    def _atualizar_estrelas(self, dt):
        for e in self.estrelas:
            e["y"] += e["v"] * dt
            if e["y"] > ALTURA:
                e["y"] = HUD
                e["x"] = random.uniform(0, LARGURA)

    def _desenhar_estrelas(self):
        t = self.tempo_anim
        for e in self.estrelas:
            brilho = e["b"] * (0.6 + 0.4 * math.sin(t * 1.5 + e["fase"]))
            alpha = int(60 * brilho)
            cor = (200, 210, 255, alpha)
            pygame.draw.circle(self.ecra, cor, (int(e["x"]), int(e["y"])), e["r"])

    # ------------------------------------------------------------------
    # Grade animada
    # ------------------------------------------------------------------
    def _renderizar_grade(self):
        self.grade_cache = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        pygame.draw.rect(self.grade_cache, (*BG_BORDA, 120),
                         (0, HUD, LARGURA, ALTURA - HUD), 2)

    def _desenhar_grade(self):
        self.ecra.blit(self.grade_cache, (0, 0))

    # ------------------------------------------------------------------
    # Glow / Sombras
    # ------------------------------------------------------------------
    def _criar_glow(self, raio, cor):
        n = raio * 2
        surf = pygame.Surface((n, n), pygame.SRCALPHA)
        for i in range(raio, 0, -1):
            t = i / raio
            alpha = int(60 * (1 - t))
            pygame.draw.circle(surf, (cor[0], cor[1], cor[2], alpha),
                               (raio, raio), i)
        return surf

    # ------------------------------------------------------------------
    # High score
    # ------------------------------------------------------------------
    @staticmethod
    def _carregar_high_score():
        try:
            with open("snake_highscore.txt", "r") as f:
                return int(f.read().strip())
        except Exception:
            return 0

    def _guardar_high_score(self):
        try:
            with open("snake_highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Estado do jogo
    # ------------------------------------------------------------------
    def reset(self):
        meio = (GRID_L // 2, GRID_A // 2)
        self.cobra = [meio, (meio[0] - 1, meio[1]), (meio[0] - 2, meio[1])]
        self.direcao = (1, 0)
        self.pontos = 0
        self.bonus = None
        self.bonus_tempo = 0
        self.velocidade = VEL_INICIAL
        self.p = 0.0
        self.combo = 0
        self.trilha = []
        self.particulas = []
        self.mensagens = []
        self.comida = self._posicao_vazia()

    def _posicao_vazia(self):
        ocupado = set(self.cobra)
        if self.bonus:
            ocupado.add(self.bonus)
        livres = [(x, y) for x in range(GRID_L) for y in range(GRID_A)
                  if (x, y) not in ocupado]
        return random.choice(livres) if livres else None

    # ------------------------------------------------------------------
    # Efeitos visuais
    # ------------------------------------------------------------------
    def _explodir(self, pos_px, cor, quantidade=20):
        for _ in range(quantidade):
            ang = random.uniform(0, 2 * math.pi)
            vel = random.uniform(50, 220)
            self.particulas.append({
                "x": float(pos_px[0]), "y": float(pos_px[1]),
                "vx": math.cos(ang) * vel, "vy": math.sin(ang) * vel,
                "vida": random.uniform(0.3, 0.8),
                "cor": cor, "tam": random.randint(2, 5),
            })

    def _trilha_cobra(self):
        if len(self.cobra) > 0:
            cabeca = self.cobra[0]
            cx, cy = self._celula_px(cabeca)
            self.trilha.insert(0, {"x": cx, "y": cy, "vida": 0.5})
            if len(self.trilha) > 30:
                self.trilha.pop()

    def _mensagem(self, texto, pos_px, cor, escala=1.0):
        self.mensagens.append({
            "texto": texto, "x": pos_px[0], "y": pos_px[1],
            "vida": 1.0, "cor": cor, "escala": escala,
        })

    def _atualizar_efeitos(self, dt):
        for p in self.particulas[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vx"] *= 0.95
            p["vy"] *= 0.95
            p["vida"] -= dt
            if p["vida"] <= 0:
                self.particulas.remove(p)

        for t in self.trilha[:]:
            t["vida"] -= dt
            if t["vida"] <= 0:
                self.trilha.remove(t)

        for m in self.mensagens[:]:
            m["y"] -= 40 * dt
            m["vida"] -= dt
            if m["vida"] <= 0:
                self.mensagens.remove(m)

        if self.flash_tempo > 0:
            self.flash_tempo -= dt
            if self.flash_tempo <= 0:
                self.flash_cor = None

        if self.shake > 0:
            self.shake -= dt

        self.tempo_anim += dt

        # Transição de estado
        if self.estado == "TRANSAICAO":
            self.transicao_alpha -= 600 * dt
            if self.transicao_alpha <= 0:
                self.estado = self.transicao_destino
                self.transicao_alpha = 0

    def _flash(self, cor, duracao=0.18):
        self.flash_cor = cor
        self.flash_tempo = duracao

    # ------------------------------------------------------------------
    # Lógica
    # ------------------------------------------------------------------
    def _mover(self):
        dx, dy = self.direcao
        cabeca = self.cobra[0]
        nova = (cabeca[0] + dx, cabeca[1] + dy)

        if not (0 <= nova[0] < GRID_L and 0 <= nova[1] < GRID_A):
            self._fim(venceu=False)
            return
        if nova in self.cobra:
            self._fim(venceu=False)
            return

        self.cobra.insert(0, nova)

        if nova == self.comida:
            self.pontos += 1
            self.combo += 1
            self._tocar("comer" if self.combo < 3 else "combo")
            cx, cy = self._celula_px(nova)
            self._explodir((cx, cy), COMIDA, 25)
            escala = min(1.8, 1.0 + self.combo * 0.15)
            self._mensagem(f"+{self.pontos}" if self.combo > 2 else "+1",
                           (cx, cy), TEXTO, escala)
            self._flash(COMIDA, 0.08)
            self.shake = 0.03
            self.comida = self._posicao_vazia()
            if self.comida is None:
                self._fim(venceu=True)
                return
            if self.bonus is None and random.random() < 0.25:
                self.bonus = self._posicao_vazia()
                self.bonus_tempo = time.time() + 5
            self.velocidade = min(VEL_MAX, self.velocidade + 0.15)
        elif self.bonus and nova == self.bonus:
            self.pontos += 5
            self.combo += 1
            self._tocar("bonus")
            cx, cy = self._celula_px(nova)
            self._explodir((cx, cy), BONUS, 35)
            self._mensagem("+5", (cx, cy), AMARELO, 1.6)
            self._flash(AMARELO, 0.25)
            self.shake = 0.08
            self.bonus = None
            self.velocidade = min(VEL_MAX, self.velocidade + 0.5)
        else:
            self.cobra.pop()
            self.combo = 0

        if self.bonus and time.time() > self.bonus_tempo:
            self.bonus = None

        self._trilha_cobra()

    def _fim(self, venceu=False):
        self._tocar("vitoria" if venceu else "gameover")
        self.shake = 0.2
        if venceu:
            # Explosão final de celebração
            for _ in range(80):
                ang = random.uniform(0, 2 * math.pi)
                vel = random.uniform(80, 300)
                cor = random.choice([AMARELO, VERDE, ACENTO, COMIDA])
                self.particulas.append({
                    "x": float(LARGURA // 2), "y": float(ALTURA // 2),
                    "vx": math.cos(ang) * vel, "vy": math.sin(ang) * vel,
                    "vida": random.uniform(0.5, 1.5),
                    "cor": cor, "tam": random.randint(3, 6),
                })
        self.estado = "TRANSAICAO"
        self.transicao_alpha = 255
        self.transicao_destino = "VITORIA" if venceu else "GAME_OVER"
        if self.pontos > self.high_score:
            self.high_score = self.pontos
            self._guardar_high_score()

    def _mudar_direcao(self, nova):
        if nova != OPOSTO[self.direcao]:
            self.direcao = nova

    # ------------------------------------------------------------------
    # Desenho
    # ------------------------------------------------------------------
    def _pontos_interpolados(self):
        pts = []
        n = len(self.cobra)
        for i, (x, y) in enumerate(self.cobra):
            if i == 0:
                px = x + self.direcao[0] * self.p
                py = y + self.direcao[1] * self.p
            else:
                ant = self.cobra[i - 1]
                px = x + (ant[0] - x) * self.p
                py = y + (ant[1] - y) * self.p
            pts.append((px * CELL + CELL / 2, HUD + py * CELL + CELL / 2))
        return pts

    def _desenhar_cobra(self):
        pts = self._pontos_interpolados()
        n = len(pts)

        # Trilha
        for t in self.trilha:
            alpha = int(30 * t["vida"] / 0.5)
            pygame.draw.circle(self.ecra, (100, 255, 140, alpha),
                               (int(t["x"]), int(t["y"])), 4)

        # Glow da cabeça
        if n > 0:
            xh, yh = pts[0]
            g = self.glow_snake
            alpha = int(80 + 60 * math.sin(self.tempo_anim * 4))
            g.set_alpha(alpha)
            self.ecra.blit(g, g.get_rect(center=(int(xh), int(yh))))

        # Corpo (da cauda para a cabeça)
        for i in range(n - 1, 0, -1):
            t = 1.0 - (i / max(n - 1, 1)) * 0.45
            r = int(CORPO_A[0] + (CORPO_B[0] - CORPO_A[0]) * t)
            g = int(CORPO_A[1] + (CORPO_B[1] - CORPO_A[1]) * t)
            b = int(CORPO_A[2] + (CORPO_B[2] - CORPO_A[2]) * t)
            pygame.draw.circle(self.ecra, (r, g, b),
                               (int(pts[i][0]), int(pts[i][1])), CELL // 2 - 3)

        # Cabeça
        if n > 0:
            xh, yh = pts[0]
            pygame.draw.circle(self.ecra, CABECA,
                               (int(xh), int(yh)), CELL // 2 - 1)

            # Olhos
            dx, dy = self.direcao
            px, py = -dy, dx
            for sinal in (-1, 1):
                ox = xh + dx * 6 + px * sinal * 5
                oy = yh + dy * 6 + py * sinal * 5
                pygame.draw.circle(self.ecra, (255, 255, 255),
                                   (int(ox), int(oy)), 4)
                pygame.draw.circle(self.ecra, (12, 14, 20),
                                   (int(ox + dx * 2), int(oy + dy * 2)), 2)

    def _desenhar_comida(self, pos, cor, glow, raio):
        if pos is None:
            return
        x, y = self._celula_px(pos)
        pulso = 0.5 + 0.5 * math.sin(self.tempo_anim * 5 + pos[0] + pos[1])

        glow.set_alpha(int(70 + 80 * pulso))
        self.ecra.blit(glow, glow.get_rect(center=(x, y)))

        r = int(raio + 3 * pulso)
        pygame.draw.circle(self.ecra, cor, (x, y), r)

        # Brilho especular
        pygame.draw.circle(self.ecra, (255, 255, 255, 120),
                           (x - 3, y - 3), max(1, r - 3))

        # Halo exterior giratório
        ang = self.tempo_anim * 2 + pos[0] * 0.5 + pos[1] * 0.5
        for i in range(6):
            a = ang + i * 2 * math.pi / 6
            hx = x + int(math.cos(a) * (r + 5))
            hy = y + int(math.sin(a) * (r + 5))
            pygame.draw.circle(self.ecra, (255, 255, 255, 60),
                               (hx, hy), 2)

    def _desenhar_hud(self):
        # Fundo HUD com gradiente
        hud = pygame.Surface((LARGURA, HUD), pygame.SRCALPHA)
        for y in range(HUD):
            t = y / HUD
            alpha = int(180 * (1 - t * 0.4))
            hud.fill((10, 12, 26, alpha))
        self.ecra.blit(hud, (0, 0))
        pygame.draw.line(self.ecra, (255, 255, 255, 30),
                         (0, HUD - 1), (LARGURA, HUD - 1), 1)

        # Pontos (esquerda)
        texto_pts = self.fontes["hud"].render(f"Pontos: {self.pontos}", True, TEXTO)
        self.ecra.blit(texto_pts, (14, 18))

        # Combo (junto aos pontos)
        if self.combo > 2:
            cor = AMARELO if self.combo < 5 else VERMELHO
            txt_c = self.fontes["pequena"].render(f"COMBO x{self.combo}", True, cor)
            self.ecra.blit(txt_c, (14, 42))

        # Recorde (direita)
        texto_rec = self.fontes["hud"].render(f"Recorde: {self.high_score}", True, ACENTO)
        self.ecra.blit(texto_rec, (LARGURA - texto_rec.get_width() - 12, 18))

        # Barra de velocidade
        w, h = 130, 4
        x0 = LARGURA // 2 - w // 2
        y0 = 16
        pygame.draw.rect(self.ecra, (35, 40, 70), (x0, y0, w, h), border_radius=2)
        frac = max(0.0, min(1.0, (self.velocidade - VEL_INICIAL) / (VEL_MAX - VEL_INICIAL)))
        if frac > 0:
            cor_barra = ACENTO if frac < 0.6 else (AMARELO if frac < 0.85 else VERMELHO)
            pygame.draw.rect(self.ecra, cor_barra, (x0, y0, int(w * frac), h), border_radius=2)

        txt_vel = self.fontes["pequena"].render(
            f"Velocidade {self.velocidade:.0f}/{VEL_MAX:.0f}", True, SUBTEXTO)
        self.ecra.blit(txt_vel, (LARGURA // 2 - txt_vel.get_width() // 2, y0 + h + 4))

    def _desenhar_particulas(self):
        for p in self.particulas:
            alpha = int(255 * min(1.0, p["vida"] * 2.5))
            t = max(0.1, p["vida"] / 0.8)
            raio = max(1, int(p["tam"] * t))
            pygame.draw.circle(self.ecra, (*p["cor"], alpha),
                               (int(p["x"]), int(p["y"])), raio)

    def _desenhar_mensagens(self):
        for m in self.mensagens:
            alpha = int(255 * min(1.0, m["vida"] / 0.3))
            escala = m.get("escala", 1.0)
            escala_anim = escala * (0.8 + 0.2 * (1 - m["vida"]))
            tam = max(8, int(18 * escala_anim))
            try:
                fonte = self.fontes["normal"]
                surf = fonte.render(m["texto"], True, m["cor"])
                surf = pygame.transform.scale(surf, (int(surf.get_width() * escala_anim / 1.0),
                                                     int(surf.get_height() * escala_anim / 1.0)))
            except Exception:
                surf = self.fontes["normal"].render(m["texto"], True, m["cor"])
            surf.set_alpha(alpha)
            self.ecra.blit(surf, (int(m["x"] - surf.get_width() // 2),
                                  int(m["y"] - surf.get_height() // 2)))

    def _texto_centro(self, texto, chave_fonte, cor, y):
        surf = self.fontes[chave_fonte].render(texto, True, cor)
        x = LARGURA // 2 - surf.get_width() // 2
        self.ecra.blit(surf, (x, y))

    def _desenhar_painel(self, titulo, linhas, cor_titulo):
        # Escurecer
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.ecra.blit(overlay, (0, 0))

        # Medir
        alturas = [self.fontes["titulo"].size(titulo)[1]]
        larg_max = self.fontes["titulo"].size(titulo)[0]
        for texto, chave, _ in linhas:
            s = self.fontes[chave].render(texto, True, TEXTO)
            alturas.append(s.get_height())
            larg_max = max(larg_max, s.get_width())

        esp = 14
        conteudo_alt = alturas[0] + sum(alturas[1:]) + esp * (len(alturas) - 1)
        larg_painel = min(larg_max + 100, LARGURA - 40)
        alt_painel = conteudo_alt + 80

        px = LARGURA // 2 - larg_painel // 2
        py = ALTURA // 2 - alt_painel // 2 - 20

        # Fundo com gradiente
        fundo = pygame.Surface((larg_painel, alt_painel), pygame.SRCALPHA)
        for y in range(alt_painel):
            t = y / alt_painel
            alpha = int(205 + 40 * (1 - t))
            fundo.fill((12, 14, 30, alpha))
        self.ecra.blit(fundo, (px, py))

        # Borda com glow
        pygame.draw.rect(self.ecra, (*cor_titulo, 100),
                         (px, py, larg_painel, alt_painel), 2, border_radius=16)
        # Brilho na borda
        for i in range(4):
            alpha = 20 - i * 4
            pygame.draw.rect(self.ecra, (*cor_titulo, alpha),
                             (px - i, py - i, larg_painel + i * 2, alt_painel + i * 2),
                             1, border_radius=16 + i)

        y = py + 30
        self._texto_centro(titulo, "titulo", cor_titulo, y)
        y += alturas[0] + esp

        for (texto, chave, cor), altura in zip(linhas, alturas[1:]):
            self._texto_centro(texto, chave, cor, y)
            y += altura + esp

    def _desenhar(self):
        # Aplicar shake
        offset_x = 0
        offset_y = 0
        if self.shake > 0:
            offset_x = int(random.uniform(-4, 4) * min(1.0, self.shake / 0.2))
            offset_y = int(random.uniform(-4, 4) * min(1.0, self.shake / 0.2))

        self.ecra.fill(BG)
        self._desenhar_grade()
        self._desenhar_estrelas()

        # Elementos de jogo (com offset de shake)
        buffer = self.ecra if self.shake <= 0 else pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        if self.shake > 0:
            buffer.fill((0, 0, 0, 0))

        if self.estado in ("INICIO", "JOGANDO", "PAUSADO", "GAME_OVER", "VITORIA", "TRANSAICAO"):
            self._desenhar_comida(self.comida, COMIDA, self.glow_comida, 6)
            if self.bonus and time.time() < self.bonus_tempo:
                self._desenhar_comida(self.bonus, BONUS, self.glow_bonus, 7)
            self._desenhar_cobra()
            self._desenhar_particulas()
            self._desenhar_mensagens()

        if self.shake > 0:
            self.ecra.blit(buffer, (offset_x, offset_y))

        self._desenhar_hud()

        # Flash
        if self.flash_tempo > 0 and self.flash_cor:
            f = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            f.fill((*self.flash_cor, int(60 * self.flash_tempo / 0.18)))
            self.ecra.blit(f, (0, 0))

        # Painéis
        if self.estado == "INICIO":
            self._desenhar_painel("SNAKE", [
                ("Use as setas ou WASD para mover", "normal", SUBTEXTO),
                ("ESPACO pausa  |  R reinicia  |  Q sai", "pequena", SUBTEXTO),
                ("PRESSIONE ENTER PARA JOGAR", "hud", VERDE),
            ], ACENTO)
        elif self.estado == "PAUSADO":
            self._desenhar_painel("PAUSA", [
                ("ESPACO para continuar", "normal", SUBTEXTO),
            ], TEXTO)
        elif self.estado == "GAME_OVER":
            linhas = [
                (f"Pontuação: {self.pontos}", "hud", TEXTO),
            ]
            if self.pontos >= self.high_score and self.pontos > 0:
                linhas.append(("NOVO RECORDE!", "hud", AMARELO))
            else:
                linhas.append((f"Recorde: {self.high_score}", "normal", SUBTEXTO))
            linhas.append(("ENTER ou R para jogar novamente", "pequena", SUBTEXTO))
            self._desenhar_painel("FIM DE JOGO", linhas, VERMELHO)
        elif self.estado == "VITORIA":
            self._desenhar_painel("VITÓRIA!", [
                (f"Pontuação: {self.pontos}", "hud", TEXTO),
                ("ENTER ou R para jogar novamente", "pequena", SUBTEXTO),
            ], AMARELO)

        # Transição
        if self.estado == "TRANSAICAO":
            t = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            t.fill((0, 0, 0, max(0, min(255, int(self.transicao_alpha)))))
            self.ecra.blit(t, (0, 0))

    # ------------------------------------------------------------------
    # Entradas e loop
    # ------------------------------------------------------------------
    def _tratar_tecla(self, tecla):
        if tecla in (pygame.K_ESCAPE, pygame.K_q):
            self._sair()
        if tecla == pygame.K_r:
            self.reset()
            self.estado = "JOGANDO"
            return

        if self.estado == "INICIO":
            if tecla in (pygame.K_RETURN, pygame.K_SPACE):
                self.reset()
                self.estado = "JOGANDO"
        elif self.estado == "JOGANDO":
            if tecla == pygame.K_SPACE:
                self.estado = "PAUSADO"
            elif tecla in DIRECOES:
                self._mudar_direcao(DIRECOES[tecla])
        elif self.estado == "PAUSADO":
            if tecla == pygame.K_SPACE:
                self.estado = "JOGANDO"
        elif self.estado in ("GAME_OVER", "VITORIA"):
            if tecla in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                self.reset()
                self.estado = "JOGANDO"

    def jogar(self):
        acumulador = 0.0
        while True:
            dt = self.relogio.tick(FPS) / 1000.0

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self._sair()
                elif evento.type == pygame.KEYDOWN:
                    self._tratar_tecla(evento.key)

            if self.estado == "JOGANDO":
                if self.bonus and time.time() > self.bonus_tempo:
                    self.bonus = None
                acumulador += dt
                intervalo = 1.0 / self.velocidade
                while acumulador >= intervalo:
                    acumulador -= intervalo
                    self._mover()
                    if self.estado != "JOGANDO":
                        break
                self.p = max(0.0, min(1.0, acumulador / intervalo)) if self.estado == "JOGANDO" else 0.0
            else:
                acumulador = 0.0
                self.p = 0.0

            self._atualizar_estrelas(dt)
            self._atualizar_efeitos(dt)
            self._desenhar()
            pygame.display.flip()

    def _sair(self):
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    JogoSnakePremium().jogar()
