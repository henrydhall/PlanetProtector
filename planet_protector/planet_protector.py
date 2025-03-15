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

if not pg.image.get_extended():
    raise SystemExit("Extended image module required.")

# Pygame setup
HEIGHT = 600
WIDTH = 700
DISPLAY_SURFACE = pg.display.set_mode((WIDTH, HEIGHT))
FPS = pg.time.Clock()
COLOR_BACKGROUD = (0, 0, 0)
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
        self._planet = planet

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
        """Update our x and y velocities, move the asteroid."""
        self.calculate_acceleration(self._planet)
        self.rect.move_ip(self.x_v, self.y_v)

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

    def reduce_mass(self, damage: int):
        self._mass -= damage
        if self._mass < ASTEROID_DESTROY_MASS:
            self.kill()


class Laser(pg.sprite.Sprite):
    """Laser sprite to reduce asteroid mass."""

    def __init__(self, power: int = 1, *groups):
        self._color = (255, 0, 0)
        self._damage = power
        pg.sprite.Sprite.__init__(self, *groups)

    def draw(self, planet: Planet, asteroid: Asteroid):
        """Draw the laser."""
        pg.draw.line(DISPLAY_SURFACE, (255, 0, 0), planet.rect.center, asteroid.rect.center, 3)

    def damage(self, asteroid: Asteroid):
        asteroid.reduce_mass(self._damage)


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
    

class Pane():
    """Abstract building display panes."""
    def __init__(self, x, y, width, height, color, border_radius):
        # TODO: figure out how to use this...
        self.rectangle = pg.Rect( x, y, width, height)
        self.color = color
        self.border_radius = border_radius
    
    def draw(self):
        """Display the bank."""
        pg.draw.rect(DISPLAY_SURFACE, pg.Color(255,255,255), pg.Rect(400,10,290,50), border_radius=15)


def main():
    """
    Main game loop.
    """

    # Create game groups
    asteroids = pg.sprite.Group()
    lasers = pg.sprite.Group()
    all = pg.sprite.RenderUpdates()

    # Create our entities
    bank = Bank(all)
    Laser(5, lasers, all)
    planet = Planet(all)

    laser1 = lasers.sprites()[0]
    # TODO: randomize asteroid mass
    # Use an exponential function

    while planet.alive():
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        all.update()

        planet.draw(DISPLAY_SURFACE)

        for asteroid in asteroids:
            asteroid.draw(DISPLAY_SURFACE)
            laser1.draw(planet, asteroid)  # TODO: update this to be...fancy
            laser1.damage(asteroid)

        if not int(random() * ASTEROID_ODDS):
            Asteroid(150, planet, asteroids, all)

        for asteroid in pg.sprite.spritecollide(planet, asteroids, 1):
            planet.kill()

        #dirty = all.draw(DISPLAY_SURFACE) # TODO: fix so we can just run this

        pg.display.update()

        DISPLAY_SURFACE.fill(COLOR_BACKGROUD)
        FPS.tick(FRAME_RATE)


if __name__ == '__main__':
    main()
    pg.quit()
