import random
import math
import pygame
from pygame.locals import *
import numpy as np
from operator import attrgetter

# Grid Size
CELL_COUNT = 30

# Colors
BLACK = (0, 0, 0)
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

    def draw(self, surface, cell_size, index):
        body = pygame.Surface((cell_size, cell_size))
        body.fill(RED)
        x = 0
        y = 0
        if index == 1:
            x = CELL_COUNT*cell_size
        elif index == 2:
            y = CELL_COUNT*cell_size
        elif index == 3:
            x = CELL_COUNT*cell_size
            y = CELL_COUNT*cell_size
        surface.blit(body, (self.x * cell_size + x, self.y * cell_size + y))

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

    def get_apple_distance(self):
        return math.sqrt(abs(pow(abs(self.x[0] - self.apple.x), 2) + pow(abs(self.y[0] - self.apple.y), 2)))

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
        distance = math.sqrt(abs(pow(abs(self.x[0] - self.apple.x), 2)
            + pow(abs(self.y[0] - self.apple.y), 2)))
        if self.direction == 0:
            x = self.apple.x - self.x[0]
            y = self.apple.y - self.y[0]
        if self.direction == 1:
            y = -self.apple.x - (-self.x[0])
            x = self.apple.y - self.y[0]
        elif self.direction == 2:
            x = -self.apple.x - (-self.x[0])
            y = -self.apple.y - (-self.y[0])
        elif self.direction == 3:
            y = self.apple.x - self.x[0]
            x = -self.apple.y - (-self.y[0])
        angle = math.atan2(y, x)
        return (distance / CELL_COUNT)*2 - 1, ((angle + math.pi) / (2 * math.pi))*2 - 1

    def observe_obstacle(self):
        head = (self.x[0], self.y[0])
        if self.direction == 0:
            front = CELL_COUNT - head[0]
            right = CELL_COUNT - head[1]
            left = head[1]
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
            right = head[0]
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
            front = head[0]
            right = head[1]
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
            front = head[1]
            right = CELL_COUNT - head[0]
            left = head[0]
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
        return (front / CELL_COUNT)*2 - 1, (right / CELL_COUNT)*2 - 1, (left / CELL_COUNT)*2 - 1

    def draw(self, surface, cell_size, index):
        body = pygame.Surface((cell_size, cell_size))
        body.fill(GREEN)
        x = 0
        y = 0
        if index == 1:
            x = CELL_COUNT*cell_size
        elif index == 2:
            y = CELL_COUNT*cell_size
        elif index == 3:
            x = CELL_COUNT*cell_size
            y = CELL_COUNT*cell_size
        for i in range(0, self.length):
            surface.blit(body, (self.x[i] * cell_size + x, self.y[i] * cell_size + y))

class Game:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Snake - The Genetic Algorithm')
        icon = pygame.image.load('resources/icon.png')
        pygame.display.set_icon(icon)

        self.cell_size = int(pygame.display.Info().current_w / 125)
        self.width = CELL_COUNT * self.cell_size * 2
        self.height = CELL_COUNT * self.cell_size * 2
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE)
        self.clock = pygame.time.Clock()

        self.screen.fill(BLACK)

        self.snakes = []
        self.stop = False

    def reset(self):
        self.stop = False
        for snake in self.snakes:
            snake = Snake(CELL_COUNT/2, CELL_COUNT/2, 5)

    def update(self, fps):
        if fps:
            self.clock.tick(fps)
        for snake in self.snakes:
            if not snake.dead:
                prev_distance = snake.get_apple_distance()
                snake.move()
                snake.score += 1
                if snake.hit_self() or snake.hit_border():
                    snake.score -= 100000
                    snake.dead = True
                else:
                    distance = snake.get_apple_distance()
                    if snake.eat_apple():
                        snake.score += 1000
                        snake.apple = Apple(snake)

    def render(self):
        self.screen.fill(BLACK)
        pygame.draw.line(self.screen, WHITE, (self.width / 2, 0), (self.width / 2, self.height), 5)
        pygame.draw.line(self.screen, WHITE, (0, self.height / 2), (self.width, self.height / 2), 5)
        snakes = sorted(self.snakes, key=attrgetter('score'))[::-1]
        for i in range(4):
            snakes[i].draw(self.screen, self.cell_size, i)
            snakes[i].apple.draw(self.screen, self.cell_size, i)
        pygame.display.flip()

    def play(self):
        while not self.stop:
            self.render()
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
            if action == 1:
                for i in range(4):
                    self.snakes[i].turn_right()
            elif action == 2:
                for i in range(4):
                    self.snakes[i].turn_left()
            self.update(5)
            front, right, left = self.snakes[0].observe_obstacle()
            print('%.2f, %.2f, %.2f' % (front, right, left))
            if self.snakes[0].dead:
                self.stop = True
        else:
            self.end()

    def end(self):
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    for _ in range(4):
        game.snakes.append(Snake(CELL_COUNT/2, CELL_COUNT/2, 25))
    game.play()
