import sys
import numpy as np
import pygame
import pygame.freetype


################################################################################
# Estos parametros se pueden cambiar para estudiar el problema
# ============================================================
#

R = 5.2 # Distancia entre el Sol y el planeta en unidades astronomicas
        # La ventana tiene 600 pixeles en total
MASS_RATIO = 0.001 # = M_planeta / M_estrella. La estrella más pequeña posible 
                   # tiene 0.08 veces la masa 
                   # del sol. La fusion nuclear no ocurre en objetos de masas 
                   # menores.

T = 5   # Periodo de la orbita en segundos reales

################################################################################
# Problem Constants
# =================
#

WIDTH, HEIGHT = (600, 600)
CX, CY = (300, 300)
BACKGROUND_COLOR = (0, 0, 0)
MAJOR_GRID_COLOR = (50, 50, 50)
PIXEL_SCALE = 200 / 5.2 # 5.2 u.a. son 200 pixeles

BODIES = {'sun' : pygame.image.load('assets/images/sun51x51.png'),
          'jupiter' : pygame.image.load('assets/images/jupiter35x35.png'),
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


class PlanetarySystem(object):
    """
    Un sistema planetario con una estrella y un planeta.
    Dada la distancia, las velocidades iniciales se calculan automáticamente de
    modo que las órbitas sean perfectamente circulares.
    """

    def __init__(self, a=5.2, mass_ratio=0.001):
        """
        a : [float] Eje semi mayor de la orbita en unidades astronomicas.
        mass_ratio : [float] la razon entre la masa del planeta y la de la
                     estrella.
        """
        self.a = a
        self.mass_ratio = mass_ratio
        self.set_initial_positions()
        self.set_initial_velocities()

    def set_initial_positions(self):
        self.y = np.array([0., 0.])
        x_sun = - self.a * self.mass_ratio / (1 + self.mass_ratio)
        x_planet = self.a / (1 + self.mass_ratio)
        self.x = np.array([x_sun, x_planet])

    def geom_transform(self):
        stamp_sizes = np.array([25, 17])
        x_positions = (self.x * PIXEL_SCALE + CX - stamp_sizes).astype(int)
        y_positions = (HEIGHT - CY - self.y * PIXEL_SCALE 
                       - stamp_sizes).astype(int)
        positions = np.stack((x_positions, y_positions), axis=1)
        return positions

    def draw(self):
        positions = self.geom_transform()
        SCREEN.blit(BODIES['sun'], positions[0])
        SCREEN.blit(BODIES['jupiter'], positions[1])
        


###############################################################################
setup_and_start()
ps = PlanetarySystem(a=5.2, mass_ratio=MASS_RATIO)


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
    ps.draw()

    if PAUSED:
        GAME_FONT.render_to(SCREEN, (25, 570), "En pausa...", 
                            (255, 255, 255))

    pygame.display.flip()


pygame.quit()

