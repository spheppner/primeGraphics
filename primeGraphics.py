"""
author: Simon HEPPNER
website: github.com/spheppner/primeGraphics
email: simon@heppner.at
name of game: primeGraphics
"""
import pygame
#import math
import random
import os
import time
#import operator
import math
import primeFinder
#import vectorclass2d as v
#import textscroller_vertical as ts
#import subprocess

def randomize_color(color, delta=50):
    d=random.randint(-delta, delta)
    color = color + d
    color = min(255,color)
    color = max(0, color)
    return color

def make_text(msg="pygame is cool", fontcolor=(255, 0, 255), fontsize=42, font=None):
    """returns pygame surface with text. You still need to blit the surface."""
    myfont = pygame.font.SysFont(font, fontsize)
    mytext = myfont.render(msg, True, fontcolor)
    mytext = mytext.convert_alpha()
    return mytext

def write(background, text, x=50, y=150, color=(0,0,0),
          fontsize=None, center=False):
        """write text on pygame surface. """
        if fontsize is None:
            fontsize = 24
        font = pygame.font.SysFont('mono', fontsize, bold=True)
        fw, fh = font.size(text)
        surface = font.render(text, True, color)
        if center: # center text around x,y
            background.blit(surface, (x-fw//2, y-fh//2))
        else:      # topleft corner is x,y
            background.blit(surface, (x,y))

def elastic_collision(sprite1, sprite2):
        """elasitc collision between 2 VectorSprites (calculated as disc's).
           The function alters the dx and dy movement vectors of both sprites.
           The sprites need the property .mass, .radius, pos.x pos.y, move.x, move.y
           by Leonard Michlmayr"""
        if sprite1.static and sprite2.static:
            return
        dirx = sprite1.pos.x - sprite2.pos.x
        diry = sprite1.pos.y - sprite2.pos.y
        sumofmasses = sprite1.mass + sprite2.mass
        sx = (sprite1.move.x * sprite1.mass + sprite2.move.x * sprite2.mass) / sumofmasses
        sy = (sprite1.move.y * sprite1.mass + sprite2.move.y * sprite2.mass) / sumofmasses
        bdxs = sprite2.move.x - sx
        bdys = sprite2.move.y - sy
        cbdxs = sprite1.move.x - sx
        cbdys = sprite1.move.y - sy
        distancesquare = dirx * dirx + diry * diry
        if distancesquare == 0:
            dirx = random.randint(0,11) - 5.5
            diry = random.randint(0,11) - 5.5
            distancesquare = dirx * dirx + diry * diry
        dp = (bdxs * dirx + bdys * diry) # scalar product
        dp /= distancesquare # divide by distance * distance.
        cdp = (cbdxs * dirx + cbdys * diry)
        cdp /= distancesquare
        if dp > 0:
            if not sprite2.static:
                sprite2.move.x -= 2 * dirx * dp
                sprite2.move.y -= 2 * diry * dp
            if not sprite1.static:
                sprite1.move.x -= 2 * dirx * cdp
                sprite1.move.y -= 2 * diry * cdp

class Flytext(pygame.sprite.Sprite):
    def __init__(self, x, y, text="hallo", color=(255, 0, 0),
                 dx=0, dy=-50, duration=2, acceleration_factor = 1.0, delay = 0, fontsize=22):
        """a text flying upward and for a short time and disappearing"""
        self._layer = 57  # order of sprite layers (before / behind other sprites)
        pygame.sprite.Sprite.__init__(self, self.groups)  # THIS LINE IS IMPORTANT !!
        self.text = text
        self.r, self.g, self.b = color[0], color[1], color[2]
        self.dx = dx
        self.dy = dy
        self.x, self.y = x, y
        self.duration = duration  # duration of flight in seconds
        self.acc = acceleration_factor  # if < 1, Text moves slower. if > 1, text moves faster.
        self.image = make_text(self.text, (self.r, self.g, self.b), fontsize)  # font 22
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.time = 0 - delay

    def update(self, seconds):
        self.time += seconds
        if self.time < 0:
            self.rect.center = (-100,-100)
        else:
            self.y += self.dy * seconds
            self.x += self.dx * seconds
            self.dy *= self.acc  # slower and slower
            self.dx *= self.acc
            self.rect.center = (self.x, self.y)
            if self.time > self.duration:
                self.kill()      # remove Sprite from screen and from groups

class VectorSprite(pygame.sprite.Sprite):
    """base class for sprites. this class inherits from pygames sprite class"""
    number = 0
    numbers = {} # { number, Sprite }

    def __init__(self, **kwargs):
        self._default_parameters(**kwargs)
        self._overwrite_parameters()
        pygame.sprite.Sprite.__init__(self, self.groups) #call parent class. NEVER FORGET !
        self.number = VectorSprite.number # unique number for each sprite
        VectorSprite.number += 1
        VectorSprite.numbers[self.number] = self
        self.create_image()
        self.distance_traveled = 0 # in pixel
        #self.rect.center = (-300,-300) # avoid blinking image in topleft corner
        self.rect.center = (int(self.pos.x), -int(self.pos.y))
        
        if self.angle != 0:
            self.set_angle(self.angle)

    def _overwrite_parameters(self):
        """change parameters before create_image is called"""
        pass

    def _default_parameters(self, **kwargs):
        """get unlimited named arguments and turn them into attributes
           default values for missing keywords"""

        for key, arg in kwargs.items():
            setattr(self, key, arg)
        if "layer" not in kwargs:
            self._layer = 4
        else:
            self._layer = self.layer
        if "static" not in kwargs:
            self.static = False
        if "pos" not in kwargs:
            self.pos = pygame.math.Vector2(random.randint(0, Viewer.width),-50)
        if "move" not in kwargs:
            self.move = pygame.math.Vector2(0,0)
        if "radius" not in kwargs:
            self.radius = 5
        if "width" not in kwargs:
            self.width = self.radius * 2
        if "height" not in kwargs:
            self.height = self.radius * 2
        if "color" not in kwargs:
            #self.color = None
            self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        if "hitpoints" not in kwargs:
            self.hitpoints = 100
        self.hitpointsfull = self.hitpoints # makes a copy
        if "mass" not in kwargs:
            self.mass = 10
        if "damage" not in kwargs:
            self.damage = 10
        if "bounce_on_edge" not in kwargs:
            self.bounce_on_edge = False
        if "kill_on_edge" not in kwargs:
            self.kill_on_edge = False
        if "angle" not in kwargs:
            self.angle = 0 # facing right?
        if "max_age" not in kwargs:
            self.max_age = None
        if "max_distance" not in kwargs:
            self.max_distance = None
        if "picture" not in kwargs:
            self.picture = None
        if "bossnumber" not in kwargs:
            self.bossnumber = None
        if "kill_with_boss" not in kwargs:
            self.kill_with_boss = False
        if "sticky_with_boss" not in kwargs:
            self.sticky_with_boss = False
        if "mass" not in kwargs:
            self.mass = 15
        if "upkey" not in kwargs:
            self.upkey = None
        if "downkey" not in kwargs:
            self.downkey = None
        if "rightkey" not in kwargs:
            self.rightkey = None
        if "leftkey" not in kwargs:
            self.leftkey = None
        if "speed" not in kwargs:
            self.speed = None
        if "age" not in kwargs:
            self.age = 0 # age in seconds
        if "warp_on_edge" not in kwargs:
            self.warp_on_edge = False

    def kill(self):
        if self.number in self.numbers:
           del VectorSprite.numbers[self.number] # remove Sprite from numbers dict
        pygame.sprite.Sprite.kill(self)

    def create_image(self):
        if self.picture is not None:
            self.image = self.picture.copy()
        else:
            self.image = pygame.Surface((self.width,self.height))
            self.image.fill((self.color))
        self.image = self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect= self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height

    def rotate(self, by_degree):
        """rotates a sprite and changes it's angle by by_degree"""
        self.angle += by_degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def set_angle(self, degree):
        """rotates a sprite and changes it's angle to degree"""
        self.angle = degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def update(self, seconds):
        """calculate movement, position and bouncing on edge"""
        # ----- kill because... ------
        if self.hitpoints <= 0:
            self.kill()
        if self.max_age is not None and self.age > self.max_age:
            self.kill()
        if self.max_distance is not None and self.distance_traveled > self.max_distance:
            self.kill()
        # ---- movement with/without boss ----
        if self.bossnumber is not None:
            if self.kill_with_boss:
                if self.bossnumber not in VectorSprite.numbers:
                    self.kill()
            if self.sticky_with_boss:
                boss = VectorSprite.numbers[self.bossnumber]
                #self.pos = pygame.math.Vector2(boss.pos.x, boss.pos.y)
                self.pos = pygame.math.Vector2(boss.pos.x, boss.pos.y)
        self.pos += self.move * seconds
        self.distance_traveled += self.move.length() * seconds
        self.age += seconds
        self.rect.center = ( round(self.pos.x, 0), -round(self.pos.y, 0) )

class Player(VectorSprite):

    def _overwrite_parameters(self):
        self._layer = 50
        self.hitpoints = 50
        self.max_hitpoints = 50
        self.endurance = 100
        self.max_endurance = 100
        self.coins = 25
        self.multiplicant = 3
        self.character = "@"
        self.inventory = []

    def create_image(self):
        self.fontsize = 32
        self.color = (255, 0, 255)
        self.text = self.character
        self.image = make_text(self.text, self.color, self.fontsize)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

class Grid(VectorSprite):

    def _overwrite_parameters(self):
        self._layer = -10

    def create_image(self):
        self.image = pygame.Surface((15, 15))
        pygame.draw.rect(self.image, (215,215,215), (0,0, 14,14),1)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()

class Wall(VectorSprite):
    
    def __init__(self, **kwargs):
        VectorSprite.__init__(self, **kwargs)
        self.color_wall = kwargs
    
    def _overwrite_parameters(self):
        self._layer = 5000000000

    def create_image(self):
        self.image = pygame.Surface((15, 15))
        self.image.fill(self.color_wall)
        pygame.draw.rect(self.image, (255,0,255), (0,0, 14,14),1)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()

class Explosion():

    def __init__(self, pos, maxspeed=150, minspeed=20, color=(255,255,0),maxduration=2.5,gravityy=3.7,sparksmin=5,sparksmax=20, a1=0,a2=360):

        for s in range(random.randint(sparksmin,sparksmax)):
            v = pygame.math.Vector2(1,0) # vector aiming right (0°)
            a = random.triangular(a1,a2)
            v.rotate_ip(a)
            g = pygame.math.Vector2(0, - gravityy)
            speed = random.randint(minspeed, maxspeed)     #150
            duration = random.random() * maxduration
            Spark(pos=pygame.math.Vector2(pos.x, pos.y), angle=a, move=v*speed,
                  max_age = duration, color=color, gravity = g)

class Spark(VectorSprite):

    def __init__(self, **kwargs):
        VectorSprite.__init__(self, **kwargs)
        if "gravity" not in kwargs:
            self.gravity = pygame.math.Vector2(0, -3.7)

    def _overwrite_parameters(self):
        self._layer = 10000000
        self.kill_on_edge = True

    def create_image(self):
        r,g,b = self.color
        r = randomize_color(r,75)    #50
        g = randomize_color(g,75)
        b = randomize_color(b,75)
        self.image = pygame.Surface((10,10))
        pygame.draw.line(self.image, (r,g,b),
                         (10,5), (5,5), 3)
        pygame.draw.line(self.image, (r,g,b),
                          (5,5), (2,5), 1)
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.image0 = self.image.copy()

    def update(self, seconds):
        VectorSprite.update(self, seconds)
        self.move += self.gravity

class Rocket(VectorSprite):
    
    def _overwrite_parameters(self):
        self._layer = 10000000000000000000
        # start?
        self.move = pygame.math.Vector2(Viewer.width // 2, Viewer.height // 2)
        self.move.normalize_ip()
        self.move *= 100 # speed
        if random.random() < 0.5:
            self.angle = 45
            x = 0
        else:
            x = Viewer.width
            self.move.x *= -1
            self.angle = 135
        self.pos = pygame.math.Vector2(x, -Viewer.height)
        self.max_distance = ((Viewer.width/2) ** 2 + (Viewer.height/2) ** 2 )**0.5
        
    def update(self, seconds):
        if self.distance_traveled > self.max_distance:
            Explosion(pos=pygame.math.Vector2(self.pos.x, self.pos.y))
        VectorSprite.update(self, seconds)
        
    
    def create_image(self):
        self.image = pygame.Surface((20, 10))
        self.image.fill((255, 255, 0))
        #pygame.draw.rect(self.image, (255,0,255), (0,0, 19,19),1)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

        
    
class Viewer(object):
    width = 0
    height = 0
    menuitems = ["Paint", "Quit"]
    cursorindex = 0
    shakescreen = False

    def __init__(self, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
           default arguments """
        pygame.init()
        Viewer.width = width    # make global readable
        Viewer.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((255,255,255)) # fill background white
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("primeGraphics | Press ESC to exit")
        self.fps = fps
        self.playtime = 0.0
        self.max_color_value = 10
        self.max_color_value2 = 10
        self.max_color_value3 = 10
        self.max_position_value = 10
        self.max_position_value2 = 10
        self.max_position_value3 = 10
        self.color_value = 0
        self.color_value2 = 0
        self.color_value3 = 0
        self.position_value = 0
        self.position_value2 = 0
        self.position_value3 = 0
        
        #self.color_init_wall = (self.color_value*100+5*self.color_value2)
        self.color_value_wall = ((25*self.color_value3),(25*self.color_value2),(25*self.color_value))
        
        self.position_tf = False
        #self.dig_sound = pygame.mixer.Sound("dig.wav")
        #self.hit_sound = pygame.mixer.Sound("Hit_Hurt.wav")
        #self.walk_sound = pygame.mixer.Sound("walk.wav")
        #self.pickup_sound = pygame.mixer.Sound("Pickup_Coin.wav")
        #self.new_level_sound = pygame.mixer.Sound("new_level.wav")
        # ------ background images ------
        #self.backgroundfilenames = [] # every .jpg file in folder 'data'
        #try:
        #    for root, dirs, files in os.walk("data"):
        #        for file in files:
        #            if file[-4:] == ".jpg" or file[-5:] == ".jpeg":
        #                self.backgroundfilenames.append(file)
        #    random.shuffle(self.backgroundfilenames) # remix sort order
        #except:
        #    print("no folder 'data' or no jpg files in it")
        #if len(self.backgroundfilenames) == 0:
        #    print("Error: no .jpg files found")
        #    pygame.quit
        #    sys.exit()
        Viewer.bombchance = 0.015
        Viewer.rocketchance = 0.001
        Viewer.wave = 0
        self.age = 0
        # ------ joysticks ----
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
        self.paint()
        self.loadbackground()
        self.load()
        self.menu_visited = False
        primeFinder.start("prime",0)

    def load(self):
        
        self.color_value_wall = ((25*self.color_value3),(25*self.color_value2),(25*self.color_value))
        
        for x in self.tilegroup:
            #print(x,"killed")
            x.kill()
        
        with open("primes.txt", "r") as f:
            self.lines = f.readlines()
        
        for y, line in enumerate(self.lines):
            for x, char in enumerate(line):
                if x < len(line)-1:
                    p = pygame.math.Vector2(x * 15+7, -y*15+8)
                    Grid(pos=p)
                if char == "#":
                    p = pygame.math.Vector2(x * 15+7, -y*15+8)
                    Wall(pos=p, color_wall=self.color_value_wall)
                #elif char == "@":
                #    if self.shopActive is True:
                #        p = pygame.math.Vector2(x * 20+10, -y*20-10)
                #        self.player.pos = p
                #    else:
                #        with open("shop_pos.txt", "r") as f:
                #            player_pos = f.readlines()[0]
                #        if player_pos != "a\n":
                #            player_pos_splitted = player_pos.split(",")
                #            p = pygame.math.Vector2(float(player_pos_splitted[0]), -float(player_pos_splitted[1]))
                #            self.player.pos.x = float(player_pos_splitted[0])
                #            self.player.pos.y = float(player_pos_splitted[1])
                #        else:
                #            p = pygame.math.Vector2(x * 20+10, -y*20-10)
                #            self.player.pos = p

    def loadbackground(self):

        try:
            self.background = pygame.image.load(os.path.join("data",
                 self.backgroundfilenames[Viewer.wave %
                 len(self.backgroundfilenames)]))
        except:
            self.background = pygame.Surface(self.screen.get_size()).convert()
            self.background.fill((255,255,255)) # fill background white

        self.background = pygame.transform.scale(self.background,
                          (Viewer.width,Viewer.height))
        self.background.convert()


    def paint(self):
        """painting on the surface and create sprites"""
        self.allgroup =  pygame.sprite.LayeredUpdates() # for drawing
        self.explosiongroup = pygame.sprite.Group()
        self.tilegroup = pygame.sprite.Group()
        self.wallgroup = pygame.sprite.Group()
        #self.playergroup = pygame.sprite.Group()
        self.floorgroup = pygame.sprite.Group()
        self.flytextgroup = pygame.sprite.Group()
        
        VectorSprite.groups = self.allgroup
        Flytext.groups = self.allgroup, self.flytextgroup
        Explosion.groups= self.allgroup, self.explosiongroup
        Wall.groups = self.allgroup, self.tilegroup, self.wallgroup
        #Player.groups = self.allgroup, self.playergroup
        Grid.groups = self.allgroup, self.tilegroup, self.floorgroup

        #self.player = Player(pos = pygame.math.Vector2(100,-100))
        #Flytext(Viewer.width/2, Viewer.height/2,  "@", color=(255,0,0), duration = 3, fontsize=20)
    
    def menurun(self):
        running = True
        while running:
            
            pressed_keys = pygame.key.get_pressed()
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_UP:
                        Viewer.cursorindex -= 1
                        if Viewer.cursorindex <= 0:
                            Viewer.cursorindex = 0
                    if event.key == pygame.K_DOWN:
                        Viewer.cursorindex += 1
                        if Viewer.cursorindex >= len(Viewer.menuitems):
                            Viewer.cursorindex = len(Viewer.menuitems)-1
                    if event.key == pygame.K_RETURN:
                        activeitem = Viewer.menuitems[Viewer.cursorindex]
                        if activeitem == "Paint":
                            return
                        elif activeitem == "Quit":
                            pygame.quit()
                            
            # delete everything on screen
            self.screen.blit(self.background, (0, 0))
            self.flytextgroup.update(seconds)
            
            # draw menuitems
            for y, i in enumerate(Viewer.menuitems):
                write(self.screen, i, 1280, 100+y*20, color=(0,0,200))
            # draw cursor
            write(self.screen, "-->", 1225, 100+Viewer.cursorindex*20, color=(0,0,random.randint(200,255)))
                
            
            # --------- collision detection between target and Explosion -----
            #for e in self.explosiongroup:
            #    crashgroup = pygame.sprite.spritecollide(e, self.targetgroup,
            #                 False, pygame.sprite.collide_circle)
            #    for t in crashgroup:
            #        t.hitpoints -= e.damage
            #        if random.random() < 0.5:
            #            Fire(pos = t.pos, max_age=3, bossnumber=t.number)


            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)

            # -------- next frame -------------
            pygame.display.flip()
        ### battle over ####
        return 0
        
        
    def run(self):
        """The mainloop"""
        running = True
        leftcorner = pygame.math.Vector2(0,self.height)
        rightcorner = pygame.math.Vector2(self.width,self.height)
        pygame.mouse.set_visible(False)
        oldleft, oldmiddle, oldright  = False, False, False
        gameOver = False
        exittime = 0
        if not self.menu_visited:
            self.menurun()
        while running:
            #print(pygame.key.get_mods())
            pressed_keys = pygame.key.get_pressed()
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            self.playtime += seconds
            if gameOver:
                if self.playtime > exittime:
                    break
            #Game over?
            #if not gameOver:
            # -------- events ------
            #self.player.move = pygame.math.Vector2(0,0) # rumstehen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    
                    if event.key == pygame.K_UP:
                        Viewer.cursorindex -= 1
                        if Viewer.cursorindex <= 0:
                            Viewer.cursorindex = 0
                    if event.key == pygame.K_DOWN:
                        Viewer.cursorindex += 1
                        if Viewer.cursorindex >= 8:
                            Viewer.cursorindex = 0
                    if event.key == pygame.K_RIGHT:
                        activeitem = Viewer.cursorindex
                        if activeitem == 0:
                            if self.color_value < self.max_color_value:
                                self.color_value += 1
                            if self.color_value > self.max_color_value:
                                self.color_value = 0
                        elif activeitem == 1:
                            if self.color_value2 < self.max_color_value2:
                                self.color_value2 += 1
                            if self.color_value2 > self.max_color_value2:
                                self.color_value2 = 0
                        elif activeitem == 2:
                            if self.color_value3 < self.max_color_value3:
                                self.color_value3 += 1
                            if self.color_value3 > self.max_color_value3:
                                self.color_value3 = 0  
                        elif activeitem == 3:
                            if self.position_value < self.max_position_value:
                                self.position_value += 1
                            if self.position_value > self.max_position_value:
                                self.position_value = 0
                        elif activeitem == 4:
                            if self.position_value2 < self.max_position_value2:
                                self.position_value2 += 1
                            if self.position_value2 > self.max_position_value2:
                                self.position_value2 = 0
                        elif activeitem == 5:
                            if self.position_value3 < self.max_position_value3:
                                self.position_value3 += 1
                            if self.position_value3 > self.max_position_value3:
                                self.position_value3 = 0
                        elif activeitem == 6:
                            if self.color_value > 0 or self.color_value2 > 0 or self.color_value3 > 0 or self.position_value > 0 or self.position_value2 > 0 or self.position_value3 > 0:
                                if self.position_value > 0:
                                    primeFinder.start("position",self.position_value)
                                if self.position_value2 > 0:
                                    primeFinder.start("position2",self.position_value,self.position_value2)
                                if self.position_value3 > 0:
                                    primeFinder.start("position3",self.position_value,self.position_value2,self.position_value3)
                                self.load()
                        elif activeitem == 7:
                            with open("save.txt", "a") as save:
                                #x = save.readlines()
                                y = ["#",str(self.color_value),str(self.color_value2),str(self.color_value3),str(self.position_value),str(self.position_value2),str(self.position_value3)]
                                for z in y:
                                    save.write(z)
                                for x in y:
                                    if x == "10":
                                        save.write(",z")
                                save.write("\n")
                                
                                                                  
                            #if self.color_value > 0:
                            #    self.load()
                            #if self.color_value2 > 0:
                            #    self.load()
                            #if self.position_value > 0:
                            #    primeFinder.start("position",self.position_value)
                            #    self.load()
                            #if self.position_value2 > 0:
                            #    primeFinder.start("position2",self.position_value,self.position_value2)
                            #    self.load()
                            #if self.position_value3 > 0:
                            #    pass
                            
                    if event.key == pygame.K_LEFT:
                        activeitem = Viewer.cursorindex
                        if activeitem == 0:
                            if self.color_value > 0:
                                self.color_value -= 1
                            if self.color_value < 0:
                                self.color_value = 0
                        elif activeitem == 1:
                            if self.color_value2 > 0:
                                self.color_value2 -= 1
                            if self.color_value2 < 0:
                                self.color_value2 = 0
                        elif activeitem == 2:
                            if self.color_value3 > 0:
                                self.color_value3 -= 1
                            if self.color_value3 < 0:
                                self.color_value3 = 0
                        elif activeitem == 3:
                            if self.position_value > 0:
                                self.position_value -= 1
                            if self.position_value < 0:
                                self.position_value = 0
                        elif activeitem == 4:
                            if self.position_value2 > 0:
                                self.position_value2 -= 1
                            if self.position_value2 < 0:
                                self.position_value2 = 0
                        elif activeitem == 5:
                            if self.position_value3 > 0:
                                self.position_value3 -= 1
                            if self.position_value3 < 0:
                                self.position_value3 = 0
                                
                    if event.key == pygame.K_m:
                        self.menurun()
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    #=============================================
            # delete everything on screen
            self.screen.blit(self.background, (0, 0))
            
            value_color_graphic = self.color_value / ( self.max_color_value / 100)
            value_color2_graphic = self.color_value2 / ( self.max_color_value2 / 100 )
            value_color3_graphic = self.color_value3 / ( self.max_color_value3 / 100 )
            value_position_graphic = self.position_value / ( self.max_position_value / 100)
            value_position2_graphic = self.position_value2 / ( self.max_position_value2 / 100)
            value_position3_graphic = self.position_value3 / ( self.max_position_value3 / 100)
            
            equipped_color2 = (233, 111, 233)
            equipped_color = (0,220,220)
            
            # ganzes kasterl
            pygame.draw.rect(self.screen, (65, 220, 65), (Viewer.width-230, 0, 230, Viewer.height))
            # oberes hp kasterl
            if Viewer.cursorindex == 0:
                pygame.draw.rect(self.screen, equipped_color, (Viewer.width-215, 20, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 75, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 130, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 185, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 240, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 295, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 350, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 405, 200, 30), 10)
                
            elif Viewer.cursorindex == 1:
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 20, 200, 30), 10)
                pygame.draw.rect(self.screen, equipped_color, (Viewer.width-215, 75, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 130, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 185, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 240, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 295, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 350, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 405, 200, 30), 10)
                
            elif Viewer.cursorindex == 2:
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 20, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 75, 200, 30), 10)
                pygame.draw.rect(self.screen, equipped_color, (Viewer.width-215, 130, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 185, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 240, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 295, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 350, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 405, 200, 30), 10)
                
            elif Viewer.cursorindex == 3:
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 20, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 75, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 130, 200, 30), 10)
                pygame.draw.rect(self.screen, equipped_color, (Viewer.width-215, 185, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 240, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 295, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 350, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 405, 200, 30), 10)
            
            elif Viewer.cursorindex == 4:
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 20, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 75, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 130, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 185, 200, 30), 10)
                pygame.draw.rect(self.screen, equipped_color, (Viewer.width-215, 240, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 295, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 350, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 405, 200, 30), 10)
                
            elif Viewer.cursorindex == 5:
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 20, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 75, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 130, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 185, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 240, 200, 30), 10)
                pygame.draw.rect(self.screen, equipped_color, (Viewer.width-215, 295, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 350, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 405, 200, 30), 10)
                
            elif Viewer.cursorindex == 6:
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 20, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 75, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 130, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 185, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 240, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 295, 200, 30), 10)
                pygame.draw.rect(self.screen, equipped_color, (Viewer.width-215, 350, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 405, 200, 30), 10)
                
            elif Viewer.cursorindex == 7:
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 20, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 75, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 130, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 185, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 240, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 295, 200, 30), 10)
                pygame.draw.rect(self.screen, (133, 11, 133), (Viewer.width-215, 350, 200, 30), 10)
                pygame.draw.rect(self.screen, equipped_color, (Viewer.width-215, 405, 200, 30), 10)
                
            if self.color_value > 0:
                pygame.draw.rect(self.screen, (220, 145, 220), (Viewer.width-215, 26, int(value_color_graphic*2), 19))
            
            if self.color_value2 > 0:
                pygame.draw.rect(self.screen, (220, 145, 220), (Viewer.width-215, 81, int(value_color2_graphic*2), 19))
            
            if self.color_value3 > 0:
                pygame.draw.rect(self.screen, (220, 145, 220), (Viewer.width-215, 136, int(value_color3_graphic*2), 19))
            
            if self.position_value > 0:
                pygame.draw.rect(self.screen, (0, 0, 220), (Viewer.width-215, 191, int(value_position_graphic*2), 19))
            
            if self.position_value2 > 0:
                pygame.draw.rect(self.screen, (0, 0, 220), (Viewer.width-215, 246, int(value_position2_graphic*2), 19))
                
            if self.position_value3 > 0:
                pygame.draw.rect(self.screen, (0, 0, 220), (Viewer.width-215, 301, int(value_position3_graphic*2), 19))
            
            
            write(self.screen, "O.K.", 1315, 367, (220, 11, 133), 20, True)
            write(self.screen, "Save", 1315, 422, (220, 11, 133), 20, True)
            
            write(self.screen, "FPS: {:6.3}".format(self.clock.get_fps()), 1315, 550, (255, 0, 0), 20, True)
      
            #self.allgroup.update(seconds)

            # --------- collision detection between target and Explosion -----
            #for e in self.explosiongroup:
            #    crashgroup = pygame.sprite.spritecollide(e, self.targetgroup,
            #                 False, pygame.sprite.collide_circle)
            #    for t in crashgroup:
            #        t.hitpoints -= e.damage
            #        if random.random() < 0.5:
            #            Fire(pos = t.pos, max_age=3, bossnumber=t.number)


            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)
            
            if Viewer.shakescreen:
                gameOver = True
                print("exittime", exittime) 
                if exittime == 0:
                    exittime = self.playtime + 1.1
                #if random.random < 0.1:
                #    Viewer.shakescreen = True
                #else:
                #    Viewer.shakescreen = False
                self.shakerscreen = self.screen.copy()
                self.screen.blit(self.shakerscreen, random.choice(((1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10))))
                
            
            
            # -------- next frame -------------
            pygame.display.flip()
        #-----------------------------------------------------
        pygame.mouse.set_visible(True)
        pygame.quit()
    
if __name__ == '__main__':
    Viewer(1430,800).run() # try Viewer(800,600).run()
