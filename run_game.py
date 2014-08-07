from twisted.internet import reactor
from twisted.internet import task
from twisted.internet import defer
from twisted.internet import threads
from pygame.locals import *
import pygame
import threading
import functools
import collections

DISPLAY_SIZE = (600, 500)
FPS = 1 / 60.0
BAT_SPEED = 50.0


class txPong(object):
    """
    silly pong clone using pygame and twisted
    """

    def __init__(self):
        self.group = None
        self.surface = None
        self.bats = None
        self.pressed = None
        self.surface_lock = threading.Lock()

    def setup_display(self, result=None):
        def func0(result=None):
            self.surface = pygame.display.set_mode(DISPLAY_SIZE)
            self.surface.fill((0, 0, 0))

        def func1(result=None):
            return threads.deferToThread(self.handle_display)

        def func2(result=None):
            c = task.LoopingCall(func1)
            c.start(FPS, now=False)

        d = defer.execute(func0)
        d.addCallback(func2)
        return d

    def listen_events(self, result=None):
        def func():
            d = defer.execute(pygame.event.get)
            d.addCallback(self.handle_events)
            return d

        self.pressed = dict()
        c = task.LoopingCall(func)
        c.start(0)
        return c

    def setup_game(self, result=None):
        def make_bat(rect):
            bat = pygame.sprite.Sprite()
            bat.rect = pygame.Rect(rect)
            bat.image = pygame.Surface(bat.rect.size)
            bat.image.fill((255, 255, 255))
            bat.position = Position(0, 0)
            return bat

        rect = (0, 0, 30, 120)
        bat1 = make_bat(rect)
        bat2 = make_bat(rect)

        rect = (0, 0, 30, 30)
        ball = make_bat(rect)

        self.sprites = [bat1, bat2, ball]
        self.group = pygame.sprite.Group()
        self.group.add(*self.sprites)

    def handle_events(self, events):
        for event in events:
            if event.type == KEYDOWN:
                self.pressed[event.key] = True

            elif event.type == KEYUP:
                try:
                    del self.pressed[event.key]
                except KeyError:
                    pass

        self.handle_time(1/60.)

    def handle_time(self, td):
        get = self.pressed.get
        if get(K_UP):
            self.sprites[0].position.y -= BAT_SPEED * td / 100
        elif get(K_DOWN):
            self.sprites[0].position.y += BAT_SPEED * td / 100

        self.sprites[0].rect.topleft = self.sprites[0].position

    def handle_display(self, result=None):
        with self.surface_lock:
            self.group.draw(self.surface)
            pygame.display.flip()

    def run(self):
        pygame.init()

        d = self.setup_display()
        d = d.addCallback(self.setup_game)
        d = d.addCallback(self.listen_events)

        reactor.run()


if __name__ == '__main__':
    txPong().run()

