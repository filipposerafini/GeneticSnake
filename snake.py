import random
import pygame
import nn
import sys
import numpy as np
from pygame.locals import *
from operator import attrgetter

# GRID SIZE
CELL_COUNT_X = 70
CELL_COUNT_Y = 40

# SETTINGS
SPECIAL_FRAMES = 3
APPLE_COOLDOWN = 120
SNAKE_COOLDOWN = 40
WAIT_STEPS = 500
MAX_PLAYERS = 2
GUI_SCALE = 120

# COLORS
BLACK = (16, 16, 16)
DARK_GRAY = (24, 24, 24)
LIGHT_GRAY = (32, 32, 32)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 100, 0)
GREEN = (0, 255, 0)
BLUE = (0, 50, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PINK = (255, 128, 255)
PURPLE = (125, 0, 255)

SOUNDS = {}

def init_sounds():
    SOUNDS['Apple'] = pygame.mixer.Sound('resources/apple.wav')
    SOUNDS['Golden'] = pygame.mixer.Sound('resources/golden.wav')
    SOUNDS['Life'] = pygame.mixer.Sound('resources/life.wav')
    SOUNDS['Special'] = pygame.mixer.Sound('resources/special.wav')
    SOUNDS['Hit'] = pygame.mixer.Sound('resources/hit.wav')

def mute_sounds(mute):
    for sound in SOUNDS.values():
        sound.set_volume(1 if mute else 0)

def play_sound(sound, train):
    if not train:
        SOUNDS[sound].play()

class AppleTypes:

    NORMAL, GOLDEN, LIFE, SPECIAL = range(4)

# Apple Colors
APPLE_COLORS = {
        AppleTypes.NORMAL : RED,
        AppleTypes.GOLDEN : YELLOW,
        AppleTypes.LIFE : MAGENTA,
        AppleTypes.SPECIAL : CYAN
        }

# Snake Colors
SNAKE_COLORS = [BLUE, GREEN]

class Apple:

    def __init__(self, snakes, train=False):
        retry = True
        while retry:
            retry = False
            self.x = random.randint(0, CELL_COUNT_X - 1)
            self.y = random.randint(0, CELL_COUNT_Y - 1)
            for i in range(len(snakes)):
                for j in range(0, snakes[i].length):
                    if self.x == snakes[i].x[j] and self.y == snakes[i].y[j]:
                        retry = True
        if train:
            self.apple_type = 0
        else:
            self.apple_type = random.choice([0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3])

        self.cooldown = 0
        self.moves = 0
        self.direction = random.choice([0, 1, 2, 3])
        if not self.apple_type == AppleTypes.NORMAL:
            self.cooldown = APPLE_COOLDOWN
            if self.apple_type == AppleTypes.SPECIAL:
                self.moves = SPECIAL_FRAMES

    def move(self):
        if self.moves == 0:
            direction = random.choice([
                self.direction,
                self.direction,
                self.direction,
                self.direction,
                self.direction,
                self.direction,
                self.direction,
                (self.direction + 1) % 4,
            
                (self.direction + 2) % 4,
                (self.direction + 3) % 4])
            if direction == 0:
                if not self.x == CELL_COUNT_X - 1:
                    self.x += 1
                else:
                    self.x -= 1
                    self.direction = 2
            if direction == 1:
                if not self.y == CELL_COUNT_Y - 1:
                    self.y += 1
                else:
                    self.y -= 1
                    self.direction = 3
            if direction == 2:
                if not self.x == 0:
                    self.x -= 1
                else:
                    self.x += 1
                    self.direction = 1
            if direction == 3:
                if not self.y == 0:
                    self.y -= 1
                else:
                    self.y += 1
                    self.direction = 0
            self.moves = SPECIAL_FRAMES
        else:
            self.moves -= 1

    def draw(self, surface, cell_size, color=None):
        body = pygame.Surface((cell_size, cell_size))
        if color is None:
            body.fill(APPLE_COLORS[self.apple_type])
        else:
            body.fill(color)
        surface.blit(body, ((self.x + 1)  * cell_size, (self.y + 1) * cell_size))

        if self.cooldown == 0:
            self.apple_type = AppleTypes.NORMAL
        else:
            self.cooldown -= 1


class Snake:

    def __init__(self, x, y, length, lives, color):
        self.x = [x]
        self.y = [y]
        self.length = length
        self.direction = 0 if self.x[0] < CELL_COUNT_X / 2 else 2
        for i in range(1, self.length):
            self.x.append(self.x[0] - i if self.x[0] < CELL_COUNT_X / 2 else self.x[0] + i)
            self.y.append(self.y[0])
        self.color = color
        self.temp_color = color
        self.score = 0
        self.lives = lives
        self.cooldown = 0
        self.step = WAIT_STEPS

    def turn_right(self):
        self.direction += 1
        if self.direction == 4:
            self.direction = 0

    def turn_left(self):
        self.direction -= 1
        if self.direction == -1:
            self.direction = 3

    def change_direction(self, direction):
        if direction != (self.direction + 2) % 4:
            self.direction = direction
            return True
        return False

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

    def change_color(self, color):
        self.temp_color = color
        self.cooldown = SNAKE_COOLDOWN

    def add_piece(self, count):
        for i in range(0, count):
            self.x.append(self.x[self.length - 1])
            self.y.append(self.y[self.length - 1])
            self.length += 1

    def eat_apple(self, apple):
        if self.collide(apple.x, apple.y):
            return True
        else:
            return False

    def hit_self(self):
        for i in range(1, self.length):
            if self.collide(self.x[i], self.y[i]):
                if self.temp_color == RED:
                    return False
                else:
                    return True
        return False

    def hit_border(self):
        if self.x[0] < 0 or self.x[0] > CELL_COUNT_X - 1:
            self.x[0] = CELL_COUNT_X - 1 if self.x[0] < 0 else 0
            if self.temp_color == RED:
                return False
            else:
                return True
        elif self.y[0] < 0 or self.y[0] > CELL_COUNT_Y - 1:
            self.y[0] = CELL_COUNT_Y - 1 if self.y[0] < 0 else 0
            if self.temp_color == RED:
                return False
            else:
                return True
        else:
            return False

    def get_distance(self, targetx, targety, direction):

        if direction == 0:
            if self.y[0] == targety and targetx > self.x[0]:
                return 1 - (targetx - self.x[0]) / CELL_COUNT_X
            else:
                return 0

        elif direction == 1:
            if self.x[0] == targetx and targety > self.y[0]:
                return 1 - (targety - self.y[0]) / CELL_COUNT_Y
            else:
                return 0

        elif direction == 2:
            if self.y[0] == targety and targetx < self.x[0]:
                return 1 - (self.x[0] - targetx) / CELL_COUNT_X
            else:
                return 0

        elif direction == 3:
            if self.x[0] == targetx and targety < self.y[0]:
                return 1 - (self.y[0] - targety) / CELL_COUNT_Y
            else:
                return 0
        else:
            return 0

    def get_inputs(self, apple):
        
        #distance from apple
        apple_front = self.get_distance(apple.x, apple.y, self.direction)
        apple_left = self.get_distance(apple.x, apple.y, (self.direction - 1) % 4)
        apple_right = self.get_distance(apple.x, apple.y, (self.direction + 1) % 4)

        #distance from wall
        wall_front = 0
        wall_left = 0
        wall_right = 0

        if self.direction == 0:
            wall_front = self.x[0] / CELL_COUNT_X
            wall_right = self.y[0] / CELL_COUNT_Y
            wall_left = 1 - wall_right

        elif self.direction == 1:
            wall_front = self.y[0] / CELL_COUNT_Y
            wall_left = self.x[0] / CELL_COUNT_X
            wall_right = 1 - wall_left

        elif self.direction == 2:
            wall_front = 1 - self.x[0] / CELL_COUNT_X
            wall_left = self.y[0] / CELL_COUNT_Y
            wall_right = 1 - wall_left

        elif self.direction == 3:
            wall_front = 1 - self.y[0] / CELL_COUNT_Y
            wall_right = self.x[0] / CELL_COUNT_X
            wall_left = 1 - wall_right

        #distance from self
        self_front = 0
        self_left = 0
        self_right = 0

        for i in range(3, self.length):
            front = self.get_distance(self.x[i], self.y[i], self.direction)
            if front > self_front:
                self_front = front
            left = self.get_distance(self.x[i], self.y[i], (self.direction - 1) % 4)
            if left > self_left:
                self_left = left
            right = self.get_distance(self.x[i], self.y[i], (self.direction + 1) % 4)
            if right > self_right:
                self_right = right

        return [apple_front, apple_left, apple_right, wall_front, wall_left, wall_right, self_front, self_left, self_right]

    def draw(self, surface, cell_size, color=None):
        body = pygame.Surface((cell_size, cell_size))
        if color is None:
            body.fill(self.temp_color)
        else:
            body.fill(color)

        for i in range(0, self.length):
            surface.blit(body, ((self.x[i] + 1) * cell_size, (self.y[i] + 1) * cell_size))

        if self.cooldown > 0:
            self.cooldown -= 1
        else:
            self.temp_color = self.color

class Game:

    def __init__(self, players, difficulty, train=False, ai=None):
        self.fps = difficulty
        self.snakes = []
        self.apples = []
        for i in range(players):
            if train: 
                snake = Snake(CELL_COUNT_X / 2, CELL_COUNT_Y / 2, 15, 1, GREEN) 
                self.snakes.append(snake)
                self.apples.append(Apple([snake], train))
            else:
                if i < MAX_PLAYERS:
                    self.snakes.append(Snake(random.randint(CELL_COUNT_X / 2, CELL_COUNT_X - 1), random.randint(CELL_COUNT_Y / 2, CELL_COUNT_Y - 1), 15, 3, SNAKE_COLORS[i]))
                if i == 0:
                    self.apples.append(Apple(self.snakes))
        self.train = train
        self.ai = ai

    def restart(self):
        return Game(len(self.snakes), self.fps, train=self.train, ai=self.ai)

    def best_snake(self):
        sorted_snakes = sorted(self.snakes, key=attrgetter('score'), reverse=True)
        for snake in sorted_snakes:
            if snake.lives > 0:
                return snake

    def update(self, clock):
        clock.tick(self.fps)

        if self.apples[0].apple_type == AppleTypes.SPECIAL:
            self.apples[0].move()

        for i in range(len(self.snakes)):
            if self.snakes[i].lives > 0:
                self.snakes[i].move()
                if self.snakes[i].hit_self() or self.snakes[i].hit_border():
                    play_sound('Hit', self.train)
                    self.snakes[i].lives -= 1
                    if not self.train:
                        self.snakes[i].score -= 50
                        self.snakes[i].change_color(RED)
                        if self.snakes[i].lives == 0:
                            return False
                else:
                    if self.train:
                        apple = self.apples[i]
                    else:
                        apple = self.apples[0]
                    if self.snakes[i].eat_apple(apple):
                        self.snakes[i].step = WAIT_STEPS
                        if apple.apple_type == AppleTypes.NORMAL:
                            play_sound('Apple', self.train)
                            self.snakes[i].add_piece(1)
                            self.snakes[i].score += self.snakes[i].step / WAIT_STEPS if self.train else 10
                        elif apple.apple_type == AppleTypes.GOLDEN:
                            play_sound('Golden', self.train)
                            self.snakes[i].add_piece(3)
                            self.snakes[i].score += 50
                        elif apple.apple_type == AppleTypes.LIFE:
                            play_sound('Life', self.train)
                            self.snakes[i].add_piece(1)
                            if self.snakes[i].lives < 5:
                                self.snakes[i].lives += 1
                            else:
                                self.snakes[i].score += 20
                        elif apple.apple_type == AppleTypes.SPECIAL:
                            play_sound('Special', self.train)
                            self.snakes[i].add_piece(5)
                            self.snakes[i].score += 100
                        if not apple.apple_type == AppleTypes.NORMAL:
                            self.snakes[i].change_color(APPLE_COLORS[apple.apple_type])
                        if self.train:
                            self.apples[i] = Apple([self.snakes[i]], self.train)
                        else:
                            self.apples[0] = Apple(self.snakes)
                    else:
                        if self.train:
                            self.snakes[i].step -= 1
                if self.snakes[i].step <= 0:
                    self.snakes[i].lives = 0
        return True

    def is_stopped(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    return True
        return False

    def end(self):
        pygame.quit()

    def render(self, surface, cell_size, font):
        surface.fill(BLACK)
        pygame.draw.rect(surface, WHITE, Rect(0, 0, surface.get_width(), surface.get_height()), cell_size)

        self.draw(surface, cell_size)

        best = self.best_snake()
        if best.lives > 0:
            score_surf = font.render(str(int(best.score)), True, YELLOW)
            score_rect = score_surf.get_rect()
            score_rect.topright = (CELL_COUNT_X * cell_size, 1.5 * cell_size)
            surface.blit(score_surf, score_rect)

            step_surf = font.render(str(best.step), True, LIGHT_GRAY)
            step_rect = step_surf.get_rect()
            step_rect.topright = (CELL_COUNT_X * cell_size, 3 * cell_size)
            surface.blit(step_surf, step_rect)

        pygame.display.flip()

    def draw(self, surface, cell_size):
        best = self.best_snake()
        best_index = 0
        for i in range(len(self.snakes)):
            if self.snakes[i] is best:
                best_index = i
                continue
            if self.snakes[i].lives > 0:
                if self.train:
                    self.snakes[i].draw(surface, cell_size, DARK_GRAY)
                else:
                    self.snakes[i].draw(surface, cell_size)
        if self.train:
            for i in range(len(self.apples)):
                if i == best_index:
                    continue
                if self.snakes[i].lives > 0:
                    if self.train:
                        self.apples[i].draw(surface, cell_size, LIGHT_GRAY)
        else:
            best_index = 0
        best.draw(surface, cell_size)
        self.apples[best_index].draw(surface, cell_size)

def init_screen(caption, scale=GUI_SCALE):
    pygame.init()
    pygame.display.set_caption(caption)
    icon = pygame.image.load('resources/icon.png')
    pygame.display.set_icon(icon)

    pygame.event.set_allowed([QUIT, KEYDOWN, MOUSEBUTTONDOWN])

    cell_size = int(pygame.display.Info().current_w / scale)
    width = CELL_COUNT_X * cell_size + 2 * cell_size
    height = CELL_COUNT_Y * cell_size + 2 * cell_size
    screen = pygame.display.set_mode((width, height), pygame.HWSURFACE)

    return cell_size, screen


if __name__ == '__main__':

    args = len(sys.argv)
    if args == 1:
        neural_net = None
        players = 1
    elif args == 2:
        filename = sys.argv[1]
        if filename.endswith('.json'):
            neural_net = nn.fromJSON(filename)
            players = 2
        else:
            print('usage: snake.py [snake_nn.json]')
            sys.exit()
    else:
        print('usage: snake.py [snake_nn.json]')
        sys.exit()

    cell_size, screen = init_screen('Python VS Viper - Debug')

    font = pygame.font.Font('resources/font.ttf', 30)
    clock = pygame.time.Clock()

    init_sounds()

    running = True

    game = Game(players, 30, ai=neural_net)

    while running:

        game.render(screen, cell_size, font)
        player = game.snakes[0]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_RIGHT:
                    player.change_direction(0)
                    break
                elif event.key == K_DOWN:
                    player.change_direction(1)
                    break
                elif event.key == K_LEFT:
                    player.change_direction(2)
                    break
                elif event.key == K_UP:
                    player.change_direction(3)
                    break
                elif event.key == K_ESCAPE:
                    running = False
                    break
                elif event.key == K_RETURN:
                    game = game.restart()
                    break

        if game.ai:
            for i in range(1, len(game.snakes)):
                player = game.snakes[i]
                inputs = player.get_inputs(game.apples[0])
                action = np.argmax(neural_net.compute_outputs(inputs))
                if action == 0:
                    player.turn_right()
                elif action == 1:
                    player.turn_left()

        if not game.update(clock):
            game = game.restart()

    # Quit
    pygame.quit()
