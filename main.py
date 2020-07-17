import os
from math import sin, radians, degrees, copysign

import pygame
from pygame.math import Vector2

GREY = (127, 127, 127)
GREEN = (0, 172, 0)

class Car:
    def __init__(self, x, y, angle=0.0, length=4, max_steering=30, max_acceleration=5.0):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0.0, 0.0)
        self.angle = angle
        self.length = length
        self.max_acceleration = max_acceleration
        self.max_steering = max_steering
        self.max_velocity = 30.0
        self.brake_deceleration = 5.0
        self.free_deceleration = 3.0

        self.acceleration = 0.0
        self.steering = 0.0

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
            pygame.draw.rect(self.surface, GREY, r)

        cnt = 0
        for r in self.tracklist:
            cnt += 1
            if cnt % 2 == 1:  #horizontal rectangle
                for x in range(r.left + 300, r.left + r.width - 300, 200): 
                    pygame.draw.rect(self.surface, (255, 255, 255), (x, r.top + 180, 100, 40))
            
            else:
                for x in range(r.top + 300, r.top + r.height - 200, 200):
                    pygame.draw.rect(self.surface, (255, 255, 255), (r.left + 180, x, 40, 100))

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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "car_images/car-red.png")
        
        car_image = pygame.image.load(image_path)
        car = Car(23.4, 23.4)
        
        ppu = 32
        
        track = Track()
        track.draw() 
        
        offtrack = False

        while not self.exit:
            dt = self.clock.get_time() / 1000.0

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

            car.acceleration = max(-car.max_acceleration, min(car.acceleration, car.max_acceleration))
            
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
                    car.velocity = Vector2(0.0, 0.0)
                    car.acceleration = 0
            else:
                offtrack = False
            #    print((int(car.position.x * ppu), int(car.position.y * ppu)))
            rotated = pygame.transform.rotate(car_image, car.angle)
            rect = rotated.get_rect()
            self.screen.fill(GREEN)
            self.screen.blit(track.surface, -car.position * ppu + (600, 450))
            self.screen.blit(rotated, pygame.Vector2(600, 450) - (rect.width / 2, rect.height / 2))

            pygame.display.update()
            self.clock.tick(self.ticks)
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()

