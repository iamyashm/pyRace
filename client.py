import os
import sys
from math import sin, radians, degrees, copysign

from network import Network

import pygame
from pygame.math import Vector2
from pygame import freetype

GREY = (127, 127, 127)
GREEN = (0, 172, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

ppu = 32 #ratio of pixel to car units

class Car:
    def __init__(self, x, y, player_no, angle=0.0, length=4, max_steering=30, max_acceleration=5.0):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0.0, 0.0)
        self.angle = angle
        self.length = length
        self.max_acceleration = max_acceleration
        self.max_steering = max_steering
        self.max_velocity = 30.0
        self.brake_deceleration = 15.0
        self.free_deceleration = 3.0
        self.acceleration = 0.0
        self.steering = 0.0
        self.player_no = player_no
        self.lap = 0
        self.onFinish = False

    def update(self, dt):
        self.velocity += (self.acceleration * dt, 0)
        self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))

        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(angular_velocity) * dt

        if self.position.x  * ppu >= 1000 and self.position.x * ppu <= 1100 and self.position.y * ppu >= 500 and self.position.y * ppu <= 900:
            if self.onFinish == False and self.velocity.x > 0:
                self.onFinish = True
                self.lap += 1
        else:
            self.onFinish = False

class Track:
    def __init__(self):
        self.surface = pygame.Surface((10000, 7000))
        self.tracklist = []
    def draw(self):
        self.surface.fill(GREEN)
        self.tracklist.append(pygame.Rect((500, 500, 2000, 400)))
        self.tracklist.append(pygame.Rect((2100, 500, 400, 1000)))
        self.tracklist.append(pygame.Rect((2100, 1100, 2000, 400)))
        self.tracklist.append(pygame.Rect((3700, 1100, 400, 1000)))
        self.tracklist.append(pygame.Rect((3100, 1700, 1000, 400)))
        self.tracklist.append(pygame.Rect((3100, 1700, 400, 1500)))
        self.tracklist.append(pygame.Rect((3100, 2800, 1000, 400)))
        self.tracklist.append(pygame.Rect((3700, 2800, 400, 2000)))
        self.tracklist.append(pygame.Rect((500, 4400, 3600, 400)))
        self.tracklist.append(pygame.Rect((500, 500, 400, 4300)))
         
        for r in self.tracklist:
            pygame.draw.rect(self.surface, GREY, r, border_radius=200)

        cnt = 0
        for r in self.tracklist:
            cnt += 1
            if cnt % 2 == 1:  #horizontal rectangle
                for x in range(r.left + 300, r.left + r.width - 300, 200): 
                    pygame.draw.rect(self.surface, WHITE, (x, r.top + 180, 100, 40))
            
            else:
                for x in range(r.top + 300, r.top + r.height - 200, 200):
                    pygame.draw.rect(self.surface, WHITE, (r.left + 180, x, 40, 100))
        
        
        even = 0
        for i in range(1000, 1100, 25):
            odd = even
            for j in range(500, 900, 25):
                if odd == 0:
                    col = WHITE
                else:
                    col = BLACK
                pygame.draw.rect(self.surface, col, (i, j, 25, 25))
                odd = 1 - odd
            even = 1 - even

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('PyRace')
        width = 1280
        height = 720
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False 
    def run(self):
        n = Network()
        car = n.getP()
        track = Track()
        track.draw() 
        track_copy = track.surface.copy()
        offtrack = False
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path1 = os.path.join(current_dir, "car_images/car-red.png")
        image_path2 = os.path.join(current_dir, "car_images/car-blue.png")

        game_font = pygame.freetype.SysFont(None, 24)
        
        if car.player_no == 1:
            car_image = pygame.image.load(image_path1)
            car2_image = pygame.image.load(image_path2)
        else:
            car_image = pygame.image.load(image_path2)
            car2_image = pygame.image.load(image_path1)

        while not self.exit:
            dt = self.clock.get_time() / 1000.0

            car2 = n.send(car)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            car.update(dt)
            
            pressed = pygame.key.get_pressed()
            
            if pressed[pygame.K_UP]:
                if car.velocity.x < 0:
                    car.acceleration = car.brake_deceleration
                else:
                    car.acceleration += 3 * dt
            elif pressed[pygame.K_DOWN]:
                if car.velocity.x > 0:
                    car.acceleration = -car.brake_deceleration
                else:
                    car.acceleration -= 3 * dt
            elif pressed[pygame.K_SPACE]:
                if abs(car.velocity.x) > dt * car.brake_deceleration:
                    car.acceleration = -copysign(car.brake_deceleration, car.velocity.x)
                else:
                    car.acceleration = -car.velocity.x / dt
            else:
                if abs(car.velocity.x) > dt * car.free_deceleration:
                    car.acceleration = -copysign(car.free_deceleration, car.velocity.x)
                else:
                    if dt != 0:
                        car.acceleration = -car.velocity.x / dt
            
            if not pressed[pygame.K_SPACE]:
                car.acceleration = max(-car.max_acceleration, min(car.acceleration, car.max_acceleration))
            
            if offtrack == True:
                car.acceleration = max(-1.0, min(car.acceleration, 1.0))

            if pressed[pygame.K_RIGHT]:
                car.steering -= 30 * dt
            elif pressed[pygame.K_LEFT]:
                car.steering += 30 * dt
            else:
                car.steering = 0
            car.steering = max(-car.max_steering, min(car.steering, car.max_steering))

            if track.surface.get_at((int(car.position.x * ppu), int(car.position.y * ppu))) == GREEN:
                if offtrack == False:
                    offtrack = True
                    car.velocity = 0.2 * car.velocity
                    car.acceleration = 0
            else:
                offtrack = False
            
            rotated = pygame.transform.rotate(car_image, car.angle)
            rect = rotated.get_rect()
            rotated2 = pygame.transform.rotate(car2_image, car2.angle)
            rect2 = rotated2.get_rect()
            
            self.screen.fill(GREEN)
            track.surface.blit(track_copy, dest=(car2.position.x * ppu - 100, car2.position.y * ppu - 100), area=(car2.position.x * ppu - 100, car2.position.y * ppu - 100, 500, 500))
            track.surface.blit(rotated2,  car2.position * ppu - (rect2.width / 2, rect2.height / 2))
            self.screen.blit(track.surface, -car.position * ppu + (600, 450))
            self.screen.blit(rotated, pygame.Vector2(600, 450) - (rect.width / 2, rect.height / 2)) 
            game_font.render_to(self.screen, (50, 50), "Current Lap: " + str(car.lap), BLACK)
            game_font.render_to(self.screen, (50, 90), "Speed: " + str(abs(int(car.velocity.x * 3.6))) + " km/h", BLACK)    
            
            pygame.display.update()
            self.clock.tick(self.ticks)
        
        pygame.display.quit()
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()


