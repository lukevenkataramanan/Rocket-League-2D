import pygame


class Ball(object):
    def __init__(self, window, x, y, radius, mass, image, gravity, friction, elasticity):
        self.window = window
        self.x = x
        self.y = y

        self.initial_x = x
        self.initial_y = y
        self.angle = 0  # how much the ball has rotated from normal

        self.radius = radius
        self.h = 2 * radius
        self.w = 2 * radius
        self.mass = mass

        self.gravity = self.mass * gravity  # force of gravity on object
        self.friction = self.gravity * friction

        self.force_x = []  # list of all forces acting in x direction
        # self.force_y = self.gravity * self.mass
        self.force_y = [self.gravity]  # list of all forces acting in y direction

        self.elasticity = elasticity
        self.image = image
        self.image_rect = self.image.get_rect(center=(300, 200))

        self.vel_x = 0
        self.vel_y = 0
        self.is_grounded = False

        self.hitbox = (self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)  # left, top, w, h
        self.left_hitbox = (self.x - self.radius, self.y + 5, 5, 2*self.radius - 10)
        self.top_hitbox = (self.x - self.radius, self.y, 2*self.radius, 5)
        self.right_hitbox = (self.x + 2*self.radius - 5 - self.radius, self.y + 5, 5, 2*self.radius - 10)
        self.bottom_hitbox = (self.x - self.radius, self.y + 2*self.radius - 5, 2*self.radius, 5)
        # left, top, width, height
        self.reset()

    def reset(self):
        self.x = self.initial_x  # reset to initial x position
        self.y = self.initial_y  # reset to initial y position

        self.force_x = []  # reset x forces
        self.force_y = [self.gravity]  # reset y forces

        self.vel_x = 0  # hold still
        self.vel_y = 0  # hold still
        self.is_grounded = False  # it's falling so not grounded
        self.hitbox = (self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)  # left, top, w, h

    def is_falling(self, ground_hitbox):
        # true if bottom of ball is below (>) top of ground
        return self.hitbox[1] + self.hitbox[3] + self.vel_y < ground_hitbox[1]

    def touching_a_wall(self, left_hitbox, right_hitbox):
        # 0: left, 1: top, 2: width, 3: height
        # returns -1 if touching left, 0 if neither, 1 if touching right
        if self.hitbox[0] < left_hitbox[0] + left_hitbox[2]:
            return -1
        elif self.hitbox[0] + self.hitbox[2] > right_hitbox[0]:
            return 1
        else:
            return 0

    def get_accel_x(self):
        return float(sum(self.force_x) / self.mass)

    def get_accel_y(self):
        return float(sum(self.force_y) / self.mass)

    def update_hitbox(self):
        self.hitbox = (self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)  # left, top, w, h
        self.left_hitbox = (self.x - self.radius, self.y + 5 - self.radius, 5, 2 * self.radius - 10)
        self.top_hitbox = (self.x - self.radius, self.y - self.radius, 2 * self.radius, 5)
        self.right_hitbox = (self.x + 2*self.radius - 5 - self.radius, self.y + 5 - self.radius, 5, 2*self.radius - 10)
        self.bottom_hitbox = (self.x - self.radius, self.y + 2 * self.radius - 5 - self.radius, 2 * self.radius, 5)

    def rotate_image(self):
        change_in_angle = float(self.vel_x / self.radius)
        self.angle += change_in_angle
        if self.angle >= 360:
            self.angle -= 360
        print('angle: ' + str(self.angle))
        # v = rw, w = v/r
        image_clean = self.image.copy()
        self.image = pygame.transform.rotate(image_clean, self.angle)

    def draw(self):
        self.window.blit(self.image, (self.x - self.radius, self.y - self.radius))


class Car(object):
    def __init__(self, window, x, y, w, h, mass, images, gravity, friction, elasticity, thrust, facing):
        self.window = window
        self.x = x
        self.y = y
        self.initial_x = x
        self.initial_y = y

        self.w = w
        self.h = h
        self.mass = mass

        self.gravity = self.mass * gravity  # force of gravity on object
        self.friction = self.gravity * friction
        self.thrust = thrust * mass
        self.boost_thrust = self.thrust * 0.75  # half as strong as normal thrust
        self.boost_thrust_up = self.gravity * -2

        self.force_x = []  # list of all forces acting in x direction
        self.force_y = [self.gravity]  # list of all forces acting in y direction

        self.elasticity = elasticity
        self.images = images  # array of images: left, right, left boost, right boost, hover
        self.images_active = [False, False, False]  # left boost, right boost, hover

        self.vel_x = 0
        self.vel_y = 0
        self.is_grounded = False
        self.facing = facing

        self.score = 0
        self.boost_left = 100
        self.status = 'neutral'

        self.jumps_remaining = 1  # can double jump
        # left top width height
        self.hitbox = (self.x, self.y, self.w, self.h)
        self.left_hitbox = (self.x, self.y + 5, 5, self.h - 10)
        self.top_hitbox = (self.x, self.y, self.w, 5)
        self.right_hitbox = (self.x + self.w - 5, self.y + 5, 5, self.h - 10)
        self.bottom_hitbox = (self.x, self.y + self.h - 5, self.w, 5)

        self.reset()

    def reset(self):
        self.x = self.initial_x
        self.y = self.initial_y

        self.force_x = []  # list of all forces acting in x direction
        self.force_y = [self.gravity]  # list of all forces acting in y direction

        self.vel_x = 0
        self.vel_y = 0
        self.jumps_remaining = 0
        self.is_grounded = False
        self.hitbox = (self.initial_x, self.initial_y, self.w, self.h)

    def is_falling(self, ground_hitbox):
        # true if bottom of ball is below (>) top of ground
        is_falling = self.hitbox[1] + self.hitbox[3] + self.vel_y < ground_hitbox[1]
        self.is_grounded = not is_falling  # if falling, not grounded and vice versa
        return is_falling

    def jump_up(self):
        if self.jumps_remaining > 0:
            if self.jumps_remaining == 2:
                self.vel_y -= 15
            else:
                self.vel_y -= 10
            self.jumps_remaining -= 1

    def drive_forward(self, direction):  # if grounded, will accelerate car
        if self.is_grounded:
            if direction == 'left' and self.thrust * -1 not in self.force_x:
                self.force_x.append(self.thrust * -1)
            elif direction == 'right' and self.thrust not in self.force_x:
                self.force_x.append(self.thrust)

    def boost_forward(self, direction):  # boost even if air, activate drive, which only works on ground
        if direction == 'left' and self.boost_thrust * -1 not in self.force_x:
            self.drive_forward('left')
            self.force_x.append(self.boost_thrust * -1)
        elif direction == 'right' and self.boost_thrust not in self.force_x:
            self.drive_forward('right')
            self.force_x.append(self.boost_thrust)
        elif direction == 'up' and self.boost_thrust_up not in self.force_y:
            if self.vel_y > -15:
                self.vel_y -= 1.5

        self.boost_left -= 2

    def flip_forward(self, direction):
        used_for_y = 2
        used_for_x = 10 - used_for_y
        if self.jumps_remaining > 0:
            self.vel_y -= used_for_y
            self.vel_y *= 0.7
            if direction == 'left':
                self.vel_x -= used_for_x
            elif direction == 'right':
                self.vel_x += used_for_x
            self.jumps_remaining -= 1

    def get_accel_x(self):
        return float(sum(self.force_x) / self.mass)  # all forces divided by mass

    def get_accel_y(self):
        return float(sum(self.force_y) / self.mass)  # all forces divided by mass

    def forces_report(self):
        # print(f' forces in x {sum(self.force_x)}')
        pass

    def draw(self):
        # self.window.blit()
        # pygame.draw.rect(self.window, color, self.hitbox)  # draw box around it
        #
        # pygame.draw.rect(self.window, (224, 229, 33), self.left_hitbox)  # draw left hitbox
        # pygame.draw.rect(self.window, (159, 28, 171), self.top_hitbox)  # draw top hitbox
        # pygame.draw.rect(self.window, (224, 229, 33), self.right_hitbox)  # draw right hitbox
        # pygame.draw.rect(self.window, (159, 28, 171), self.bottom_hitbox)  # draw bottom hitbox
        if self.facing == 'left':
            self.window.blit(self.images[0], (self.x, self.y-12))
        else:
            self.window.blit(self.images[1], (self.x, self.y - 12))

    def update_hitbox(self):
        self.hitbox = (self.x, self.y, self.w, self.h)
        self.left_hitbox = (self.x, self.y + 5, 5, self.h - 10)
        self.top_hitbox = (self.x, self.y, self.w, 5)
        self.right_hitbox = (self.x + self.w - 5, self.y + 5, 5, self.h - 10)
        self.bottom_hitbox = (self.x, self.y + self.h - 5, self.w, 5)


class Structure(object):
    def __init__(self, x, y, w, h):
        self.hitbox = (x, y, w, h)  # doesn't move so doesn't have to update
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class Wall(Structure):
    def __init__(self, x, y, w, h):
        super(Wall, self).__init__(x, y, w, h)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.bottom_hitbox = (x, y + h - 5, w, 5)
        self.left_hitbox = (x, y + 5, 5, h - 10)
        self.right_hitbox = (x + w - 5, y + 5, 5, h - 10)
