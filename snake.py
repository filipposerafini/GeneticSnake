import random
import math
import pygame
from pygame.locals import *
import numpy as np
from operator import attrgetter

# Debug
DEBUG_ENABLE = True

# Grid Size
CELL_COUNT = 40

# Colors
BLACK = (0, 0, 0)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

class Apple:

    def __init__(self, snake):
        retry = True
        while retry:
            retry = False
            self.x = random.randint(0, CELL_COUNT - 1)
            self.y = random.randint(0, CELL_COUNT - 1)
            for i in range(0, snake.length):
                if self.x == snake.x[i] and self.y == snake.y[i]:
                    retry = True

    def draw(self, surface, cell_size, color):
        body = pygame.Surface((cell_size, cell_size))
        body.fill(color)
        surface.blit(body, ((self.x + 1) * cell_size, (self.y + 1) * cell_size))

class Snake:

    def __init__(self, x, y, length):
        self.x = [x]
        self.y = [y]
        self.length = length
        self.direction = 0 if self.x[0] < CELL_COUNT / 2 else 2
        for i in range(1, self.length):
            self.x.append(self.x[0] - i if self.x[0] < CELL_COUNT / 2 else self.x[0] + i)
            self.y.append(self.y[0])
        self.apple = Apple(self)
        self.score = 0
        self.dead = False

    def turn_right(self):
        self.direction += 1
        if self.direction == 4:
            self.direction = 0

    def turn_left(self):
        self.direction -= 1
        if self.direction == -1:
            self.direction = 3

    def change_direction(self, x):
        if x == 1:
            self.turn_right()
        elif x == 2:
            self.turn_left()

    def move(self):
        for i in range(self.length - 1 , 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]
        if self.direction == 0:
            self.x[0] += 1
        elif self.direction == 1:
            self.y[0] += 1
        elif self.direction == 2:
            self.x[0] -= 1
        elif self.direction == 3:
            self.y[0] -= 1

    def collide(self, x, y):
        if self.x[0] == x and self.y[0] == y:
            return True
        else:
            return False

    def add_piece(self, count):
        for i in range(0, count):
            self.x.append(self.x[self.length - 1])
            self.y.append(self.y[self.length - 1])
            self.length += 1

    def eat_apple(self):
        if self.collide(self.apple.x, self.apple.y):
            self.add_piece(1)
            return True
        return False

    def hit_self(self):
        for i in range(1, self.length):
            if self.collide(self.x[i], self.y[i]):
                return True
        return False

    def hit_border(self):
        if self.x[0] < 0 or self.x[0] > CELL_COUNT - 1:
            return True
        elif self.y[0] < 0 or self.y[0] > CELL_COUNT - 1:
            return True
        else:
            return False

    def observe_apple(self):
        return Point(self, x=self.apple.x, y=self.apple.y)

    def observe_obstacle(self):
        head = (self.x[0], self.y[0])
        if self.direction == 0:
            front = CELL_COUNT - head[0]
            right = CELL_COUNT - head[1]
            left = head[1] + 1
            for i in range(1, self.length):
                distance = 0
                if self.y[i] == head[1]:
                    distance = self.x[i] - head[0]
                    if distance >= 0 and distance < front:
                        front = distance
                elif self.x[i] == head[0]:
                    distance = self.y[i] - head[1]
                    if distance > 0 and distance < right:
                        right = distance
                    elif distance < 0 and abs(distance) < left:
                        left = abs(distance)
        elif self.direction == 1:
            front = CELL_COUNT - head[1]
            right = head[0] + 1
            left = CELL_COUNT - head[0]
            for i in range(1, self.length):
                distance = 0
                if self.x[i] == head[0]:
                    distance = self.y[i] - head[1]
                    if distance >= 0 and distance < front:
                        front = distance
                elif self.y[i] == head[1]:
                    distance = self.x[i] - head[0]
                    if distance < 0 and abs(distance) < right:
                        right = abs(distance)
                    elif distance > 0 and distance < left:
                        left = distance
        elif self.direction == 2:
            front = head[0] + 1
            right = head[1] + 1
            left = CELL_COUNT - head[1]
            for i in range(1, self.length):
                distance = 0
                if self.y[i] == head[1]:
                    distance = head[0] - self.x[i]
                    if distance >= 0 and distance < front:
                        front = distance
                elif self.x[i] == head[0]:
                    distance = self.y[i] - head[1]
                    if distance < 0 and abs(distance) < right:
                        right = abs(distance)
                    elif distance > 0 and distance < left:
                        left = distance
        elif self.direction == 3:
            front = head[1] + 1
            right = CELL_COUNT - head[0]
            left = head[0] + 1
            for i in range(1, self.length):
                distance = 0
                if self.x[i] == head[0]:
                    distance = head[1] - self.y[i]
                    if distance >= 0 and distance < front:
                        front = distance
                elif self.y[i] == head[1]:
                    distance = self.x[i] - head[0]
                    if distance > 0 and distance < right:
                        right = distance
                    elif distance < 0 and abs(distance) < left:
                        left = abs(distance)
        if front < 0:
            front = 0
        return [Point(self, distance=front, direction=Point.FRONT),
                Point(self, distance=right, direction=Point.RIGHT),
                Point(self, distance=left, direction=Point.LEFT)]

    def draw(self, surface, cell_size, color, debug):
        body = pygame.Surface((cell_size, cell_size))
        body.fill(color)
        for i in range(0, self.length):
            surface.blit(body, ((self.x[i] + 1) * cell_size, (self.y[i] + 1) * cell_size))
        if debug:
            pts = pygame.Surface((cell_size, cell_size))
            pts.fill(MAGENTA)
            points = sorted(self.observe_obstacle(), key=lambda pt: pt.direction)
            for point in points:
                surface.blit(pts, tuple([(coord + 1) * cell_size for coord in point.to_absolute()]))

class Point:

    NAMED_DIRECTION = ["Front", "Right", "Back", "Left"]
    FRONT = 0
    RIGHT = 1
    BACK = 2
    LEFT = 3
    _c = 5 # round decimals for python noob maths

    def __init__(self, snake, **kwargs):
        self.snake = snake
        noAbs = 2
        noRel = 2
        for key in kwargs:
            if key == "x" or key == "y":
                setattr(self, key,  kwargs[key])
                noAbs -= 1
            if key == "distance" or key == "direction":
                setattr(self, key,  kwargs[key])
                noRel -= 1
        if not noRel: #immediately calculate abs
            self._absolute()
        elif noAbs:
            raise Exception("No absolute nor relative coordinate defined")

    def to_absolute(self):
        return (self.x, self.y)

    def to_relative(self):
        self._relative()
        return (self.distance, self.direction)

    def to_norm_relative(self):
        distance, direction = self.to_relative()
        return ((distance / CELL_COUNT)*2 - 1, (direction / 4)*2 - 1)

    def _relative(self):
        x_rel = self.x - self.snake.x[0]
        y_rel = self.y - self.snake.y[0]
        self.distance = round(math.sqrt(x_rel*x_rel + y_rel*y_rel), self._c)
        angle = math.atan2(y_rel, x_rel)
        if angle < 0:
            angle = 2*math.pi+angle
        self.direction = round(2 * angle / math.pi - self.snake.direction, self._c)
        if self.direction >= 4:
            self.direction -= 4
        if self.direction < 0:
            self.direction += 4

    def _absolute(self):
        angle = self.direction * math.pi / 2
        absolute_angle = angle + (math.pi / 2) * self.snake.direction
        self.x = round(self.snake.x[0] + self.distance * math.cos(absolute_angle), self._c)
        self.y = round(self.snake.y[0] + self.distance * math.sin(absolute_angle), self._c)

    def __str__(self):
        return str(self.to_relative())

class Game:

    def __init__(self, hidden=False):
        self.hidden = hidden

        if not hidden:
            pygame.init()
            pygame.display.set_caption('Snake - The Genetic Algorithm')
            icon = pygame.image.load('resources/icon.png')
            pygame.display.set_icon(icon)

            self.cell_size = int(pygame.display.Info().current_w / 100)
            self.width = CELL_COUNT * self.cell_size + 2 * self.cell_size
            self.height = CELL_COUNT * self.cell_size + 2 * self.cell_size
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE)
            self.clock = pygame.time.Clock()

            self.screen.fill(BLACK)

        self.snakes = []
        self.stop = False

    def best_snake(self):
        sorted_snakes = sorted(self.snakes, key=attrgetter('score'), reverse=True)
        for snake in sorted_snakes:
            if not snake.dead:
                return snake

    def update(self, fps):
        if fps:
            self.clock.tick(fps)
        for snake in self.snakes:
            if not snake.dead:
                snake.move()
                if snake.hit_self() or snake.hit_border():
                    snake.dead = True
                else:
                    if snake.eat_apple():
                        snake.score += 1
                        snake.apple = Apple(snake)

    def render(self, debug=False):
        if self.hidden:
            return
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, Rect(0, 0, self.width, self.height), self.cell_size*2)
        best = max(self.snakes, key=attrgetter('score'))
        for snake in self.snakes:
            if not snake.dead and snake is not best:
                snake.draw(self.screen, self.cell_size, DARK_GRAY, debug)
                snake.apple.draw(self.screen, self.cell_size, LIGHT_GRAY)
        if not best.dead:
            best.draw(self.screen, self.cell_size, GREEN, debug)
            best.apple.draw(self.screen, self.cell_size, RED)
        pygame.display.flip()

    def play(self):
        while not self.stop:
            self.render(debug=DEBUG_ENABLE)
            action = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.end()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_RIGHT:
                        action = 1
                        break
                    elif event.key == K_LEFT:
                        action = 2
                        break
                    elif event.key == K_ESCAPE:
                        self.end()
                        return
                else:
                    pass
            player = self.snakes[0]
            if action == 1:
                player.turn_right()
            elif action == 2:
                player.turn_left()
            self.update(5)

            pts = player.observe_obstacle()
            for pt in pts:
                pt.to_relative()
            pts = sorted(pts, key=lambda pt: pt.direction)
            apple = player.observe_apple().to_norm_relative()
            obstacles = [obstacle.to_norm_relative() for obstacle in player.observe_obstacle()]
            inputs = [apple[0], apple[1], obstacles[0][0], obstacles[1][0], obstacles[2][0]]
            print(inputs)
            if player.dead:
                self.stop = True
        else:
            self.end()

    def end(self):
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.snakes.append(Snake(CELL_COUNT/2, CELL_COUNT/2, 10))
    game.play()
