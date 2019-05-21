import sys
import numpy as np
import pygame
import pygame.freetype


################################################################################
# Estos parametros se pueden cambiar para estudiar el problema
# ============================================================
#

# MASS_RATIO = 3e-6
MASS_RATIO = 0.5

################################################################################
# Problem Constants
# =================
#

np.random.seed(63546)
WIDTH, HEIGHT = (600, 600)
CX, CY = (300, 300)
BACKGROUND_COLOR = (0, 0, 0)
MAJOR_GRID_COLOR = (50, 50, 50)
PROBES_COLOR = (120, 120, 120)
PIXEL_SCALE = 200 / 1.0 # 1.0 u.a. son 200 pixeles
TIME_SCALE = 5 / 1.0    # 5 segundos del programa es 1 año terrestre

BODIES = {'sun' : pygame.image.load('assets/images/sun51x51.png'),
          'earth' : pygame.image.load('assets/images/earth21x21.png'),
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

def theta(x, y):
    theta = np.arctan(x / y)
    theta[x<0] += np.pi
    theta[(x>0)*(y<0)] += 2 * np.pi
    return theta

class SunPlusEarth(object):
    """
    """

    def __init__(self, mass_ratio=3e-6):
        self.R = 1.
        self.theta = 0
        self.x = np.array([0., 1.]) # [sun, earth]
        self.y = np.array([0., 0.])

    def step_forward(self, dt):
        self.theta -= 2 * np.pi / 1. * dt
        self.x[1] = self.R * np.cos(self.theta)
        self.y[1] = self.R * np.sin(self.theta)

    def geom_transform(self):
        stamp_sizes = np.array([25, 10])
        x_positions = (self.x * PIXEL_SCALE + CX - stamp_sizes).astype(int)
        y_positions = (HEIGHT - CY - self.y * PIXEL_SCALE 
                       - stamp_sizes).astype(int)
        positions = np.stack((x_positions, y_positions), axis=1)
        return positions

    def draw(self):
        positions = self.geom_transform()
        SCREEN.blit(BODIES['sun'], positions[0])
        SCREEN.blit(BODIES['earth'], positions[1])

class MasslessProbes(object):

    def __init__(self, x, y, vx, vy, color=(125, 125, 125), size=5, width=1):
        self.color = color
        self.size = size
        self.width = width
        self.x = x.copy()
        self.y = y.copy()
        self.vx = vx.copy()
        self.vy = vy.copy()
        self.acceleration()

    def initial_velocities(self):
        r = np.sqrt(self.x**2 + self.y**2)
        v = - 2 * np.pi / 1. * r
        angles = np.arctan2(self.y, self.x)
        self.vx = -v * np.sin(angles)
        self.vy = v * np.cos(angles)

    def acceleration(self):
        dist_to_sun = np.sqrt((self.x - sun_earth.x[0])**2 + 
                              (self.y - sun_earth.y[0])**2)
        dist_to_earth = np.sqrt((self.x - sun_earth.x[1])**2 + 
                                (self.y - sun_earth.y[1])**2)
        self.ax = (-G * Msun * (self.x - sun_earth.x[0]) / dist_to_sun
                   - G * Mp * (self.x - sun_earth.x[1]) / dist_to_earth)
        self.ay = (-G * Msun * (self.y - sun_earth.y[0]) / dist_to_sun
                   - G * Mp * (self.y - sun_earth.y[1]) / dist_to_earth)

    def step_forward(self, dt):
        self.x = self.x + self.vx * dt + 0.5 * self.ax * dt**2
        self.y = self.y + self.vy * dt + 0.5 * self.ay * dt**2

        old_ax = self.ax.copy()
        old_ay = self.ay.copy()
        self.acceleration()

        self.vx = self.vx + 0.5 * (self.ax + old_ax) * dt
        self.vy = self.vy + 0.5 * (self.ay + old_ay) * dt

    def geom_transform(self):
        x_positions = (self.x * PIXEL_SCALE + CX).astype(int)
        y_positions = (HEIGHT - CY - self.y * PIXEL_SCALE).astype(int)
        positions = np.stack((x_positions, y_positions), axis=1)
        return positions

    def draw(self):
        positions = self.geom_transform()
        for position in positions:
            pygame.draw.circle(SCREEN, self.color, position, self.size,
                               self.width) 

    @classmethod
    def with_random_positions(cls, N, color=PROBES_COLOR, size=5, width=1):
        counter = 0
        x = np.zeros(N)
        y = np.zeros(N)
        while counter < N:
            x_test = np.random.uniform(low=-215, high=215, size=1)
            y_test = np.random.uniform(low=-215, high=215, size=1)
            r = np.sqrt(x_test**2 + y_test**2)
            if r>215 or r<20:
                continue
            x[counter] = x_test
            y[counter] = y_test
            counter += 1
        x /= PIXEL_SCALE
        y /= PIXEL_SCALE
        output = cls(x, y, np.zeros(N), np.zeros(N), color=color, size=size,
                     width=width)
        output.initial_velocities()
        return output

###############################################################################
setup_and_start()
sun_earth = SunPlusEarth(mass_ratio=MASS_RATIO)
probes = MasslessProbes.with_random_positions(100, color=PROBES_COLOR,
                                              size=5, width=1)

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
        sun_earth.step_forward(dt)
        probes.step_forward(dt)

    sun_earth.draw()
    probes.draw()

    pygame.display.flip()


pygame.quit()

