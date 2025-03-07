"""
Here is my game Planet Protector!

Just run this and you'll be good to go!
"""

import math
from random import random
import sys

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
MAX_METEOR_SIZE = 10000  # Real world size
MAX_METEOR_DISPLAY = 30  # Display size
PLANET_CENTER_X = 200
PLANET_CENTER_Y = 200
FIRING_RADIUS = 175

# Globals
FRAME_RATE = 15
METEOR_ODDS = 50


class Planet(pg.sprite.Sprite):
    """Planet."""

    def __init__(self, *groups):
        self.image = pg.image.load('resources/planet.png')
        # TODO: do group stuff with this one
        # pg.sprite.Sprite.__init__(self, *groups)
        self.rect = self.image.get_rect()
        self.rect.center = (PLANET_CENTER_X, PLANET_CENTER_Y)

    def update(self):
        """Planet update method."""
        pass

    def draw(self, surface):
        """Draw the planet"""
        surface.blit(self.image, self.rect)


class Meteor(pg.sprite.Sprite):
    """Meteor class"""

    # TODO: I'd like to have a set speed, and just have that come towards the planet.
    # TODO: look into why we have a very slight wobble in the trajectory towards the planet.
    # the wobble started with having random start and changing the location of the planet
    x_v = 0
    y_v = 0

    def __init__(self, mass, *groups):
        dimension = (MAX_METEOR_DISPLAY * mass / MAX_METEOR_SIZE) + 8
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = pg.transform.scale(pg.image.load('resources/meteor_1.png'), (dimension, dimension))
        self.rect = self.image.get_rect()
        self.rect.center = self.random_start()
        self._mass = mass

    def random_start(self) -> tuple[int, int]:
        """Generate a random start location on the perimeters of our firing area."""
        angle = random() * 2 * math.pi
        x = math.cos(angle) * FIRING_RADIUS + PLANET_CENTER_X
        y = math.sin(angle) * FIRING_RADIUS + PLANET_CENTER_Y
        return x, y

    def draw(self, surface: pg.display):
        """Draw the meteor"""
        surface.blit(self.image, self.rect)

    def update(self, planet: Planet):
        """Update our x and y velocities, move the meteor."""
        self.calculate_acceleration(planet)
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
        if self._mass < 0:
            self.kill()


class Laser(pg.sprite.Sprite):
    """Laser sprite to reduce meteor mass."""

    def __init__(self, power: int = 1):
        # TODO: implement group stuff
        self._color = (255, 0, 0)
        self._damage = power

    def draw(self, planet: Planet, meteor: Meteor):
        """Draw the laser."""
        pg.draw.line(DISPLAY_SURFACE, (255, 0, 0), planet.rect.center, meteor.rect.center, 3)

    def damage(self, meteor: Meteor):
        meteor.reduce_mass(self._damage)


def main():
    """
    Main game loop.
    """

    planet = Planet()
    laser1 = Laser()

    # Create game groups
    meteors = pg.sprite.Group()
    # TODO: create other game groups
    # TODO: randomize meteor mass
    # TODO: check for meteor/planet collision

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        if not meteors:  # TODO: change this to adding meteors at random
            Meteor(50, meteors)
        planet.draw(DISPLAY_SURFACE)
        for meteor in meteors:
            meteor.draw(DISPLAY_SURFACE)
            meteor.update(planet)
            laser1.draw(planet, meteor)  # TODO: update this to be...fancy
            laser1.damage(meteor)

        if not int(random() * METEOR_ODDS):
            Meteor(100)

        pg.display.update()

        DISPLAY_SURFACE.fill(COLOR_BACKGROUD)
        FPS.tick(FRAME_RATE)


if __name__ == '__main__':
    main()
