import pygame
import random
import math

# Configurações globais / Constantes
LARGURA = 600
ALTURA = 600
TAMANHO_BLOCO = 20
FPS = 120

VELOCIDADE_COBRA = 220.0  # Pixels por segundo
RAIO_COBRA = 10           # Raio para renderização e hitbox
DISTANCIA_SEGMENTOS = 14  # Espaçamento para o visual cilíndrico contínuo

# Cores (RGB)
COR_FUNDO = (18, 18, 24)
COR_COMIDA = (231, 76, 60)
COR_TEXTO = (236, 240, 241)

# Pré-renderiza texturas 3D (Bolinhas iluminadas) para máxima performance
def criar_textura_esfera_3d(raio, cor_base):
    tamanho = raio * 2
    surface = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
    
    for y in range(tamanho):
        for x in range(tamanho):
            dx = x - raio
            dy = y - raio
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist <= raio:
                nx = dx / raio
                ny = dy / raio
                nz = math.sqrt(max(0, 1.0 - (nx*nx + ny*ny)))
                
                # Direção da Luz
                lx, ly, lz = -0.4, -0.4, 0.8
                iluminacao = max(0.2, (nx*lx + ny*ly + nz*lz))
                
                r = min(255, int(cor_base[0] * iluminacao + 40 * (iluminacao**3)))
                g = min(255, int(cor_base[1] * iluminacao + 40 * (iluminacao**3)))
                b = min(255, int(cor_base[2] * iluminacao + 40 * (iluminacao**3)))
                
                surface.set_at((x, y), (r, g, b, 255))
                
    return surface


class JogoSnake:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Snake 3D Fluido - Pygame")
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.Font(None, 28)

        # Pré-geração das esferas 3D
        self.tex_cabeca = criar_textura_esfera_3d(RAIO_COBRA, (46, 204, 113))
        self.tex_corpo = criar_textura_esfera_3d(RAIO_COBRA, (39, 174, 96))
        self.tex_comida = criar_textura_esfera_3d(RAIO_COBRA, (231, 76, 60))

        self.reiniciar()

    def reiniciar(self):
        self.cabeca_x = float(LARGURA // 2)
        self.cabeca_y = float(ALTURA // 2)

        # O corpo é composto por coordenadas [x, y] exatas
        self.segmentos = []
        num_segmentos_iniciais = 6
        for i in range(num_segmentos_iniciais):
            self.segmentos.append([
                self.cabeca_x - (i * DISTANCIA_SEGMENTOS), 
                self.cabeca_y
            ])

        self.direcao = [1, 0]  # Vetor de direção [x, y]
        self.proxima_direcao = [1, 0]
        self.pontuacao = 0
        self.game_over = False
        self._gerar_comida()

    def _gerar_comida(self):
        margem = 30
        while True:
            x = float(random.randrange(margem, LARGURA - margem, TAMANHO_BLOCO))
            y = float(random.randrange(margem, ALTURA - margem, TAMANHO_BLOCO))
            self.comida = [x, y]
            
            # Garante que não renasça em cima do corpo
            valido = True
            for seg in self.segmentos:
                if math.hypot(seg[0] - x, seg[1] - y) < RAIO_COBRA * 2:
                    valido = False
                    break
            if valido:
                break

    def processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.KEYDOWN:
                if self.game_over:
                    if evento.key == pygame.K_r:
                        self.reiniciar()
                    elif evento.key == pygame.K_ESCAPE:
                        return False

                # Altera a direção impedindo inverter 180º no mesmo eixo
                elif evento.key in (pygame.K_UP, pygame.K_w) and self.direcao[1] == 0:
                    self.proxima_direcao = [0, -1]
                elif evento.key in (pygame.K_DOWN, pygame.K_s) and self.direcao[1] == 0:
                    self.proxima_direcao = [0, 1]
                elif evento.key in (pygame.K_LEFT, pygame.K_a) and self.direcao[0] == 0:
                    self.proxima_direcao = [-1, 0]
                elif evento.key in (pygame.K_RIGHT, pygame.K_d) and self.direcao[0] == 0:
                    self.proxima_direcao = [1, 0]

        return True

    def atualizar(self, dt):
        if self.game_over:
            return

        self.direcao = self.proxima_direcao

        # 1. Atualiza posição da cabeça
        passo = VELOCIDADE_COBRA * dt
        self.segmentos[0][0] += self.direcao[0] * passo
        self.segmentos[0][1] += self.direcao[1] * passo

        cabeca = self.segmentos[0]

        # 2. Ajusta o corpo uniformemente (Inverse Kinematics / Efeito Cobra Cilíndrica)
        for i in range(1, len(self.segmentos)):
            lider = self.segmentos[i - 1]
            atual = self.segmentos[i]

            dx = lider[0] - atual[0]
            dy = lider[1] - atual[1]
            distancia = math.hypot(dx, dy)

            if distancia > 0:
                fator = DISTANCIA_SEGMENTOS / distancia
                atual[0] = lider[0] - (dx * fator)
                atual[1] = lider[1] - (dy * fator)

        # 3. Colisão com Paredes
        if (cabeca[0] - RAIO_COBRA < 0 or cabeca[0] + RAIO_COBRA >= LARGURA or
            cabeca[1] - RAIO_COBRA < 0 or cabeca[1] + RAIO_COBRA >= ALTURA):
            self.game_over = True
            return

        # 4. Colisão com o Próprio Corpo
        raio_hitbox = RAIO_COBRA * 0.85
        for i in range(4, len(self.segmentos)):
            seg = self.segmentos[i]
            dist_centro = math.hypot(cabeca[0] - seg[0], cabeca[1] - seg[1])
            if dist_centro < raio_hitbox * 2:
                self.game_over = True
                return

        # 5. Colisão com a Comida
        dist_comida = math.hypot(cabeca[0] - self.comida[0], cabeca[1] - self.comida[1])
        if dist_comida < RAIO_COBRA * 2:
            self.pontuacao += 10
            cauda = self.segmentos[-1]
            self.segmentos.append([cauda[0], cauda[1]])
            self._gerar_comida()

    def desenhar(self):
        self.tela.fill(COR_FUNDO)

        # Desenha Comida 3D
        self.tela.blit(self.tex_comida, (self.comida[0] - RAIO_COBRA, self.comida[1] - RAIO_COBRA))

        # Desenha o Corpo da Cobra (de trás para frente)
        for i in range(len(self.segmentos) - 1, 0, -1):
            seg = self.segmentos[i]
            self.tela.blit(self.tex_corpo, (seg[0] - RAIO_COBRA, seg[1] - RAIO_COBRA))

        # Desenha a Cabeça 3D
        cabeca = self.segmentos[0]
        self.tela.blit(self.tex_cabeca, (cabeca[0] - RAIO_COBRA, cabeca[1] - RAIO_COBRA))

        # Placar
        texto_pontos = self.fonte.render(f"Pontos: {self.pontuacao}", True, COR_TEXTO)
        self.tela.blit(texto_pontos, (10, 10))

        # Game Over
        if self.game_over:
            texto_over = self.fonte.render("GAME OVER", True, COR_COMIDA)
            texto_reiniciar = self.fonte.render("Pressione [R] para reiniciar ou [ESC] para sair", True, COR_TEXTO)

            rect_over = texto_over.get_rect(center=(LARGURA // 2, ALTURA // 2 - 20))
            rect_reiniciar = texto_reiniciar.get_rect(center=(LARGURA // 2, ALTURA // 2 + 20))

            self.tela.blit(texto_over, rect_over)
            self.tela.blit(texto_reiniciar, rect_reiniciar)

        pygame.display.flip()

    def executar(self):
        rodando = True
        while rodando:
            dt = self.relogio.tick(FPS) / 1000.0
            if dt > 0.05: dt = 0.05  # Previne saltos no lag
            
            rodando = self.processar_eventos()
            self.atualizar(dt)
            self.desenhar()

        pygame.quit()


if __name__ == "__main__":
    jogo = JogoSnake()
    jogo.executar()