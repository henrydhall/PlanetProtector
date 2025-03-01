"""
Here is my game Planet Protector!

Just run this and you'll be good to go!
"""

import math
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
MAX_METEOR_SIZE = 10000 # Real world size
MAX_METEOR_DISPLAY = 30 # Display size

# Globals
FRAME_RATE = 15


class Planet(pg.sprite.Sprite):
    """Planet."""

    def __init__(self):
        self.image = pg.image.load('resources/planet.png')
        self.rect = self.image.get_rect()
        self.rect.center = (250, 250)

    def update(self):
        """Planet update method."""
        pass

    def draw(self, surface):
        """Draw the planet"""
        surface.blit(self.image, self.rect)


class Meteor(pg.sprite.Sprite):
    """Meteor class"""

    # TODO: I'd like to have a set speed, and just have that come towards the planet.
    # TODO: set random x/y away from planet to start.
    x_v = 0
    y_v = 0

    def __init__(self, mass):
        dimension = (MAX_METEOR_DISPLAY * mass/MAX_METEOR_SIZE) + 8
        self.image = pg.transform.scale(pg.image.load('resources/meteor_1.png'), (dimension,dimension))
        self.rect = self.image.get_rect()
        self.rect.center = (250, 50)
        self._mass = mass

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


class Laser(pg.sprite.Sprite):
    """Laser sprite to reduce meteor mass."""

    def __init__(self):
        self._color = (255, 0, 0)

    def draw(self, planet: Planet, meteor: Meteor):
        """Draw the laser."""
        pg.draw.line(DISPLAY_SURFACE, (255, 0, 0), planet.rect.center, meteor.rect.center, 3)


def main():
    """
    Main game loop.
    """
    planet = Planet()
    meteor1 = Meteor(50)
    laser1 = Laser()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        planet.draw(DISPLAY_SURFACE)
        meteor1.draw(DISPLAY_SURFACE)
        laser1.draw(planet, meteor1)

        meteor1.update(planet)
        pg.display.update()

        DISPLAY_SURFACE.fill(COLOR_BACKGROUD)
        FPS.tick(FRAME_RATE)


if __name__ == '__main__':
    main()
