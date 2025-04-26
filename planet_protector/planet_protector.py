"""
Here is my game Planet Protector!

Just run this and you'll be good to go!
"""

import math
import os
from random import random
import sys

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import pygame as pg

pg.init()


if not pg.image.get_extended():
    raise SystemExit("Extended image module required.")

# Pygame setup
HEIGHT = 600
WIDTH = 700
DISPLAY_SURFACE = pg.display.set_mode((WIDTH, HEIGHT))
FPS = pg.time.Clock()
ACCELERATION = 0.1
MAX_ASTEROID_SIZE = 10000  # Real world size
MAX_ASTEROID_DISPLAY = 30  # Display size
PLANET_CENTER_X = 200
PLANET_CENTER_Y = 200
FIRING_RADIUS = 190

# Globals
FRAME_RATE = 15
ASTEROID_ODDS = 50
ASTEROID_DESTROY_MASS = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Planet(pg.sprite.Sprite):
    """Planet."""

    def __init__(self, *groups):
        self.image = pg.image.load('resources/planet.png')
        pg.sprite.Sprite.__init__(self, *groups)
        self.rect = self.image.get_rect()
        self.rect.center = (PLANET_CENTER_X, PLANET_CENTER_Y)

    def draw(self, surface):
        """Draw the planet"""
        surface.blit(self.image, self.rect)


class Asteroid(pg.sprite.Sprite):
    """Asteroid class"""

    # TODO: I'd like to have a set speed, and just have that come towards the planet.
    # TODO: look into why we have a very slight wobble in the trajectory towards the planet.
    # the wobble started with having random start and changing the location of the planet
    x_v = 0
    y_v = 0

    def __init__(self, mass: int, planet: Planet, *groups):
        dimension = (MAX_ASTEROID_DISPLAY * mass / MAX_ASTEROID_SIZE) + 8
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = pg.transform.scale(pg.image.load('resources/asteroid_1.png'), (dimension, dimension))
        self.rect = self.image.get_rect()
        self.rect.center = self.random_start()
        self._mass = mass
        self.start_mass = mass
        self._planet = planet
        self.font = pg.font.SysFont('Arial', 25)

    def random_start(self) -> tuple[int, int]:
        """Generate a random start location on the perimeters of our firing area."""
        angle = random() * 2 * math.pi
        x = math.cos(angle) * FIRING_RADIUS + PLANET_CENTER_X
        y = math.sin(angle) * FIRING_RADIUS + PLANET_CENTER_Y
        return x, y

    def draw(self, surface: pg.display):
        """Draw the asteroid"""
        surface.blit(self.image, self.rect)

    def update(self):
        """Update our x and y velocities, move the asteroid, draw current mass."""
        self.calculate_acceleration(self._planet)
        self.rect.move_ip(self.x_v, self.y_v)
        DISPLAY_SURFACE.blit(self.font.render(str(self._mass), True, WHITE), (self.rect.x + 10, self.rect.y))

    def calculate_acceleration(self, planet: Planet) -> tuple[float, float]:
        """Calculate the component accelerations."""
        if self.rect.centery == planet.rect.centery:
            if self.rect.centerx < planet.rect.centerx:
                angle = math.pi / 2
            else:
                angle = -math.pi / 2
        else:
            angle = math.atan((self.rect.centerx - planet.rect.centerx) / (self.rect.centery - planet.rect.centery))
        opposite = abs(math.sin(angle)) * ACCELERATION
        adjacent = abs(math.cos(angle)) * ACCELERATION
        if self.rect.centerx > planet.rect.centerx:
            self.x_v -= opposite
        else:
            self.x_v += opposite

        if self.rect.centery > planet.rect.centerx:
            self.y_v -= adjacent
        else:
            self.y_v += adjacent

    def reduce_mass(self, damage: int) -> bool:
        """Reduce the mass of the asteroid. Return true if it is destroyed."""
        self._mass -= damage
        if self._mass < ASTEROID_DESTROY_MASS:
            self.kill()
            return True
        return False


class Bank(pg.sprite.Sprite):
    """Class for tracking player's money."""

    def __init__(self, start_amount: int = 200, *groups):
        super().__init__(*groups)
        self._bank = start_amount

    def add_bank(self, amount: int):
        """Add to the bank."""
        self._bank += amount

    def sub_bank(self, amount: int) -> bool:
        """Subtract from bank if allowed."""
        if amount <= self._bank:
            self._bank -= amount
            return True
        return False


class Laser(pg.sprite.Sprite):
    """Laser sprite to reduce asteroid mass."""

    def __init__(self, bank: Bank, power: int = 1, *groups):
        self._color = (255, 0, 0)
        self._damage = power
        pg.sprite.Sprite.__init__(self, *groups)
        self._bank = bank
        self.image = pg.image.load('resources/laser.png')
        self.rect = self.image.get_rect()
        self.rect.center = (PLANET_CENTER_X, PLANET_CENTER_Y)
        self.upgrade_cost = 10

    def draw(self, planet: Planet, asteroid: Asteroid):
        """Draw the laser."""
        pg.draw.line(DISPLAY_SURFACE, (255, 0, 0), planet.rect.center, asteroid.rect.center, 3)

    def update(self, *args, **kwargs):
        """Update Laser, display stats in pane."""

    def damage(self, asteroid: Asteroid):
        """Damage an asteroid. Add to the bank if it is destroyed."""
        if asteroid.reduce_mass(self._damage):
            self._bank.add_bank(asteroid.start_mass)

    def upgrade(self):
        """Upgrade the laser."""
        self.upgrade_cost = self.upgrade_cost * 2
        self._damage += 1


class Pane:
    """Abstract building display panes."""

    def __init__(self, x, y, width, height, color: pg.Color, border_radius, font_size=25):
        self.rect = pg.Rect(x, y, width, height)
        self.color = color
        self.border_radius = border_radius
        self.font = pg.font.SysFont('Arial', font_size)

    def draw(self, text):
        """Display the Pane."""
        pg.draw.rect(DISPLAY_SURFACE, self.color, self.rect, border_radius=self.border_radius)
        DISPLAY_SURFACE.blit(self.font.render(text, True, BLACK), (self.rect.x + 20, self.rect.y + 7))


class InfoPane(Pane):
    """Panes to display things like bank and weapon info.

    bank_pane = Pane(400, 10, 290, 50, pg.Color(WHITE), 15)
    """

    def __init__(self, position: int, font_size=25):
        super().__init__(400, 10 + position * 50, 290, 44, pg.Color(WHITE), 15, font_size)


class Click(pg.sprite.Sprite):
    """Click entity to interact with the game."""

    def __init__(self, click_info, *groups):
        super().__init__(*groups)
        self.image = pg.transform.scale(pg.image.load('resources/laser.png'), (5, 5))
        self.rect = self.image.get_rect()
        self.rect.center = click_info['pos']

    def draw(self, surface):
        surface.blit(self.image, self.rect)


def main():
    """
    Main game loop.
    """

    # Create game groups
    asteroids = pg.sprite.Group()
    lasers = pg.sprite.Group()
    clicks = pg.sprite.Group()
    all = pg.sprite.RenderUpdates()

    # Create our entities
    bank_pane = InfoPane(0)
    laser_pane = InfoPane(1, 15)

    bank = Bank(200)
    planet = Planet(all)
    Laser(bank, 3, lasers, all)

    laser1: Laser = lasers.sprites()[0]
    # TODO: randomize asteroid mass
    # Use an exponential function

    while planet.alive():
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                Click(event.dict, clicks, all)
                for click in pg.sprite.spritecollide(laser_pane, clicks, True):
                    if bank.sub_bank(laser1.upgrade_cost):
                        laser1.upgrade()

        all.update()

        dirty = all.draw(DISPLAY_SURFACE)

        bank_pane.draw('$' + str(bank._bank))
        laser_pane.draw('Laser 1  Damage: ' + str(laser1._damage) + ' Cost to upgrade:' + str(laser1.upgrade_cost))

        for click in clicks:
            click.kill()

        for asteroid in asteroids:
            laser1.draw(planet, asteroid)
            laser1.damage(asteroid)

        if not int(random() * ASTEROID_ODDS):
            Asteroid(150, planet, asteroids, all)

        for asteroid in pg.sprite.spritecollide(planet, asteroids, True):
            planet.kill()

        pg.display.update()

        DISPLAY_SURFACE.fill(BLACK)
        FPS.tick(FRAME_RATE)


if __name__ == '__main__':
    main()
    pg.quit()
