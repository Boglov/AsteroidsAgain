import math
import pygame
import time
import random


from datetime import datetime
from pygame.locals import *

exitGame = False

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Initialization
pygame.init()
FPS = 60
DISPLAY_WIDTH = 1024 
DISPLAY_HEIGHT = 768
DISPLAY_CENTER = pygame.Vector2(DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2)

FramePerSec = pygame.time.Clock()
gameSurface = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption("Asteroids Again")

font1 = pygame.font.Font('freesansbold.ttf', 32)
scoreText = font1.render('Score: ', True, WHITE, BLACK)
textRect = scoreText.get_rect()
textRect.center = (200, 20)

gameSurface.fill(BLACK)

worldSpace = pygame.Vector2()
bgSpace = pygame.Vector2()
farBgSpace = pygame.Vector2()
staticBgSpace = pygame.Vector2()

        
class Starfield():
    def __init__(self, minSize = 1, maxSize = 3):
        self.starCount = 200
        self.stars = []
        self.sizes = []

        for s in range(0, self.starCount):
        
            self.stars.append(pygame.Vector2((random.randint(-1000, 1000), random.randint(-1000, 1000))))
            self.sizes.append(random.randint(minSize, maxSize))

    def Draw(self):
        for a in range(0, self.starCount):
            nPos = self.stars[a] + bgSpace
            pygame.draw.circle(gameSurface, WHITE, (int(nPos.x), int(nPos.y)), self.sizes[a])
            
    def DrawFar(self):
        for a in range(0, self.starCount):
            nPos = self.stars[a] + farBgSpace
            pygame.draw.circle(gameSurface, WHITE, (int(nPos.x), int(nPos.y)), self.sizes[a])
            
    def DrawStatic(self):
        for a in range(0, self.starCount):
            nPos = self.stars[a] + staticBgSpace
            pygame.draw.circle(gameSurface, WHITE, (int(nPos.x), int(nPos.y)), self.sizes[a])

class Bullet():
    def __init__(self):
        self.pos = pygame.Vector2()
        self.vel = pygame.Vector2()
        self.angle = 0
        self.active = False
        self.speed = 15
        self.clr = RED

    def Update(self):
        if self.active:
            self.vel.x = self.speed * math.cos(self.angle)
            self.vel.y = self.speed * math.sin(self.angle)
            self.pos += self.vel

    def Draw(self):
        if self.active:
            p1 = pygame.Vector2()
            p2 = pygame.Vector2()

            p1.xy = (self.pos.x, self.pos.y)
            p2.xy = (self.pos.x + 8*math.cos(self.angle), self.pos.y + 8*math.sin(self.angle))

            pygame.draw.line(gameSurface, self.clr, (int(p1.x), int(p1.y)), (int(p2.x), int(p2.y)))

    def Fire(self, ox, oy, direction):
        self.pos.xy = (ox, oy)
        self.angle = direction
        self.active = True


class Asteroid():
    maxSides = 20
    minSides = 6
    def __init__(self, minS=minSides, maxS=maxSides, minR=30, maxR=40):
        self.pos = pygame.Vector2()
        self.vel = pygame.Vector2()
        self.point = []
        self.lens = []
        self.sides = random.randint(self.minSides, self.maxSides)
        self.angle = 45
        self.minRadius = 30
        self.maxRadius = 40
        theta = 2.0*math.pi/self.sides
        random.seed(datetime.now())
        
        
        
        for p in range(0, self.sides):
            rVar = random.randint(self.minRadius, self.maxRadius)
            px = (rVar * math.cos(self.angle+theta*p) + self.pos.x+worldSpace.x)
            py = (rVar * math.sin(self.angle+theta*p) + self.pos.y+worldSpace.y)
            self.lens.append(rVar)
            self.point.append((px, py))
        
    def Update(self):
        self.pos += self.vel
        
        theta = 2.0*math.pi/self.sides
        random.seed(datetime.now())
        self.angle += .006
        
        for p in range(0, self.sides):
            px = (self.lens[p] * math.cos(self.angle+theta*p) + self.pos.x+worldSpace.x)
            py = (self.lens[p] * math.sin(self.angle+theta*p) + self.pos.y+worldSpace.y)
            self.point[p] = (px, py)

    def Draw(self):
        for i in range(0, self.sides-1):
            newInt = pygame.Vector2(self.point[i])
            pygame.draw.line(gameSurface, WHITE, (round(newInt.x), round(newInt.y)), (int(self.point[i+1][0]), int(int(self.point[i+1][1]))))
        pygame.draw.line(gameSurface, WHITE, (int(self.point[self.sides-1][0]), int(self.point[self.sides-1][1])), (int(self.point[0][0]), int(self.point[0][1])))

    def SetPos(self, pX, pY):
        self.pos.xy = (pX, pY)


class Entity():
    bulletPoolSize = 100
    bullets = []

    def __init__(self):
        self.pos = pygame.Vector2()
        self.vel = pygame.Vector2()
        self.r = 15
        self.angle = 0
        self.innerAngle = 90
        self.speed = .6
        self.turnSpeed = .07

        self.point = []
        self.point.append((self.pos.x+self.r*math.cos(self.angle), self.pos.y+self.r*math.sin(self.angle)))
        self.point.append((self.pos.x+self.r*math.cos(self.angle-self.innerAngle), self.pos.y+self.r*math.sin(self.angle-self.innerAngle)))
        self.point.append((self.pos.x+self.r*math.cos(self.angle+self.innerAngle), self.pos.y+self.r*math.sin(self.angle+self.innerAngle)))

        self.pos.xy = DISPLAY_CENTER
        self.vel.xy = (0, 0)
        self.innerAngle = 90
        self.bIndex = 0

        for b in range(0, self.bulletPoolSize):
            self.bullets.append(Bullet())

    def Fire(self):
        if self.bIndex >= self.bulletPoolSize:
            self.bIndex = 0
        self.bullets[self.bIndex].Fire(self.point[0][0], self.point[0][1], self.angle)
        self.bIndex+=1

    def HandleInput(self):
        global exitGame
        for event in pygame.event.get():
            if event.type == QUIT:
                exitGame = True


        keys=pygame.key.get_pressed()
        
        if keys[K_ESCAPE]:
            exitGame = True
        if keys[K_UP] or keys[K_w]:
            player.vel.x += player.speed*math.cos(player.angle)
            player.vel.y += player.speed*math.sin(player.angle)

        if keys[K_DOWN] or keys[K_s]:
            player.vel.x -= player.speed*math.cos(player.angle)
            player.vel.y -= player.speed*math.sin(player.angle)

        if keys[K_LEFT] or keys[K_a]:
            player.angle -= player.turnSpeed

        if keys[K_RIGHT] or keys[K_d]:
            player.angle += player.turnSpeed

        if keys[K_SPACE] or keys[K_RETURN]:
            player.Fire()
        


    def Update(self):
        player.pos += player.vel
        self.point[0] = (int(self.pos.x+self.r*math.cos(self.angle)), int(self.pos.y+self.r*math.sin(self.angle)))
        self.point[1] = (int(self.pos.x+self.r*math.cos(self.angle-self.innerAngle)), int(self.pos.y+self.r*math.sin(self.angle-self.innerAngle)))
        self.point[2] = (int(self.pos.x+self.r*math.cos(self.angle+self.innerAngle)), int(self.pos.y+self.r*math.sin(self.angle+self.innerAngle)))

        borderSize = 200
        pLaxRate = self.speed*10



        if player.pos.x < borderSize:
            worldSpace.x += pLaxRate
            bgSpace.x += pLaxRate/2
            farBgSpace.x += pLaxRate/3
            player.pos.x = borderSize + 1

        if player.pos.x > DISPLAY_WIDTH - borderSize:
            worldSpace.x -= pLaxRate
            bgSpace.x -= pLaxRate/2
            farBgSpace.x -= pLaxRate/3
            player.pos.x = DISPLAY_WIDTH - borderSize - 1

        if player.pos.y < borderSize:
            worldSpace.y += pLaxRate
            bgSpace.y += pLaxRate/2
            farBgSpace.y += pLaxRate/3
            player.pos.y = borderSize+1

        if player.pos.y > DISPLAY_HEIGHT- borderSize:
            worldSpace.y -= pLaxRate
            bgSpace.y -= pLaxRate/2
            farBgSpace.y -= pLaxRate/3
            player.pos.y = DISPLAY_HEIGHT - borderSize-1
           
        
        #Introduce drag to velocity
        player.vel *= .83

    def Draw(self):
        pygame.draw.line(gameSurface, GREEN, self.point[0], self.point[1])
        pygame.draw.line(gameSurface, GREEN, self.point[1], self.point[2])
        pygame.draw.line(gameSurface, GREEN, self.point[2], self.point[0])
        pygame.draw.circle(gameSurface, BLACK, (self.point[0]), 3)
        
        
        playableSpace = 3000

        #Left limits, right indicator
        if self.pos.x + worldSpace.x > playableSpace:
            pygame.draw.line(gameSurface, GREEN, ((DISPLAY_WIDTH-5,5)), ((DISPLAY_WIDTH-5, DISPLAY_HEIGHT-5)))
        
        #Top limits, bottom indicator
        if self.pos.y + worldSpace.y > playableSpace:
            pygame.draw.line(gameSurface, GREEN, ((5, DISPLAY_HEIGHT-5)), ((DISPLAY_WIDTH-5, DISPLAY_HEIGHT-5)))
            
        #Right limits, left indicator
        if self.pos.x + worldSpace.x < -playableSpace+DISPLAY_WIDTH:
            pygame.draw.line(gameSurface, GREEN, ((5, 5)), ((5,DISPLAY_HEIGHT-5)))   
           
        #Bottom limits, top indicator
        if self.pos.y + worldSpace.y < -playableSpace+DISPLAY_HEIGHT:
            pygame.draw.line(gameSurface, GREEN, ((5, 5)), ((DISPLAY_WIDTH-5, 5)))
            
        for b in range(0, len(self.bullets)):
            self.bullets[b].Update()
            self.bullets[b].Draw()
            
            
player = Entity()

asteroids = []
random.seed(datetime.now())
numOfAsteroids = 100
starfield1 = Starfield(2,3)
starfield2 = Starfield(1,2)
starfield3 = Starfield(1,1)

def SpawnAsteroids(minS, maxS, minR, maxR):
    for i in range(0, numOfAsteroids):
        asteroids.append(Asteroid(minS, maxS, minR, maxR))
        vr = .5
        asteroids[i].vel = (random.uniform(-vr,vr), random.uniform(-vr,vr))
        asteroids[i].SetPos(random.randint(-1000, 1000), random.randint(-1000, 1000))

def DrawAsteroids():
    for n in range(0, numOfAsteroids):
        asteroids[n].Update()
        asteroids[n].Draw()


SpawnAsteroids(9, 40, 10, 200)

while(not exitGame):

    player.HandleInput()
    #End input section

    #Begin update section
    player.Update()
    #End update section

    #Begin drawing section
    gameSurface.fill(BLACK)
    gameSurface.blit(scoreText, textRect)

    starfield1.Draw()
    starfield2.DrawFar()
    starfield3.DrawStatic()
    DrawAsteroids()

    player.Draw()

    #End drawing section
    pygame.display.flip()
    pygame.display.update()
    FramePerSec.tick(FPS)

pygame.quit()
quit()
