#!/usr/bin/python

import pygame, sys, os, math, random, copy
from pygame.locals import *

#the images are in the "images" folder
def loadimage(name, x=0, y=0, size=None):
    #arguments: name of the image, x and y position of the top-left corner inside the image, size of the image (it is a square).
    #returns: surface with the image, rect of that surface
    image_path = os.path.join('images', name)
    image = pygame.image.load(image_path).convert_alpha()
    if size != None:
        image_surface = pygame.Surface((size, size))
        image_surface.blit(image, (0, 0), (x, y, size, size))
    else:
        image_surface = image
    return image_surface

class Text(pygame.sprite.Sprite):
    def __init__(self, font_name, size):   
        pygame.sprite.Sprite.__init__(self)
        font_path = os.path.join('font', font_name)
        self.font = pygame.font.Font(font_path, size)
    def set(self, bottomright, text, color):
        self.text = str(text)
        self.image = self.font.render(self.text, False, color)
        self.rect = self.image.get_rect()
        self.rect.bottomright = bottomright

def getsound(name):
    file_path = os.path.join('sounds', name)
    return pygame.mixer.Sound(file_path)

class Pacman(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.upimages = (loadimage('sprites.png', 0, 0, 16), loadimage('sprites.png', 16, 0, 16), loadimage('sprites.png', 0, 0, 16), loadimage('sprites.png', 32, 0, 16))
        self.downimages = (loadimage('sprites.png', 48, 0, 16), loadimage('sprites.png', 64, 0, 16), loadimage('sprites.png', 48, 0, 16), loadimage('sprites.png', 80, 0, 16))
        self.leftimages = (loadimage('sprites.png', 96, 0, 16), loadimage('sprites.png', 112, 0, 16), loadimage('sprites.png', 96, 0, 16), loadimage('sprites.png', 0, 16, 16))
        self.rightimages = (loadimage('sprites.png', 16, 16, 16), loadimage('sprites.png', 32, 16, 16), loadimage('sprites.png', 16, 16, 16), loadimage('sprites.png', 48, 16, 16))
        self.deathimages = (loadimage('sprites.png', 0, 128, 16), loadimage('sprites.png', 16, 128, 16), loadimage('sprites.png', 32, 128, 16), loadimage('sprites.png', 48, 128, 16), loadimage('sprites.png', 64, 128, 16), loadimage('sprites.png', 80, 128, 16), loadimage('sprites.png', 96, 128, 16), loadimage('sprites.png', 112, 128, 16))
        self.image = self.upimages[0]
        self.rect = self.image.get_rect().move(160 , 272 )
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.current_animation = 0
        self.animation_timer = 0
        self.death = None
        self.sdots_eaten = 0
    def update(self):
        if self.death == None:
            if (self.rect.x % (16 ) == 0 and self.rect.y % (16 ) == 0) or self.next_direction == (- self.direction[0], - self.direction[1]):
                self.direction = self.next_direction
            if self.direction == (0, -1):
                self.image = self.upimages[self.current_animation]
            elif self.direction == (0, 1):
                self.image = self.downimages[self.current_animation]
            elif self.direction == (-1, 0):
                self.image = self.leftimages[self.current_animation]
            elif self.direction == (1, 0):
                self.image = self.rightimages[self.current_animation]
            if self.animation_timer % 4 == 0 :
                if self.current_animation < 3:
                    self.current_animation += 1
                else: 
                    self.current_animation = 0
            self.animation_timer +=1 
            self.rect.move_ip(self.direction[0], self.direction[1])

            #teleport pacman if he goes outside the map
            if self.rect.x == -16:
                self.rect.x = 333
            elif self.rect.x == 334:
                self.rect.x = -15

            #check the collision
            global score
            if pygame.sprite.spritecollideany(self, wallgroup) != None:
                self.rect.move_ip(self.direction[0]  * -1, self.direction[1]  * -1)
            if pygame.sprite.spritecollideany(self, ghostgroup) != None:
                collided_ghost = pygame.sprite.spritecollideany(self, ghostgroup)
                if collided_ghost.mode == 'CHASE' or collided_ghost.mode == 'SCATTER':
                    self.death = 0.0
                    death_sound.play()
                elif collided_ghost.mode == 'FRIGHTENED':
                    collided_ghost.dead = True
                    score += 300
                    eatghost_sound.play()
            dot = pygame.sprite.spritecollideany(self, smalldotgroup)
            if dot != None:
                if dot.is_alive == True:
                    self.sdots_eaten += 1
                    score += 10
                    dot.is_alive = False
                    if dot.is_big:
                        bdot_sound.play()
                        for ghost in ghostgroup:
                            if ghost.mode == 'SCATTER' or ghost.mode == 'CHASE' or ghost.mode == 'FRIGHTENED':
                                if current_level == 1:
                                    ghost.frighttimer = 10 * 60
                                elif current_level <= 2:
                                    ghost.frighttimer = 7 * 60
                                elif current_level <= 4:
                                    ghost.frighttimer = 6 * 60
                                elif current_level <= 6:
                                    ghost.frighttimer = 5 * 60
                                elif current_level <= 9:
                                    ghost.frighttimer = 4 * 60
                                elif current_level >= 15:
                                    ghost.frighttimer = 2 * 60
                                score += 40
                    else: sdot_sound.play()
        else:
            if self.death >= 7.0:
                quit_hscore()
            self.image = self.deathimages[int(self.death)]
            self.death += 0.1

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, xsize, ysize):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect((x , y ), (xsize , ysize ))
        self.add(wallgroup)

class Ghost(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.mode = 'STOP'
        self.upimages = (loadimage('sprites.png', 0, 32 + 16 * color, 16), loadimage('sprites.png', 16, 32 + 16 * color, 16))
        self.downimages = (loadimage('sprites.png', 32, 32 + 16 * color, 16), loadimage('sprites.png', 48, 32 + 16 * color, 16))
        self.leftimages = (loadimage('sprites.png', 64, 32 + 16 * color, 16), loadimage('sprites.png', 80, 32 + 16 * color, 16))
        self.rightimages = (loadimage('sprites.png', 96, 32 + 16 * color, 16), loadimage('sprites.png', 112, (32 + 16 * color), 16))
        self.frightimages = (loadimage('sprites.png', 64, 16, 16), loadimage('sprites.png', 80, 16, 16), loadimage('sprites.png', 96, 16, 16), loadimage('sprites.png', 112, 16, 16))
        self.eyesimages = (loadimage('sprites.png', 64, 112, 16), loadimage('sprites.png', 80, 112, 16), loadimage('sprites.png', 96, 112, 16), loadimage('sprites.png', 112, 112, 16))
        self.image = self.upimages[1]
        self.rect = self.image.get_rect().move(x, y)
        self.direction = (0,0)
        self.target = (64, 64)
        self.current_normanimation = 0
        self.current_frightanimation = 0
        self.animation_timer = 0
        self.timer = 0
        self.frighttimer = 0
        self.dead = False
        self.speed = 1

    def update(self):
        self.update_timer()
        self.mode = self.get_mode()
        if self.rect.x % (16 ) == 0 and self.rect.y % (16 ) == 0:
            self.direction = self.get_direction()
        if self.mode == 'CHASE' or self.mode == 'SCATTER':
            if self.direction == (0, -1):
                self.image = self.upimages[self.current_normanimation]
            elif self.direction == (0, 1):
                self.image = self.downimages[self.current_normanimation]
            elif self.direction == (-1, 0):
                self.image = self.leftimages[self.current_normanimation]
            elif self.direction == (1, 0):
                self.image = self.rightimages[self.current_normanimation]
            if self.timer % 4 == 0 :
                self.current_normanimation = int(not bool(self.current_normanimation))
        elif self.mode == 'FRIGHTENED':
            self.image = self.frightimages[self.current_frightanimation]
            if self.frighttimer % 4 == 0:
                self.current_frightanimation += 1
                if self.current_frightanimation > 3:
                    self.current_frightanimation = 0
        elif self.mode == 'EYES':
            if self.direction == (0, -1):
                self.image = self.eyesimages[0]
            if self.direction == (0, 1):
                self.image = self.eyesimages[1]
            if self.direction == (-1, 0):
                self.image = self.eyesimages[2]
            if self.direction == (1, 0):
                self.image = self.eyesimages[3]


        self.animation_timer += 1
        if pacman.death == None:
            if self.mode == 'FRIGHTENED':
                if self.frighttimer % 2 == 0:
                    self.rect.move_ip(self.direction[0] , self.direction[1] )
            else: self.rect.move_ip(self.direction[0] , self.direction[1] )

            #teleport the ghost if he goes outside the map
            if self.rect.x == -16:
                self.rect.x = 333
            elif self.rect.x == 334:
                self.rect.x = -15

    def get_direction(self):
        direction = 0
        if self.mode == 'EYES' and self.rect.topleft == (160 , 128 ):
            direction = 1
            self.dead = False
            self.frighttimer = 0
        elif self.mode == 'CHASE' or self.mode == 'SCATTER' or self.mode == 'EYES':
            self.target = self.get_target()
            possible_directions = [999999999, 999999999, 999999999, 999999999]

            if self.rect.move(0, -16 ).collidelist(walls) == -1 and self.direction != (0, 1):
                possible_directions[0] = (self.rect.move(0, -16 ).centerx - self.target[0])**2 + (self.rect.move(0, -16 ).centery - self.target[1])**2

            if self.rect.move(0, 16 ).collidelist(walls) == -1 and self.direction != (0, -1):
                possible_directions[1] = (self.rect.move(0, 16 ).centerx - self.target[0])**2 + (self.rect.move(0, 16 ).centery - self.target[1])**2

            if self.rect.move(-16 , 0).collidelist(walls) == -1 and self.direction != (1, 0):
                possible_directions[2] = (self.rect.move(-16 , 0).centerx - self.target[0])**2 + (self.rect.move(-16 , 0).centery - self.target[1])**2

            if self.rect.move(16 , 0).collidelist(walls) == -1 and self.direction != (-1, 0):
                possible_directions[3] = (self.rect.move(16 , 0).centerx - self.target[0])**2 + (self.rect.move(16 , 0).centery - self.target[1])**2
           
            smallest_as_far = possible_directions[0]
            direction = 0
            for i in range(1,4):
                if smallest_as_far > possible_directions[i]:
                    smallest_as_far = possible_directions[i]
                    direction = i

        elif self.mode == 'FRIGHTENED':
            possible_directions = []
            if self.rect.move(0, -16).collidelist(walls) == -1 and self.direction != (0, 1):
                possible_directions.append(0)
            if self.rect.move(0, 16).collidelist(walls) == -1 and self.direction != (0, -1):
                possible_directions.append(1)
            if self.rect.move(-16, 0).collidelist(walls) == -1 and self.direction != (1, 0):
                possible_directions.append(2)
            if self.rect.move(16, 0).collidelist(walls) == -1 and self.direction != (-1, 0):
                possible_directions.append(3)
            direction = possible_directions[random.randrange(0, len(possible_directions))]

        elif self.mode == 'STOP':
            return (0, 0)

        if direction == 0: return (0, -1)
        elif direction == 1: return (0, 1)
        elif direction == 2: return (-1, 0)
        elif direction == 3: return (1, 0)

    def get_mode(self):
        if self.dead == True:
            return 'EYES'
        elif self.mode == 'SCATTER' or self.mode == 'CHASE' or self.mode == 'FRIGHTENED' or self.mode == 'EYES':
            if self.frighttimer <= 0:
                if current_level == 1:
                    if self.timer < 7 * 60:
                        return 'SCATTER'
                    elif self.timer < 27 * 60:
                        return 'CHASE'
                    elif self.timer < 34 * 60:
                        return 'SCATTER'
                    elif self.timer < 54 * 60:
                        return 'CHASE'
                    elif self.timer < 59 * 60:
                        return 'SCATTER'
                    elif self.timer < 79 * 60:
                        return 'CHASE'
                    elif self.timer < 84 * 60:
                        return 'SCATTER'
                    elif self.timer > 84 * 60:
                        return 'CHASE'
                elif current_level >= 2 and current_level < 5:
                    if self.timer < 7 * 60:
                        return 'SCATTER'
                    elif self.timer < 27 * 60:
                        return 'CHASE'
                    elif self.timer < 34 * 60:
                        return 'SCATTER'
                    elif self.timer < 54 * 60:
                        return 'CHASE'
                    elif self.timer < 59 * 60:
                        return 'SCATTER'
                    elif self.timer < 1033 * 60:
                        return 'CHASE'
                    elif self.timer < 1033 * 60 + 1:
                        return 'SCATTER'
                    elif self.timer > 1033 * 60 + 1:
                        return 'CHASE'
                if current_level >= 5:
                    if self.timer < 5 * 60:
                        return 'SCATTER'
                    elif self.timer < 25 * 60:
                        return 'CHASE'
                    elif self.timer < 30 * 60:
                        return 'SCATTER'
                    elif self.timer < 50 * 60:
                        return 'CHASE'
                    elif self.timer < 55 * 60:
                        return 'SCATTER'
                    elif self.timer < 1092 * 60:
                        return 'CHASE'
                    elif self.timer < 1092 * 60 + 1:
                        return 'SCATTER'
                    elif self.timer > 84 * 60 + 1:
                        return 'CHASE'
            elif self.frighttimer > 0:
                return 'FRIGHTENED'
        elif self.mode == 'STOP':
            if pacman.sdots_eaten >= self.sdots_count:
                return 'SCATTER'
            else: 
                return 'STOP'
    
    def update_timer(self):
        if self.mode == 'SCATTER' or self.mode == 'CHASE':
            self.timer += 1
        elif self.mode == 'FRIGHTENED':
            self.frighttimer -= 1

class Blinky(Ghost):
    def __init__(self):
        Ghost.__init__(self, 0, 160 , 128 )
        self.sdots_count = 1
    def get_target(self):
        if self.mode == 'CHASE': return pacman.rect.center
        elif self.mode == 'SCATTER' : return (332 , 0)
        elif self.mode == 'EYES': return (166 , 177 )

class Pinky(Ghost):
    def __init__(self):
        Ghost.__init__(self, 1, 160 , 160 )
        self.sdots_count = 1
    def get_target(self):
        self.targetforinky = pacman.rect.move(pacman.direction[0] * 32 , pacman.direction[1] * 32 )
        if self.mode == 'CHASE': return pacman.rect.move(pacman.direction[0] * 32 , pacman.direction[1] * 32 )
        elif self.mode == 'SCATTER' : return (0, 0)
        elif self.mode == 'EYES': return (166 , 177 )

class Inky(Ghost):
    def __init__(self):
        Ghost.__init__(self, 2, 144 , 160 )
        self.sdots_count = 30
    def get_target(self):
        if self.mode == 'CHASE': 
            return pinky.targetforinky.move(pacman.rect.move(pacman.direction[0] * 32 , pacman.direction[1] * 32 ).centerx - blinky.rect.centerx, pacman.rect.move(pacman.direction[0] * 32 , pacman.direction[1] * 32 ).centery - blinky.rect.centery).center
        elif self.mode == 'SCATTER' : return (332 , 390 )         
        elif self.mode == 'EYES': return (166 , 177 )

class Clyde(Ghost):
    def __init__(self):
        Ghost.__init__(self, 3, 176 , 160 )
        self.sdots_count = 90
    def get_target(self):
        if self.mode == 'CHASE':
            if math.sqrt((self.rect.centerx - pacman.rect.centerx)**2 + (self.rect.centery - pacman.rect.centery)**2) < 128 :
                return (0, 390 )
            else:
                return pacman.rect.center
        elif self.mode == 'SCATTER':
            return (0, 390 )
        elif self.mode == 'EYES': return (166 , 177 )

class SmallDot(pygame.sprite.Sprite):
    def __init__(self, topleft):
        pygame.sprite.Sprite.__init__(self)
        self.image = loadimage('sdot.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        self.is_alive = True
        self.is_big = False

class BigDot(pygame.sprite.Sprite):
    def __init__(self, topleft):
        pygame.sprite.Sprite.__init__(self)
        self.image = loadimage('bdot.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        self.is_alive = True
        self.is_big = True

def quit_hscore():
    global score
    global highscore
    if score > highscore:
        highscore_file = open('highscore.txt', 'wt')
        highscore_file.write(str(score))
        highscore_file.close()
    pygame.quit()
    quit()

def level():
    screen = pygame.Surface((334, 416))
    scaledscreen = pygame.Surface((334 * scale, 416 * scale))
    global display
    global score
    global current_level

    #set the title of the window and the icon
    pygame.display.set_caption('PAC-MAN')
    pygame.display.set_icon(loadimage('icon.png'))

    #set the backgrund image
    backgrund = loadimage('map.png')

    #create groups with the game objects
    global pacmangroup
    pacmangroup = pygame.sprite.RenderUpdates()
    global wallgroup
    wallgroup = pygame.sprite.Group()
    global ghostgroup
    ghostgroup = pygame.sprite.RenderUpdates()
    global smalldotgroup
    smalldotgroup = pygame.sprite.RenderUpdates()
    global textgroup
    textgroup = pygame.sprite.RenderUpdates()

    #initialize the game objects
    global pacman
    pacman = Pacman()
    pacman.add(pacmangroup)

    global walls
    walls = (Wall(0, 0, 334, 16), Wall(0, 16, 16, 128), Wall(16, 128, 48, 16), Wall(64, 128, 16, 48), Wall(0, 160, 64, 16), Wall(0, 192, 64, 16), Wall(64, 192, 16, 48), Wall(0, 224, 64, 16), Wall(0, 240, 16, 144), Wall(16, 288, 32, 16), Wall(16, 368, 318, 16), Wall(320, 16, 16, 128), Wall(256, 128, 64, 16), Wall(256, 144, 16, 32), Wall(272, 160, 62, 16), Wall(256, 192, 78, 16), Wall(256, 208, 16, 32), Wall(272, 224, 62, 16), Wall(320, 240, 14, 128), Wall(288, 288, 32, 16), Wall(160, 16, 16, 48), Wall(32, 32, 48, 32), Wall(96, 32, 48, 32), Wall(32, 80, 48, 32), Wall(192, 32, 48, 32), Wall(256, 32, 48, 32), Wall(256, 80, 48, 32), Wall(96, 80, 16, 96), Wall(112, 112, 32, 16), Wall(128, 80, 80, 16), Wall(160, 96, 16, 32), Wall(224, 80, 16, 96), Wall(192, 112, 32, 16), Wall(128, 144, 80, 64), Wall(96, 192, 16, 48), Wall(224, 192, 16, 48), Wall(128, 224, 80, 16), Wall(160, 240, 16, 32), Wall(32, 256, 48, 16), Wall(64, 272, 16, 32), Wall(96, 256, 48, 16), Wall(192, 256, 48, 16), Wall(256, 256, 48, 16), Wall(256, 272, 16, 32), Wall(128, 288, 80, 16), Wall(160, 304, 16, 48), Wall(96, 288, 16, 32), Wall(32, 320, 112, 32), Wall(224, 288, 16, 32), Wall(192, 320, 112, 32))

    global blinky
    blinky = Blinky()
    blinky.add(ghostgroup)

    global pinky
    pinky = Pinky()
    pinky.add(ghostgroup)

    global inky
    inky = Inky()
    inky.add(ghostgroup)

    global clyde
    clyde = Clyde()
    clyde.add(ghostgroup)

    whitespaces = ((1, 144), (16, 144), (32, 144), (48, 144), (0, 176), (16, 176), (32, 176), (48, 176), (64, 176), (0, 208), (16, 208), (32, 208), (48, 208), (96, 176), (144, 112), (176, 112), (112 , 128 ), (128 , 128 ), (144 , 128 ), (160 , 128 ), (176 , 128 ), (192 , 128 ), (208 , 128 ), (112 , 144 ), (112 , 160 ), (112 , 176 ), (112 , 192 ), (112 , 208 ), (208 , 112 ), (208 , 128 ), (208 , 144 ), (208 , 160 ), (208 , 176 ), (208 , 192 ), (208 , 208 ), (128 , 208 ), (144 , 208 ), (160 , 208 ), (176 , 208 ), (192 , 208 ), (112 , 224 ), (208 , 224 ), (224 , 176 ), (170 , 272 ), (272 , 144 ), (288 , 144 ), (304 , 144 ), (320 , 144 ), (256 , 176 ), (272 , 176 ), (288 , 176 ), (304 , 176 ), (320 , 176 ), (272 , 208 ), (288 , 208 ), (304 , 208 ), (320 , 208 ), (16 , 32 ), (304 , 32 ), (16 , 272 ), (304 , 272 ), (160 , 172 ), (0, 144), (160, 272))
    current_dot_topleft = [0, 0]
    sdots = []
    j = 0
    while True:
        sdots.append(SmallDot(current_dot_topleft))
        if pygame.sprite.spritecollideany(sdots[j], wallgroup) == None and tuple(current_dot_topleft) not in whitespaces:
            sdots[j].add(smalldotgroup)
            j += 1
        else: del sdots[j]
        if current_dot_topleft[0] < screen.get_width() - 16 :
            current_dot_topleft[0] += 16    
        elif current_dot_topleft[0] >= screen.get_width() -16 :
            if current_dot_topleft[1] < screen.get_height() - 48 :
                current_dot_topleft[1] += 16 
                current_dot_topleft[0] = 0
            else:
                break

    bdots = [BigDot((16 , 32 )), BigDot((304 , 32 )), BigDot((16 , 274 )), BigDot((304 , 274 ))]
    for bdot in bdots:
        bdot.add(smalldotgroup)

    score_text = Text('PressStart2P.ttf', 16)
    score_text.add(textgroup)
    highscore_text = Text('PressStart2P.ttf', 16)
    highscore_text.add(textgroup)
    #blit the backgrund on the screen
    screen.blit(backgrund, (0, 0))
    for dot in smalldotgroup:
        screen.blit(dot.image, dot.rect)
    scaledscreen = pygame.transform.scale(screen, (334 * scale, 416 * scale))
    display.blit(scaledscreen, (0, 0))
    pygame.display.update()

    #create a list where the program will put the dirty rects
    dirty_rects = []

    #initialize the clock and create a timer
    clock = pygame.time.Clock()

    global running
    completed = False

    while not completed:
        #set the frame rate
        clock.tick(60)
        
        #show the frame rate
        #pygame.display.set_caption('Pacman però è brutto  {} FPS'.format(int(clock.get_fps())))
            
        #look at the events, if the window is closed, close the program, else if the arrows are pressed change the direction on pacman
        for event in pygame.event.get():
            if event.type == QUIT:
                quit_hscore()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    quit_hscore()
                elif event.key == K_UP:
                    pacman.next_direction = (0, -1)
                elif event.key == K_LEFT:
                    pacman.next_direction = (-1, 0)
                elif event.key == K_DOWN:
                    pacman.next_direction = (0, 1)
                elif event.key == K_RIGHT:
                    pacman.next_direction = (1, 0)
                elif event.key == K_s:
                    pacman.next_direction = (0, 0)
        
        #clear the screen and then draw the objects
        for rect in dirty_rects:
            pygame.draw.rect(screen, (0, 0, 0), rect)
        pacmangroup.update()
        ghostgroup.update()
        score_text.set((334, 400), 'SCORE:{}'.format(score), (255, 255, 255))
        highscore_text.set((334, 416), 'HIGH SCORE:{}'.format(highscore), (255, 255, 255))
        dirty_rects = []
        for dot in smalldotgroup:
            if dot.is_alive == True:
                #if pygame.sprite.spritecollideany(dot, ghostgroup) != None:
                screen.blit(dot.image, dot.rect)
                dirty_rects.append(dot.rect)
        dirty_rects.extend(ghostgroup.draw(screen))
        dirty_rects.extend(pacmangroup.draw(screen))
        dirty_rects.extend(textgroup.draw(screen))
        pygame.draw.rect(screen, (72, 216, 247), pygame.Rect((142, 150), (48, 2)))
        pygame.draw.rect(screen, (72, 216, 247), pygame.Rect((142, 154), (48, 2)))

        #These should draw the targets of the ghosts but the .get_target function doesn't always work
        #pygame.draw.circle(screen, (100, 0, 0), blinky.get_target(), 9, 3)
        #pygame.draw.circle(screen, (100, 60, 80), pinky.get_target().center, 9, 3)
        #pygame.draw.circle(screen, (20, 100, 100), inky.get_target(), 9, 3)
        #pygame.draw.circle(screen, (100, 80, 20), clyde.get_target(), 12, 2)

        pygame.transform.scale(screen, (334 * scale, 416 * scale), display)
        scaled_dirty_rects = []
        for rect in dirty_rects:
            scal_rect = copy.deepcopy(rect)
            scal_rect.x *= scale
            scal_rect.y *= scale
            scal_rect.w *= scale
            scal_rect.h *= scale
            scal_rect.inflate(int(2 * scale), int(2 * scale))
            scaled_dirty_rects.append(scal_rect)
        pygame.display.update(scaled_dirty_rects)
        #pygame.display.update()
        if pacman.sdots_eaten >= 178:
            completed = True

def only_text_screen(message, sound=False):
    if sound:
        beginning_sound.play()
    screen = pygame.Surface((334, 416))
    screen.fill((0, 0, 0))
    text = Text('PressStart2P.ttf', 24)
    text.set((0, 0), message, (255, 255, 255))
    text.rect.center = (167, 208)
    screen.blit(text.image, text.rect)
    pygame.transform.scale(screen, (334 * scale, 416 * scale), display)
    pygame.display.update()
    pygame.time.wait(4000)

def menu():
    pass
 
def loadsounds():
    global beginning_sound
    beginning_sound = getsound('beginning.wav')
    global sdot_sound
    sdot_sound = getsound('chomp.wav')
    global death_sound
    death_sound = getsound('death.wav')
    global eatghost_sound
    eatghost_sound = getsound('eatghost.wav')
    global bdot_sound
    bdot_sound = getsound('extrapac.wav')

def main():
    #define the scale of the display
    global scale
    scale = 2

    #initialize pygame and the display
    pygame.init()
    global display
    display = pygame.display.set_mode((334 * scale, 416 * scale))

    global score
    score = 0

    global highscore
    highscorefile = open('highscore.txt', 'rt')
    highscore = int(highscorefile.read())
    highscorefile.close()

    global current_level 
    current_level = 1
    
    loadsounds()
    while 1:
        only_text_screen('LEVEL {}'.format(current_level), 1)
        level()
        current_level += 1

main()
quit_hscore()