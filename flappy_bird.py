import pygame
import neat
import os
import random

WIN_WIDTH = 500
WIN_HEIGHT = 800

# 2 times the img, load img, finding path
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("Desktop", "Flappy Bird AI", "IMGS", "bird1.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("Desktop", "Flappy Bird AI", "IMGS", "bird2.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("Desktop", "Flappy Bird AI", "IMGS", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Desktop", "Flappy Bird AI", "IMGS", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Desktop", "Flappy Bird AI", "IMGS", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Desktop", "Flappy Bird AI", "IMGS", "bg.png")))

pygame.display.set_caption("Flappy Bird AI")
pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)

gene = 0

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25       # 25 degree upward
    ROTATION_VELOCITY = 20      # each frame
    ANIMATION_TIME = 5      # wings flapping time


    # FIRST method: bird location and animation setting
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0       # starting at flat
        self.tick_count = 0     # physics like jump and down
        self.velocity = 0
        self.height = self.y    # y location when moving bird
        self.img_count = 0      # img for showing when moving
        self.img = self.IMGS[0]     # represent bird1.png


    # SECOND method: jump animation  
    # for pygame windows, the (x, y) of the top left corner will be (0, 0) 
    # so going up(↑) will be negative velocity, and going down(↓) will be positive velocity
    # going left(←) will be negative velocity, and going right(→) will be positive velocity
    def jump(self):
        self.velocity = -10.5
        self.tick_count = 0     # track for last jump, 0 for changing velocity or direction
        self.height = self.y


    # THIRD method: frame move
    def move(self):
        self.tick_count += 1

        # displacement = ut + 1/2at^2
        # example: current frame 1 / velocity -9.0
        #          current frame 2 / velocity -15.0
        #          current frame 3 / velocity -18.0
        #          current frame 4 / velocity -18.0
        #          current frame 5 / velocity -15.0
        #          current frame 6 / velocity -9.0
        #          current frame 7 / velocity  0.0
        # move up and down (curve)
        d = self.velocity * self.tick_count + 1.5 * self.tick_count ** 2

        # make sure bird not moving way too far up and down
        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

        
        if d < 0 or self.y < self.height + 50:      # make sure bird still going up
            if self.tilt < self.MAX_ROTATION:       # make sure bird not rotate backward
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:     # rotate completely 90 degree down
                self.tilt -= self.ROTATION_VELOCITY


    # FOURTH method: draw bird
    def draw(self, window):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:        # 5 frame
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:      # 10 frame
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:      # 15 frame
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:      # 20 frame
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:     # reset 
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:        # when falling down img stay at bird2
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # for rotate information    
        # https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        window.blit(rotated_image, new_rect.topleft)
        
    # FIFTH method: create a mask from the given surface
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VELOCITY = 5


    # FIRST method: pipe setting
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()


    # SECOND method: top and bottom pipe location
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP


    # THIRD method: pipe moving function
    def move(self):
        self.x -= self.VELOCITY     # bird move right(→), pipe move left(←)


    # FOURTH method: draw pipe
    def draw(self, window):
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    # FIFTH method: collision of bird and pipe
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_pipe_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_pipe_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_pipe_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_pipe_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # bird collision with pipe, NONE for no
        top_point = bird_mask.overlap(top_pipe_mask, top_pipe_offset)
        bottom_point = bird_mask.overlap(bottom_pipe_mask, bottom_pipe_offset)

        if top_point or bottom_point:       # if collision
            return True
        
        return False


class Base:
    VELOCITY = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG


    # 2 base img
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH


    # moving left(←)
    def  move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        # a cycle between 2 same base img (eg: 1 → 2 → 1 → 2 → 1)
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH


    def draw(self, window):
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))


# blit actually means draw
def draw_window(window, birds, pipes, base, score, gene):
    window.blit(BG_IMG, (0, 0))

    for bird in birds:
        bird.draw(window)
    for pipe in pipes:
        pipe.draw(window)
    base.draw(window)
    
    if gene == 0:
        gene = 1

    text = STAT_FONT.render("Gens: " + str(gene - 1), 1, (255, 255, 255))
    window.blit(text, (10, 10))      # keeping in top left position

    text = STAT_FONT.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
    window.blit(text, (10, 50))      # keeping in top middle position

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))      # keeping in top right position

    pygame.display.update()


# main window
def main(genomes, config):
    global gene
    gene += 1
    nets = []
    gen = []
    birds = []                    # for NEAT

    for g_id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        
        g.fitness = 0
        gen.append(g)

        birds.append(Bird(230, 350))
    
    # bird = Bird(230, 350)       # starting location for DEMO
    pipes = [Pipe(600)]
    base = Base(730)
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))       # main window setting
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run:
        clock.tick(30)      # atmost 30 tick per sec(30 frame)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        # bird.move()       # check if bird move function correct, for DEMO

        # to check if the bird is/isn't collide with the first showing pipes and not the second showing pipes
        # maximum 2 rows of pipes showing on the window
        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_index = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            gen[x].fitness += 0.1
            bird.move()

            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))

            if output[0] > 0.5:
                bird.jump()

        remove = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            for bird in birds:
                if pipe.collide(bird):
                    gen[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    gen.pop(birds.index(bird))
                    birds.pop(birds.index(bird))
            
            # after the bird passed the pipes, create new pipes
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            for g in gen:
                g.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in remove:
            pipes.remove(r)

        # check if bird hit the ground or over the sky
        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= 730 or bird.y < -50:
                nets.pop(birds.index(bird))
                gen.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        # stop when score = 100
        if score > 30:
            break

        base.move()
        draw_window(window, birds, pipes, base, score, gene)


"""
NEAT(AI)
1. inputs: bird.y, top_pipe, bottom_pipe
2. outputs: jump/not jump
3. activation function: tanh (evaluate values between 1/-1)
4. population size: 100 (birds, start with Gen 0)
5. fitness function: distance (further distance, better generation)
6. max generations: 30 (if fail 30 tries, means programming fail)

"""

def run(config_file):
    # load in the configuration file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    # set up population
    p = neat.Population(config)

    # set the output we gonna see
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # run for up to 50 generations
    winner = p.run(main, 50)

    # show final stats
    print("\nBest genome:\n{!s}".format(winner))


# file path
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt") 
    run(config_path)


