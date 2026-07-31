# gfx.py
import pygame
import math

CACHE_TEXTURAS = {}

def criar_textura_cel_shaded(raio, cor_base, cor_outline=(10, 10, 12)):
    """Gera uma esfera estilo Cartoon/Borderlands com Toon Shading e Outline."""
    chave_cache = (raio, cor_base, cor_outline)
    if chave_cache in CACHE_TEXTURAS:
        return CACHE_TEXTURAS[chave_cache]

    tamanho = (raio + 3) * 2
    centro = tamanho // 2
    surface = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)

    # 1. Desenha o Contorno de Tinta (Ink Line)
    pygame.draw.circle(surface, cor_outline, (centro, centro), raio + 2)

    # 2. Toon Shading (3 Tons Discretos de Cor)
    cor_sombra = (max(0, cor_base[0] - 80), max(0, cor_base[1] - 80), max(0, cor_base[2] - 80))
    cor_brilho = (min(255, cor_base[0] + 60), min(255, cor_base[1] + 60), min(255, cor_base[2] + 60))

    # Base (Tom Médio)
    pygame.draw.circle(surface, cor_base, (centro, centro), raio)

    # Sombra Inferior (Corte Seco)
    sombra_surf = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
    pygame.draw.circle(sombra_surf, cor_sombra, (centro + 2, centro + 3), raio - 1)
    # Mascara a sombra para ficar dentro do círculo principal
    mascara = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
    pygame.draw.circle(mascara, (255, 255, 255, 255), (centro, centro), raio)
    sombra_surf.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(sombra_surf, (0, 0))

    # Ponto de Brilho Cartoon (Highlight / Specular Seco)
    offset_luz = (centro - int(raio * 0.3), centro - int(raio * 0.3))
    pygame.draw.circle(surface, cor_brilho, offset_luz, int(raio * 0.35))
    pygame.draw.circle(surface, (255, 255, 255), (offset_luz[0] - 1, offset_luz[1] - 1), int(raio * 0.15))

    CACHE_TEXTURAS[chave_cache] = surface
    return surface

def criar_sombra_projetada(raio):
    """Gera uma sombra no chão estilizada."""
    tamanho = (raio * 2) + 8
    surface = pygame.Surface((tamanho, tamanho // 2), pygame.SRCALPHA)
    pygame.draw.ellipse(surface, (10, 10, 15, 120), (0, 0, tamanho, tamanho // 2))
    return surface