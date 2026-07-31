# particulas.py
import pygame
import random

class ParticulaCartoon:
    def __init__(self, x, y, cor):
        self.x = x
        self.y = y
        self.cor = cor
        self.vx = random.uniform(-120, 120)
        self.vy = random.uniform(-120, 120)
        self.tamanho = random.randint(4, 8)
        self.vida = 0.3  # Segundos de duração

    def atualizar(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vida -= dt
        self.tamanho = max(0, self.tamanho - dt * 15)

    def desenhar(self, tela):
        if self.vida > 0 and self.tamanho > 1:
            # Partícula no estilo bloco de quadrinhos com contorno
            rect = pygame.Rect(self.x, self.y, self.tamanho, self.tamanho)
            pygame.draw.rect(tela, (10, 10, 12), rect.inflate(2, 2))
            pygame.draw.rect(tela, self.cor, rect)

class SistemaParticulas:
    def __init__(self):
        self.particulas = []

    def emitir(self, x, y, cor, quantidade=12):
        for _ in range(quantidade):
            self.particulas.append(ParticulaCartoon(x, y, cor))

    def atualizar_e_desenhar(self, dt, tela):
        for p in self.particulas[:]:
            p.atualizar(dt)
            if p.vida <= 0:
                self.particulas.remove(p)
            else:
                p.desenhar(tela)