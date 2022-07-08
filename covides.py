import pygame
import random
from pygame import mixer

#Initializing pygame module
pygame.init()

#Initialize clock function
clock = pygame.time.Clock()
fps = 60

#Setting width and height for display
screen_width = 864
screen_height = 700

#Setting caption for screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Covid Escape - Game')

#Defining font
font = pygame.font.SysFont('Bauhaus 93', 60)

#Defining colours
green = (118, 238, 0)

#Defining game variables
base_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_freq = 1500 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_freq
score = 0
pass_pipe = False

#Load required assets to the pygame module
title = pygame.image.load('titlescreen.png')
bg = pygame.image.load('background.png')
base = pygame.image.load('road.png')
restart_but = pygame.image.load('restart.png')
gameover = pygame.image.load('gameover.png')
quote = pygame.image.load('endquote.png')

#Adding title sound score
mixer.music.load('bgm.mp3')
mixer.music.play()

#Defining draw_text function
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#Defining reset_game function
def reset_game():
    pipe_group.empty()
    player.rect.x = 100
    player.rect.y = int(screen_height / 2)
    score = 0
    return score

#Defining sprite class Player
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'player.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

#Defining update
    def update(self):

        if flying == True:
            #adding gameover sound effect
            mixer.music.load('gameover_bgm.mp3')
            mixer.music.play()
            #gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 600:
                self.rect.y += int(self.vel)

        if game_over == False:
            #Player jump functionality
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                #Adding sound on click
                click_bgm = mixer.Sound('click_bgm.mp3')
                click_bgm.play()
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            #Rotate the player while hitting the ground
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

#Defining sprite class Pipe
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('pipe.png')
        self.rect = self.image.get_rect()

        #Position 1 is from the top, -1 is from the bottom assigning to pipes
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

#Defining sprite class Button
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    #Defining draw function
    def draw(self):
        action = False

        #Get mouse position
        pos = pygame.mouse.get_pos()

        #Check if the mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #Draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

player_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

player = Player(100, int(screen_height / 2))

player_group.add(player)

#Creating restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, restart_but)

run = True
while run:

    clock.tick(fps)

    #Draw background for the game
    screen.blit(bg, (0,0))

    #Draw titlescreen until start
    if flying == False and game_over == False:
        screen.blit(title, (0, 0))

    #Draw gameover text for gameover screen
    if game_over == True:
        screen.blit(gameover, (330, 100))
        screen.blit(quote, (200, 100))

    #Withdraw pipes and player for gameover screen
    if game_over == False:
        player_group.draw(screen)
        player_group.update()
        pipe_group.draw(screen)

    #Draw the scrolling base for the moving effect
    screen.blit(base, (base_scroll, 600))

    #Check the score
    if len(pipe_group) > 0:
        if player_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and player_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if player_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text("Covid wave : " + str(score), font, green, 275, 10)

    #Look for collision between pipe and player
    if pygame.sprite.groupcollide(player_group, pipe_group, False, False) or player.rect.top < 0:
        game_over = True

    #Check if player has hit the ground
    if player.rect.bottom >= 600:
        game_over = True
        flying = False

    if game_over == False and flying == True:
        #Generate new pipes (Iterations)
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_freq:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        #Scroll the base
        base_scroll -= scroll_speed
        if abs(base_scroll) > 35:
            base_scroll = 0

        pipe_group.update()

    #Check for game over and reset
    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
    pygame.display.update()
pygame.quit()