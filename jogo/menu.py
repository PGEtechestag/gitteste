# menu.py
import pygame
from config import (
    LARGURA, ALTURA, COR_TEXTO, COR_DESTAQUE, 
    COR_BOTAO, COR_BOTAO_HOVER, OPCOES_FPS
)

class Botao:
    def __init__(self, x, y, largura, altura, texto, acao=None):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.acao = acao

    def desenhar(self, tela, fonte):
        mouse_pos = pygame.mouse.get_pos()
        cor = COR_BOTAO_HOVER if self.rect.collidepoint(mouse_pos) else COR_BOTAO

        pygame.draw.rect(tela, cor, self.rect, border_radius=8)
        pygame.draw.rect(tela, COR_DESTAQUE, self.rect, width=2, border_radius=8)

        surface_texto = fonte.render(self.texto, True, COR_TEXTO)
        rect_texto = surface_texto.get_rect(center=self.rect.center)
        tela.blit(surface_texto, rect_texto)

    def checar_clique(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos) and self.acao:
                self.acao()


class InterfaceMenu:
    def __init__(self, engine):
        self.engine = engine
        self.fonte_titulo = pygame.font.Font(None, 48)
        self.fonte_botoes = pygame.font.Font(None, 32)
        
        self._criar_botoes_menu()
        self._criar_botoes_config()

    def _criar_botoes_menu(self):
        cx, cy = LARGURA // 2, ALTURA // 2
        self.botoes_menu = [
            Botao(cx - 100, cy - 60, 200, 45, "JOGAR", lambda: self.engine.mudar_estado("JOGANDO")),
            Botao(cx - 100, cy + 10, 200, 45, "OPÇÕES", lambda: self.engine.mudar_estado("CONFIG")),
            Botao(cx - 100, cy + 80, 200, 45, "SAIR", lambda: self.engine.fechar_jogo())
        ]

    def _criar_botoes_config(self):
        cx = LARGURA // 2
        self.botoes_config = [
            # Controle de Volume (- / +)
            Botao(cx - 110, 200, 40, 40, "-", lambda: self.engine.ajustar_volume(-0.1)),
            Botao(cx + 70, 200, 40, 40, "+", lambda: self.engine.ajustar_volume(0.1)),
            
            # Controle de FPS
            Botao(cx - 110, 310, 220, 40, "ALTERAR FPS", lambda: self.engine.alternar_fps()),
            
            # Voltar
            Botao(cx - 100, 440, 200, 45, "VOLTAR", lambda: self.engine.mudar_estado("MENU"))
        ]

    def processar_eventos(self, evento, estado_atual):
        botoes = self.botoes_menu if estado_atual == "MENU" else self.botoes_config
        for b in botoes:
            b.checar_clique(evento)

    def desenhar_menu(self, tela):
        # Título
        txt_titulo = self.fonte_titulo.render("SNAKE 3D", True, COR_DESTAQUE)
        tela.blit(txt_titulo, txt_titulo.get_rect(center=(LARGURA // 2, 140)))

        for b in self.botoes_menu:
            b.desenhar(tela, self.fonte_botoes)

    def desenhar_config(self, tela):
        # Título Opções
        txt_titulo = self.fonte_titulo.render("CONFIGURAÇÕES", True, COR_DESTAQUE)
        tela.blit(txt_titulo, txt_titulo.get_rect(center=(LARGURA // 2, 100)))

        # Seção Volume
        vol_pct = int(self.engine.audio.volume * 100)
        txt_vol = self.fonte_botoes.render(f"Volume: {vol_pct}%", True, COR_TEXTO)
        tela.blit(txt_vol, txt_vol.get_rect(center=(LARGURA // 2, 220)))

        # Seção FPS
        txt_fps = self.fonte_botoes.render(f"FPS Alvo: {self.engine.fps_alvo}", True, COR_TEXTO)
        tela.blit(txt_fps, txt_fps.get_rect(center=(LARGURA // 2, 280)))

        for b in self.botoes_config:
            b.desenhar(tela, self.fonte_botoes)