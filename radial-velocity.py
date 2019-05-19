import sys
import numpy as np
import pygame
import pygame.freetype



R = 150 # Distancia entre el Sol y el planeta en pixeles
        # La ventana tiene 600 pixeles en total
T = 5   # Periodo de la orbita en segundos reales


################################################################################
# Problem Constants
# =================
#

WIDTH, HEIGHT = (600, 600)
CX, CY = (300, 300)
BACKGROUND_COLOR = (0, 0, 0)
MAJOR_GRID_COLOR = (50, 50, 50)

BODIES = {'sun' : pygame.image.load('assets/images/sun51x51.png'),
          'jupyter' : pygame.image.load('assets/images/jupyter35x35.png'),
          }

GMsun = 4 * np.pi**2 * R**3 / T**2
################################################################################


def setup_and_start():
    global RUNNING
    global PAUSED
    global SCREEN
    global GAME_FONT
    global CLOCK

    pygame.init()
    GAME_FONT = pygame.freetype.Font(
                                "assets/fonts/Indie_Flower/IndieFlower.ttf", 24)
    CLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Velocidad Radial")
    RUNNING = True
    PAUSED = True


def toggle_pause():
    global PAUSED
    if PAUSED == True:
        PAUSED = False
    else:
        PAUSED = True

def draw_vertical_grid():
    global SCREEN
    for major_grid in range(0, WIDTH, 100):
        pygame.draw.line(SCREEN, MAJOR_GRID_COLOR, (major_grid, 0),
                         (major_grid, WIDTH), 3)
        for minor_grid in range(major_grid, major_grid+100, 20):
            pygame.draw.line(SCREEN, MAJOR_GRID_COLOR, (minor_grid, 0),
                             (minor_grid, WIDTH), 1)

def draw_horizontal_grid():
    global SCREEN
    for major_grid in range(0, HEIGHT, 100):
        pygame.draw.line(SCREEN, MAJOR_GRID_COLOR, (0, major_grid),
                         (HEIGHT, major_grid), 3)
        for minor_grid in range(major_grid, major_grid+100, 20):
            pygame.draw.line(SCREEN, MAJOR_GRID_COLOR, (0, minor_grid),
                             (HEIGHT, minor_grid), 1)

def draw_background():
    global SCREEN
    SCREEN.fill(BACKGROUND_COLOR)
    draw_vertical_grid()
    draw_horizontal_grid()



setup_and_start()

while RUNNING:
    dt = CLOCK.tick(26)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                toggle_pause()

            if event.key == pygame.K_q:
                RUNNING = False
                pygame.quit()
                sys.exit()

    draw_background()

    if PAUSED:
        GAME_FONT.render_to(SCREEN, (25, 570), "En pausa...", 
                            (255, 255, 255))

    pygame.display.flip()


pygame.quit()

