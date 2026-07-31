# mapa.py
import random
import math
import pygame
from config import LARGURA, ALTURA, TAMANHO_BLOCO, RAIO_COBRA, COR_COMIDA, COR_FUNDO
from gfx import criar_textura_cel_shaded, criar_sombra_projetada

class Mapa:
    def __init__(self):
        self.tex_comida = criar_textura_cel_shaded(RAIO_COBRA, COR_COMIDA)
        self.tex_sombra = criar_sombra_projetada(RAIO_COBRA)
        self.comida = [0.0, 0.0]
        self.surface_grid = self._criar_surface_grid()

    def _criar_surface_grid(self):
        """Desenha um fundo com grade e bordas estilo HQ/Borderlands."""
        grid_surf = pygame.Surface((LARGURA, ALTURA))
        grid_surf.fill(COR_FUNDO)

        # Cor das linhas da grade
        cor_linha = (40, 44, 60)
        cor_borda = (10, 10, 12)

        # 1. Desenha as linhas verticais e horizontais da grade
        for x in range(0, LARGURA, TAMANHO_BLOCO):
            pygame.draw.line(grid_surf, cor_linha, (x, 0), (x, ALTURA), 1)
        for y in range(0, ALTURA, TAMANHO_BLOCO):
            pygame.draw.line(grid_surf, cor_linha, (0, y), (LARGURA, y), 1)

        # 2. Desenha a borda grossa preta ao redor de todo o mapa (Estilo Comic Book)
        pygame.draw.rect(grid_surf, cor_borda, (0, 0, LARGURA, ALTURA), 6)

        return grid_surf

    def gerar_comida(self, segmentos_cobra):
        # Gera a posição alinhada exatamente ao centro dos blocos da grade
        colunas = (LARGURA // TAMANHO_BLOCO) - 2
        linhas = (ALTURA // TAMANHO_BLOCO) - 2

        while True:
            grid_x = random.randint(1, colunas)
            grid_y = random.randint(1, linhas)

            # Posição centralizada no bloco
            x = float(grid_x * TAMANHO_BLOCO + TAMANHO_BLOCO // 2)
            y = float(grid_y * TAMANHO_BLOCO + TAMANHO_BLOCO // 2)

            # Evita gerar em cima do corpo da cobra
            valido = True
            for seg in segmentos_cobra:
                if math.hypot(seg[0] - x, seg[1] - y) < RAIO_COBRA * 1.8:
                    valido = False
                    break

            if valido:
                self.comida = [x, y]
                break

    def verificar_colisao_comida(self, cabeca_cobra):
        dist_comida = math.hypot(cabeca_cobra[0] - self.comida[0], cabeca_cobra[1] - self.comida[1])
        return dist_comida < RAIO_COBRA * 1.8

    def desenhar(self, tela):
        # 1. Desenha o chão com a grade HQ
        tela.blit(self.surface_grid, (0, 0))

        # 2. Desenha a sombra projetada da comida
        sombra_w = self.tex_sombra.get_width()
        sombra_h = self.tex_sombra.get_height()
        tela.blit(self.tex_sombra, (self.comida[0] - sombra_w // 2, self.comida[1] + 2 - sombra_h // 2))

        # 3. Desenha a comida (Offset corrigido para o centro exato)
        offset_x = self.tex_comida.get_width() // 2
        offset_y = self.tex_comida.get_height() // 2
        tela.blit(self.tex_comida, (self.comida[0] - offset_x, self.comida[1] - offset_y))