import sys
import numpy as np
from scipy.optimize import newton
import pygame
import pygame.freetype


################################################################################
# Estos parametros se pueden cambiar para estudiar el problema
# ============================================================
#

MASS_RATIO = 0.01
# MASS_RATIO = 3e-6 # Este es el valor correcto para la Tierra

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
        self.vx = np.array([0., 0.])
        self.vy = np.array([0., -2 * np.pi])
        self.acceleration()

    def acceleration(self):
        d = np.sqrt((self.x[1] - self.x[0])**2 + (self.y[1] - self.y[0])**2)
        self.ax = -G * Msun * (self.x[1] - self.x[0]) / d**3
        self.ay = -G * Msun * (self.y[1] - self.y[0]) / d**3

    def step_forward(self, dt):
        # self.theta -= 2 * np.pi / 1. * dt
        # self.x[1] = self.R * np.cos(self.theta)
        # self.y[1] = self.R * np.sin(self.theta)

        self.x[1] = self.x[1] + self.vx[1] * dt + 0.5 * self.ax * dt**2
        self.y[1] = self.y[1] + self.vy[1] * dt + 0.5 * self.ay * dt**2

        old_ax = self.ax.copy()
        old_ay = self.ay.copy()
        self.acceleration()

        self.vx[1] = self.vx[1] + 0.5 * (self.ax + old_ax) * dt
        self.vy[1] = self.vy[1] + 0.5 * (self.ay + old_ay) * dt

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
        self.ax = (-G * Msun * (self.x - sun_earth.x[0]) / dist_to_sun**3
                   - G * Mp * (self.x - sun_earth.x[1]) / dist_to_earth**3)
        self.ay = (-G * Msun * (self.y - sun_earth.y[0]) / dist_to_sun**3
                   - G * Mp * (self.y - sun_earth.y[1]) / dist_to_earth**3)

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

    @classmethod
    def populating_lagrange_points(cls, color=PROBES_COLOR, size=5, width=1):
        R = 1.
        def l1(r, R=1., mass_ratio=MASS_RATIO):
            output = mass_ratio * (R-r)**2 + (R-r)**3/R**3 * r**2- r**2
            return output

        def l2(r, R=1., mass_ratio=MASS_RATIO):
            output = r**2 + mass_ratio * (R+r)**2 - (R+r)**3/R**3 * r**2
            return output

        def l3(r, R=1., mass_ratio=MASS_RATIO):
            output = (R+r)**2 + mass_ratio * r**2 - r**3/R**3*(R+r)**2
            return output

        l1_x = newton(l1, 0)
        l2_x = newton(l2, 0.5)
        l3_x = -newton(l3, 1)

        x = np.array([R-l1_x, R+l2_x, l3_x])
        y = np.zeros(3)
        vx = np.zeros(3)

        w = -2 * np.pi / 1.
        vy = np.ones(3) * w * x

        output = cls(x, y, vx, vy, color=color, size=size,
                     width=width)
        return output


###############################################################################
setup_and_start()
sun_earth = SunPlusEarth(mass_ratio=MASS_RATIO)
probes = MasslessProbes.with_random_positions(100, color=PROBES_COLOR,
                                              size=5, width=1)
lagrange = MasslessProbes.populating_lagrange_points(color=(125, 0, 0),
                                                     size=7, width=2)

objetos = [sun_earth, probes, lagrange]

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
        for objeto in objetos:
            objeto.step_forward(dt)

    for objeto in objetos:
        objeto.draw()

    pygame.display.flip()


pygame.quit()

