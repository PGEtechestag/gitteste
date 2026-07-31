import pygame
import random

# Inicializa o Pygame
pygame.init()

# Definição de Cores
PRETO = (0, 0, 0)
CINZA_ESCURO = (30, 30, 30)
AZUL_CLARO = (0, 255, 255)
BRANCO = (255, 255, 255)
VERMELHO_MACA = (213, 50, 80)
AMARELO_PARTICULA = (255, 200, 0)

# Paleta de Cores da Cobra (Arco-íris)
CORES_COBRA = [
    (255, 0, 0), (255, 127, 0), (255, 255, 0), 
    (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
]

LARGURA = 300
ALTURA = 300
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('Jogo da Cobrinha com Partículas')

clock = pygame.time.Clock()
tamanho_bloco = 20

fonte_estilo = pygame.font.SysFont(None, 35)
fonte_placar = pygame.font.SysFont(None, 20)

def desenhar_fundo_xadrez():
    for linha in range(0, ALTURA, tamanho_bloco):
        for coluna in range(0, LARGURA, tamanho_bloco):
            if ((linha // tamanho_bloco) + (coluna // tamanho_bloco)) % 2 == 0:
                cor = PRETO
            else:
                cor = CINZA_ESCURO
            pygame.draw.rect(tela, cor, [coluna, linha, tamanho_bloco, tamanho_bloco])

def mostrar_placar(pontos, velocidade_atual):
    texto_pontos = fonte_placar.render(f"Pontos: {pontos} | Vel: {velocidade_atual}", True, BRANCO)
    tela.blit(texto_pontos, [5, 5])

def desenhar_cobra(tamanho_bloco, lista_cobra, x_mudanca, y_mudanca, comida_x, comida_y):
    for i, pedaco in enumerate(lista_cobra):
        cor = CORES_COBRA[i % len(CORES_COBRA)]
        pygame.draw.rect(tela, cor, [pedaco[0], pedaco[1], tamanho_bloco, tamanho_bloco])
        
        # Desenha os olhos na cabeça
        if i == len(lista_cobra) - 1:
            cx, cy = pedaco[0], pedaco[1]
            
            if x_mudanca > 0:
                olho1, olho2 = (cx + 15, cy + 5), (cx + 15, cy + 15)
            elif x_mudanca < 0:
                olho1, olho2 = (cx + 5, cy + 5), (cx + 5, cy + 15)
            elif y_mudanca < 0:
                olho1, olho2 = (cx + 5, cy + 5), (cx + 15, cy + 5)
            else:
                olho1, olho2 = (cx + 5, cy + 15), (cx + 15, cy + 15)
            
            p1_x, p1_y = olho1[0], olho1[1]
            p2_x, p2_y = olho2[0], olho2[1]
            
            if comida_x > cx: p1_x += 1; p2_x += 1
            elif comida_x < cx: p1_x -= 1; p2_x -= 1
            if comida_y > cy: p1_y += 1; p2_y += 1
            elif comida_y < cy: p1_y -= 1; p2_y -= 1

            pygame.draw.circle(tela, BRANCO, olho1, 4)
            pygame.draw.circle(tela, BRANCO, olho2, 4)
            pygame.draw.circle(tela, PRETO, (p1_x, p1_y), 2)
            pygame.draw.circle(tela, PRETO, (p2_x, p2_y), 2)

def jogoPrincipal():
    jogo_fechado = False
    fim_de_jogo = False

    # CORREÇÃO: Força a cobra a nascer em um múltiplo exato de 20 (Alinhada ao xadrez)
    x = round((LARGURA / 2) / tamanho_bloco) * tamanho_bloco
    y = round((ALTURA / 2) / tamanho_bloco) * tamanho_bloco

    x_mudanca = 0
    y_mudanca = 0

    lista_cobra = []
    comprimento_cobra = 1
    velocidade = 6
    
    particulas = []

    # CORREÇÃO: Nova fórmula mais limpa para garantir que a maçã sempre caia perfeitamente no xadrez
    comida_x = random.randrange(0, LARGURA, tamanho_bloco)
    comida_y = random.randrange(0, ALTURA, tamanho_bloco)

    while not jogo_fechado:

        while fim_de_jogo:
            tela.fill(PRETO)
            texto_perdeu = fonte_estilo.render("VOCÊ PERDEU!", True, BRANCO)
            texto_teclas = fonte_placar.render("Aperte C (Jogar) ou Q (Sair)", True, BRANCO)
            
            rect_perdeu = texto_perdeu.get_rect(center=(LARGURA / 2, ALTURA / 3))
            rect_teclas = texto_teclas.get_rect(center=(LARGURA / 2, ALTURA / 2))
            
            tela.blit(texto_perdeu, rect_perdeu)
            tela.blit(texto_teclas, rect_teclas)
            pygame.display.update()

            for evento in pygame.event.get():
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_q:
                        jogo_fechado = True
                        fim_de_jogo = False
                    if evento.key == pygame.K_c:
                        jogoPrincipal()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                jogo_fechado = True
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT and x_mudanca == 0:
                    x_mudanca = -tamanho_bloco; y_mudanca = 0
                elif evento.key == pygame.K_RIGHT and x_mudanca == 0:
                    x_mudanca = tamanho_bloco; y_mudanca = 0
                elif evento.key == pygame.K_UP and y_mudanca == 0:
                    y_mudanca = -tamanho_bloco; x_mudanca = 0
                elif evento.key == pygame.K_DOWN and y_mudanca == 0:
                    y_mudanca = tamanho_bloco; x_mudanca = 0

        if x >= LARGURA or x < 0 or y >= ALTURA or y < 0:
            fim_de_jogo = True

        x += x_mudanca
        y += y_mudanca
        
        desenhar_fundo_xadrez()
        
        # CORREÇÃO: Borda reduzida para 1 pixel para não tampar o desenho do chão
        pygame.draw.rect(tela, AZUL_CLARO, [0, 0, LARGURA, ALTURA], 1)
        
        centro_maca = (int(comida_x + tamanho_bloco/2), int(comida_y + tamanho_bloco/2))
        pygame.draw.circle(tela, VERMELHO_MACA, centro_maca, int(tamanho_bloco/2))
        
        for p in particulas:
            p[0][0] += p[1][0] 
            p[0][1] += p[1][1] 
            p[2] -= 0.5        
            if p[2] > 0: 
                pygame.draw.circle(tela, p[3], (int(p[0][0]), int(p[0][1])), int(p[2]))
                
        particulas = [p for p in particulas if p[2] > 0]

        cabeca_cobra = []
        cabeca_cobra.append(x)
        cabeca_cobra.append(y)
        lista_cobra.append(cabeca_cobra)
        
        if len(lista_cobra) > comprimento_cobra:
            del lista_cobra[0]

        for bloco in lista_cobra[:-1]:
            if bloco == cabeca_cobra:
                fim_de_jogo = True

        desenhar_cobra(tamanho_bloco, lista_cobra, x_mudanca, y_mudanca, comida_x, comida_y)
        mostrar_placar(comprimento_cobra - 1, velocidade)
        pygame.display.update()

        if x == comida_x and y == comida_y:
            for _ in range(15): 
                vel_x = random.uniform(-4, 4) 
                vel_y = random.uniform(-4, 4)
                raio = random.uniform(2, 6)   
                cor = random.choice([VERMELHO_MACA, AMARELO_PARTICULA, BRANCO])
                particulas.append([[comida_x + 10, comida_y + 10], [vel_x, vel_y], raio, cor])

            # CORREÇÃO: Sorteia a nova comida cravada no xadrez
            comida_x = random.randrange(0, LARGURA, tamanho_bloco)
            comida_y = random.randrange(0, ALTURA, tamanho_bloco)
            comprimento_cobra += 1
            
            if (comprimento_cobra - 1) % 10 == 0:
                velocidade += 2 

        clock.tick(velocidade)

    pygame.quit()
    quit()

jogoPrincipal()