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
WIDTH = 600
DISPLAY_SURFACE = pg.display.set_mode((HEIGHT,WIDTH))
FPS = pg.time.Clock()
COLOR_BACKGROUD = (0, 0, 0)
ACCELERATION = .5

# Globals
FRAME_RATE = 4


class Planet(pg.sprite.Sprite):
    """Planet."""
    def __init__(self):
        self.image = pg.image.load('resources/planet.png')
        self.rect = self.image.get_rect()
        self.rect.center = (250,250)

    def update(self):
        """Planet update method."""
        pass

    def draw(self, surface):
        """Draw the planet"""
        surface.blit(self.image, self.rect)


class Meteor(pg.sprite.Sprite):
    """Meteor class"""
    x_v = 10
    y_v = 0

    def __init__(self):
        self.image = pg.image.load('resources/meteor_1.png')
        self.rect = self.image.get_rect()
        self.rect.center = (251,50)

    def draw(self, surface):
        """Draw the meteor"""
        surface.blit(self.image, self.rect)

    def update(self, planet: Planet):
        """Update our x and y velocities, move the meteor."""
        #self.x_v, self.y_v = self.calculate_acceleration(planet)
        self.calculate_acceleration(planet)
        self.rect.move_ip(self.x_v,self.y_v)

    def calculate_acceleration(self, planet: Planet) -> tuple[float, float]:
        """Calculate the component accelerations.
        TODO: fix the division by zero error when x or y matches the planet's.
        """
        angle = math.atan( (self.rect.centerx - planet.rect.centerx) / (self.rect.centery-planet.rect.centery) )
        opposite = abs(math.sin(angle)) * ACCELERATION
        adjacent = abs(math.cos(angle)) * ACCELERATION
        print(opposite, adjacent, self.x_v, self.y_v, self.rect.x, self.rect.y)
        if self.rect.centerx > planet.rect.centerx:
            self.x_v -= opposite
        else:
            self.x_v += opposite

        if self.rect.centery > planet.rect.centerx:
            self.y_v -= adjacent
        else:
            self.y_v += adjacent

def main():
    """
    Main game loop.
    """
    planet = Planet()
    meteor1 = Meteor()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        planet.draw(DISPLAY_SURFACE)
        meteor1.draw(DISPLAY_SURFACE)

        meteor1.update(planet)
        pg.display.update()

        DISPLAY_SURFACE.fill(COLOR_BACKGROUD)
        FPS.tick(FRAME_RATE)

if __name__ == '__main__':
    main()
