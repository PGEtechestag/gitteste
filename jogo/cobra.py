# cobra.py
import math
import pygame
from config import LARGURA, ALTURA, VELOCIDADE_COBRA, RAIO_COBRA, DISTANCIA_SEGMENTOS, COR_CABECA, COR_CORPO
from gfx import criar_textura_cel_shaded, criar_sombra_projetada

class Cobra:
    def __init__(self):
        self.tex_cabeca = criar_textura_cel_shaded(RAIO_COBRA + 1, COR_CABECA)
        self.tex_corpo = criar_textura_cel_shaded(RAIO_COBRA, COR_CORPO)
        self.tex_sombra = criar_sombra_projetada(RAIO_COBRA)
        self.resetar()

    def resetar(self):
        self.cabeca_x = float(LARGURA // 2)
        self.cabeca_y = float(ALTURA // 2)

        self.segmentos = []
        num_segmentos_iniciais = 6
        for i in range(num_segmentos_iniciais):
            self.segmentos.append([
                self.cabeca_x - (i * DISTANCIA_SEGMENTOS), 
                self.cabeca_y
            ])

        self.direcao = [1, 0]
        self.proxima_direcao = [1, 0]

    def mudar_direcao(self, nova_direcao):
        if nova_direcao[0] != 0 and self.direcao[0] == 0:
            self.proxima_direcao = nova_direcao
        elif nova_direcao[1] != 0 and self.direcao[1] == 0:
            self.proxima_direcao = nova_direcao

    def atualizar(self, dt):
        self.direcao = self.proxima_direcao

        passo = VELOCIDADE_COBRA * dt
        self.segmentos[0][0] += self.direcao[0] * passo
        self.segmentos[0][1] += self.direcao[1] * passo

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

    def crescer(self):
        cauda = self.segmentos[-1]
        self.segmentos.append([cauda[0], cauda[1]])

    def verificar_colisao_parede(self):
        cabeca = self.segmentos[0]
        return (cabeca[0] - RAIO_COBRA < 0 or cabeca[0] + RAIO_COBRA >= LARGURA or
                cabeca[1] - RAIO_COBRA < 0 or cabeca[1] + RAIO_COBRA >= ALTURA)

    def verificar_autocolisao(self):
        cabeca = self.segmentos[0]
        raio_hitbox = RAIO_COBRA * 0.85
        for i in range(4, len(self.segmentos)):
            seg = self.segmentos[i]
            if math.hypot(cabeca[0] - seg[0], cabeca[1] - seg[1]) < raio_hitbox * 2:
                return True
        return False

    def desenhar(self, tela):
        # 1. Passada de Sombras no chão (Centralizada)
        sombra_w = self.tex_sombra.get_width() // 2
        sombra_h = self.tex_sombra.get_height() // 2
        for seg in self.segmentos:
            tela.blit(self.tex_sombra, (seg[0] - sombra_w, seg[1] + 4 - sombra_h))

        # 2. Desenha o Corpo (do rabo para a cabeça)
        offset_corpo_x = self.tex_corpo.get_width() // 2
        offset_corpo_y = self.tex_corpo.get_height() // 2
        for i in range(len(self.segmentos) - 1, 0, -1):
            seg = self.segmentos[i]
            tela.blit(self.tex_corpo, (seg[0] - offset_corpo_x, seg[1] - offset_corpo_y))

        # 3. Desenha a Cabeça
        cabeca = self.segmentos[0]
        offset_cabeca_x = self.tex_cabeca.get_width() // 2
        offset_cabeca_y = self.tex_cabeca.get_height() // 2
        tela.blit(self.tex_cabeca, (cabeca[0] - offset_cabeca_x, cabeca[1] - offset_cabeca_y))

        # 4. Olhos Cartoon que olham para a direção do movimento
        dx, dy = self.direcao[0], self.direcao[1]
        olho_dist = 6
        olho_raio = 4

        px, py = -dy * olho_dist, dx * olho_dist
        
        olho1_x = int(cabeca[0] + dx * 6 + px)
        olho1_y = int(cabeca[1] + dy * 6 + py)
        olho2_x = int(cabeca[0] + dx * 6 - px)
        olho2_y = int(cabeca[1] + dy * 6 - py)

        for ox, oy in [(olho1_x, olho1_y), (olho2_x, olho2_y)]:
            pygame.draw.circle(tela, (10, 10, 12), (ox, oy), olho_raio + 1)
            pygame.draw.circle(tela, (255, 255, 255), (ox, oy), olho_raio)
            pygame.draw.circle(tela, (10, 10, 12), (ox + dx * 2, oy + dy * 2), 2)