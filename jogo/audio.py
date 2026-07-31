# audio.py
import pygame
import array
import math
from config import VOLUME_PADRAO

class GerenciadorAudio:
    def __init__(self):
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            except pygame.error:
                pygame.mixer.init()

        self.volume = VOLUME_PADRAO
        self.som_comida = self._gerar_som_beep(frequencia_inicio=500, frequencia_fim=900, duracao=0.08)
        self.som_game_over = self._gerar_som_beep(frequencia_inicio=300, frequencia_fim=100, duracao=0.4)
        self.definir_volume(self.volume)

    def _gerar_som_beep(self, frequencia_inicio, frequencia_fim, duracao):
        sample_rate = 44100
        num_samples = int(sample_rate * duracao)
        buffer = array.array('h')

        for i in range(num_samples):
            t = i / sample_rate
            freq_atual = frequencia_inicio + (frequencia_fim - frequencia_inicio) * (i / num_samples)
            amplitude = 16000
            if i < 500:
                amplitude *= (i / 500)
            elif i > num_samples - 500:
                amplitude *= ((num_samples - i) / 500)

            val = int(amplitude * math.sin(2 * math.pi * freq_atual * t))
            buffer.append(val)

        return pygame.mixer.Sound(buffer=buffer.tobytes())

    def definir_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        if self.som_comida:
            self.som_comida.set_volume(self.volume)
        if self.som_game_over:
            self.som_game_over.set_volume(self.volume)

    def tocar_comida(self):
        if self.som_comida:
            self.som_comida.play()

    def tocar_game_over(self):
        if self.som_game_over:
            self.som_game_over.play()