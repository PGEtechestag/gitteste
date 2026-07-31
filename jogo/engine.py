# engine.py
import pygame
from particulas import SistemaParticulas
from config import (
    LARGURA, ALTURA, FPS, OPCOES_FPS, 
    COR_FUNDO, COR_TEXTO, COR_COMIDA
)
from cobra import Cobra
from mapa import Mapa
from audio import GerenciadorAudio
from menu import InterfaceMenu

class JogoSnake:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Snake 3D Fluido - Cel-Shaded")
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.Font(None, 28)

        self.audio = GerenciadorAudio()
        self.cobra = Cobra()
        self.mapa = Mapa()
        self.menu = InterfaceMenu(self)
        self.particulas = SistemaParticulas()

        # Máquina de estados: "MENU", "CONFIG", "JOGANDO"
        self.estado = "MENU"
        self.fps_alvo = FPS
        self.rodando = True

        self.reiniciar()

    def mudar_estado(self, novo_estado):
        if novo_estado == "JOGANDO" and self.game_over:
            self.reiniciar()
        self.estado = novo_estado

    def fechar_jogo(self):
        self.rodando = False

    def ajustar_volume(self, delta):
        novo_vol = round(self.audio.volume + delta, 1)
        self.audio.definir_volume(novo_vol)

    def alternar_fps(self):
        idx = OPCOES_FPS.index(self.fps_alvo)
        self.fps_alvo = OPCOES_FPS[(idx + 1) % len(OPCOES_FPS)]

    def reiniciar(self):
        self.cobra.resetar()
        self.mapa.gerar_comida(self.cobra.segmentos)
        self.pontuacao = 0
        self.game_over = False

    def processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if self.estado in ("MENU", "CONFIG"):
                self.menu.processar_eventos(evento, self.estado)

            elif self.estado == "JOGANDO":
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.mudar_estado("MENU")
                    elif self.game_over:
                        if evento.key == pygame.K_r:
                            self.reiniciar()
                    else:
                        if evento.key in (pygame.K_UP, pygame.K_w):
                            self.cobra.mudar_direcao([0, -1])
                        elif evento.key in (pygame.K_DOWN, pygame.K_s):
                            self.cobra.mudar_direcao([0, 1])
                        elif evento.key in (pygame.K_LEFT, pygame.K_a):
                            self.cobra.mudar_direcao([-1, 0])
                        elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                            self.cobra.mudar_direcao([1, 0])

        return self.rodando

    def atualizar(self, dt):
        if self.estado != "JOGANDO" or self.game_over:
            return

        self.cobra.atualizar(dt)

        if self.cobra.verificar_colisao_parede() or self.cobra.verificar_autocolisao():
            self.game_over = True
            self.audio.tocar_game_over()
            return

        if self.mapa.verificar_colisao_comida(self.cobra.segmentos[0]):
            self.pontuacao += 10
            # Emite explosão de partículas de comida estilo Borderlands
            self.particulas.emitir(self.mapa.comida[0], self.mapa.comida[1], COR_COMIDA, quantidade=16)
            self.cobra.crescer()
            self.mapa.gerar_comida(self.cobra.segmentos)
            self.audio.tocar_comida()

    def desenhar(self):
        self.tela.fill(COR_FUNDO)

        if self.estado == "MENU":
            self.menu.desenhar_menu(self.tela)

        elif self.estado == "CONFIG":
            self.menu.desenhar_config(self.tela)

        elif self.estado == "JOGANDO":
            # 1. Desenha o chão e comida
            self.mapa.desenhar(self.tela)
            
            # 2. Desenha a cobra com os olhos expressivos
            self.cobra.desenhar(self.tela)

            # 3. Desenha as partículas por cima dos elementos do jogo
            self.particulas.atualizar_e_desenhar(0.016, self.tela)

            # 4. Interface (Score / Game Over)
            texto_pontos = self.fonte.render(f"Pontos: {self.pontuacao}", True, COR_TEXTO)
            self.tela.blit(texto_pontos, (10, 10))

            if self.game_over:
                texto_over = self.fonte.render("GAME OVER", True, COR_COMIDA)
                texto_reiniciar = self.fonte.render("Pressione [R] para reiniciar ou [ESC] para o Menu", True, COR_TEXTO)

                rect_over = texto_over.get_rect(center=(LARGURA // 2, ALTURA // 2 - 20))
                rect_reiniciar = texto_reiniciar.get_rect(center=(LARGURA // 2, ALTURA // 2 + 20))

                self.tela.blit(texto_over, rect_over)
                self.tela.blit(texto_reiniciar, rect_reiniciar)

        pygame.display.flip()

    def executar(self):
        while self.rodando:
            dt = self.relogio.tick(self.fps_alvo) / 1000.0
            if dt > 0.05:
                dt = 0.05

            self.rodando = self.processar_eventos()
            self.atualizar(dt)
            self.desenhar()

        pygame.quit()