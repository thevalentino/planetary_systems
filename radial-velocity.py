import sys
import numpy as np
import pygame
import pygame.freetype


################################################################################
# Estos parametros se pueden cambiar para estudiar el problema
# ============================================================
#

R = 5.2 # Distancia entre el Sol y el planeta en unidades astronomicas
MASS_RATIO = 0.001 # = M_planeta / M_estrella. Por ejemplo:
                   # M_jupiter /  M_sol = 0.0009545942
                   # Notar que la estrella más pequeña posible tiene 0.08 veces
                   # la masa del sol. La fusion nuclear no ocurre en objetos de
                   # masas menores.

################################################################################
# Problem Constants
# =================
#

WIDTH, HEIGHT = (600, 600)
CX, CY = (300, 300)
BACKGROUND_COLOR = (0, 0, 0)
MAJOR_GRID_COLOR = (50, 50, 50)
PIXEL_SCALE = 200 / 5.2 # 5.2 u.a. son 200 pixeles
TIME_SCALE = 5 / 11.8622 # 5 segundos del programa son 11.8622 años terrestres

BODIES = {'sun' : pygame.image.load('assets/images/sun51x51.png'),
          'jupiter' : pygame.image.load('assets/images/jupiter35x35.png'),
          }

G = 39.47692640889762 # [ua^3 / Msun / yr^2]
Msun = 1.
Mp = Msun * MASS_RATIO

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

    def __init__(self, d=5.2, mass_ratio=0.001):
        """
        d : [float] Distancia entre el planeta y la estrella.
        mass_ratio : [float] la razon entre la masa del planeta y la de la
                     estrella.
        """
        self.d = d
        self.mass_ratio = mass_ratio
        self.set_initial_positions()
        self.set_initial_velocities()
        self.acceleration()

    def set_initial_positions(self):
        self.y = np.array([0., 0.])
        x_sun = -self.d * self.mass_ratio / (1 + self.mass_ratio)
        x_planet = self.d / (1 + self.mass_ratio)
        self.x = np.array([x_sun, x_planet])

    def set_initial_velocities(self):
        self.vx = np.array([0., 0.])
        self.vy = np.array([np.sqrt(-G * Mp * self.x[0] / self.d**2), 
                            -np.sqrt(G * Msun * self.x[1] / self.d**2)])

    def acceleration(self):
        dist = np.sqrt((self.x[1] - self.x[0])**2 + (self.y[1] - self.y[0])**2)
        fx = G * Msun * Mp * (self.x[1] - self.x[0]) / dist**3
        self.ax = np.array([1/Msun, -1/Mp]) * fx
        fy = G * Msun * Mp * (self.y[1] - self.y[0]) / dist**3
        self.ay = np.array([1/Msun, -1/Mp]) * fy

    def step_forward(self, dt):
        self.x = self.x + self.vx * dt + 0.5 * self.ax * dt**2
        self.y = self.y + self.vy * dt + 0.5 * self.ay * dt**2

        old_ax = self.ax.copy()
        old_ay = self.ay.copy()
        self.acceleration()

        self.vx = self.vx + 0.5 * (self.ax + old_ax) * dt
        self.vy = self.vy + 0.5 * (self.ay + old_ay) * dt

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
ps = PlanetarySystem(d=R, mass_ratio=MASS_RATIO)


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
    else:
        dt = dt / 1000. / TIME_SCALE
        ps.step_forward(dt)
        print("Vsun,x = {:-.5f} [km/s]".format(ps.vx[0]*4.740))

    ps.draw()

    pygame.display.flip()


pygame.quit()

