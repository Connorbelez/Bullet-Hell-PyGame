# import and initialize
import pygame
import random
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    RLEACCEL,
    K_SPACE,
)
import math
import os
import getopt
from socket import *
import sys
from socket import *
from pygame.locals import *

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1200
SHOOT = pygame.USEREVENT + 3
pygame.font.init()
font = pygame.font.SysFont('Arial', 30)



class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        # self.surf = pygame.Surface((64, 64))
        playerImg = pygame.image.load(os.path.join('resources', 'battleship.png')).convert()
        # self.surf = pygame.image.load(os.path.join('resources', 'battleship.png')).convert()
        playerImg = pygame.transform.scale(playerImg, (64, 64))
        playerImg = pygame.transform.rotate(playerImg, 270)
        self.surf = playerImg
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.ammo = 100

    # update method
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -10)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 10)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(10, 0)

        # clamp functionality
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


    def getCenter(self):
        x = self.rect.center
        return x

    def shoot(self):
        self.ammo -= 1

    def reload(self):
        x = random.randint(1,10)
        self.ammo += x
        if self.ammo>100:
            self.ammo =100


class AlienDrones(pygame.sprite.Sprite):
    def __init__(self):
        super(AlienDrones, self).__init__()
        # self.surf = pygame.Surface((20, 10))
        aliendroneImg = pygame.image.load(os.path.join('resources', 'ufo.png')).convert()
        aliendroneImg = pygame.transform.scale(aliendroneImg, (64, 64))
        self.surf = aliendroneImg
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),  # this places it just off the screen
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(5, 20)
        # move the sprite based on speed
        # remove teh sprite when it passes the left edge of the screen

    def update(self):  # note this is overriding an inherited method
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()  # removes references to the sprite, sends to trash collector

    def droppedAmmo(self):
        x = random.randint(0, 100)
        if x >= 75:
            return True
        else:
            return False

    def getCentre(self):
        return self.rect.center


class Ammo(pygame.sprite.Sprite):
    def __init__(self, alien):
        super(Ammo, self).__init__()
        ammoImg = pygame.image.load(os.path.join('resources', 'ammo.png')).convert()
        ammoImg = pygame.transform.scale(ammoImg, (32, 32))
        self.surf = ammoImg
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=alien.getCentre()
        )

    def update(self):
        self.rect.move_ip(-5, 0)
        if self.rect.right < 0:
            self.kill()


class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super(Cloud, self).__init__()
        cloudImg = pygame.image.load(os.path.join('resources', 'clouds.png')).convert()
        cloudImg = pygame.transform.scale(cloudImg, (200, 200))
        self.surf = cloudImg
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

    def update(self):
        self.rect.move_ip(-5, 0)
        if self.rect.left < 0:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, player):
        super(Bullet, self).__init__()
        bulletImg = pygame.image.load(os.path.join('resources', 'bullet.png')).convert()
        bulletImg = pygame.transform.scale(bulletImg, (20, 20))
        bulletImg = pygame.transform.rotate(bulletImg, 270)
        self.surf = bulletImg
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                player.getCenter()
            )
        )

        # move teh bullets

    def update(self):
        self.rect.move_ip(20, 0)
        if self.rect.left >= SCREEN_WIDTH:
            self.kill()


def main():
    pygame.init()
    clock = pygame.time.Clock()

    # setup the drawing window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Invaders")
    icon = pygame.image.load(os.path.join('resources', 'ufo.png'))
    pygame.display.set_icon(icon)

    # set up the player
    player = Player()
    # testdrone = AlienDrones() #test

    # Custom Event for creating enemies
    ADD_DRONE = pygame.USEREVENT + 1
    pygame.time.set_timer(ADD_DRONE, 250)
    ADD_CLOUD = pygame.USEREVENT + 2
    pygame.time.set_timer(ADD_CLOUD, 1000)
    SHOOT = pygame.USEREVENT + 3
    pygame.time.set_timer(SHOOT, 250)
    # SHOOTY = pygame.event.Event()

    # custom event for bullets

    # Sprite Groups
    # enemy group used for collision detection an position updates
    # all_sprites used for rendering

    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    clouds = pygame.sprite.Group()
    friendlyBullets = pygame.sprite.Group()
    ammo = pygame.sprite.Group()

    # gameloop
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            # elif event.type == KEYDOWN:
            #     if event.key == K_ESCAPE:
            #         return

            # populate drones
            elif event.type == ADD_DRONE:
                # create a drone and add it to the sprite groups
                new_drone = AlienDrones()
                enemies.add(new_drone)
                all_sprites.add(new_drone)
            elif event.type == ADD_CLOUD:
                new_cloud = Cloud()
                clouds.add(new_cloud)
                all_sprites.add(new_cloud)
            elif event.type == KEYDOWN:
                if player.ammo > 0:
                    if event.key == K_SPACE:
                        player.shoot()
                        new_bullet = Bullet(player)
                        friendlyBullets.add(new_bullet)
                        all_sprites.add(new_bullet)

        # get all keys currently pressed
        pressed_keys = pygame.key.get_pressed()
        # update the rect position after key press on each frame

        # update all enemies
        enemies.update()
        clouds.update()
        player.update(pressed_keys)
        friendlyBullets.update()
        ammo.update()

        # fill the background
        screen.fill((0, 31, 53))

        # display ammot
        textsurface = font.render(f'{player.ammo}', False, (255, 255, 255))
        screen.blit(textsurface, (0, 0))

        # draw the player surface to the screen screen.blit(player.surf, player.rect)  # this takes 2 arguments. the
        # surface to draw and the location to draw it. this therefore uses the top left corner of the players rect.

        # draw all sprites to the screen
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        # check for collisions
        if pygame.sprite.spritecollideany(player, enemies):
            # code for "death"
            player.kill()
            return

        x= pygame.sprite.spritecollide(player,ammo,True)
        if len(x) >0:
            player.reload()
            x=[]


        for enemy in enemies:
            if pygame.sprite.spritecollideany(enemy, friendlyBullets):
                if enemy.droppedAmmo():
                    new_ammo = Ammo(enemy)
                    ammo.add(new_ammo)
                    all_sprites.add(new_ammo)

        pygame.sprite.groupcollide(friendlyBullets, enemies, True, True)

        # if pygame.sprite.spritecollideany(player, ammo):
        #     player.reload()



        # flip the display
        pygame.display.flip()  # this updates the entire screen with everything thats been drawn since the last flip.
        clock.tick(37)

    # quit
    pygame.quit()


if __name__ == "__main__":
    main()
