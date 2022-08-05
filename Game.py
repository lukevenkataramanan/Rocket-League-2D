from objects import *
import numpy as np
from numpy import linalg
from random import randrange
from colors import get_color as gc
import pygame
import time


def objects_are_touching(obj1, obj2):  # compares objects or hitboxes
    box1 = obj1.hitbox
    box2 = obj2.hitbox
    left1 = box1[0]  # left of the first object
    left2 = box2[0]  # left of the second object
    top1 = box1[1]  # top of the first object
    top2 = box2[1]  # top of the second object
    right1 = box1[0] + box1[2]  # right of the first object
    right2 = box2[0] + box2[2]  # right of the second object
    bottom1 = box1[1] + box1[3]  # bottom of the first object
    bottom2 = box2[1] + box2[3]  # bottom of the second object
    collided = right1 > left2 and left1 < right2 and bottom1 > top2 and top1 < bottom2  # returns if they are touching
    return collided


def hitbox_are_touching(hitbox1, hitbox2):  # only used for following function
    box1 = hitbox1
    box2 = hitbox2
    left1 = box1[0]  # left of the first object
    left2 = box2[0]  # left of the second object
    top1 = box1[1]  # top of the first object
    top2 = box2[1]  # top of the second object
    right1 = box1[0] + box1[2]  # right of the first object
    right2 = box2[0] + box2[2]  # right of the second object
    bottom1 = box1[1] + box1[3]  # bottom of the first object
    bottom2 = box2[1] + box2[3]  # bottom of the second object
    collided = right1 > left2 and left1 < right2 and bottom1 > top2 and top1 < bottom2  # returns if they are touching
    return collided


def objects_collided_vertically(top_obj, bottom_obj):
    if hitbox_are_touching(top_obj.bottom_hitbox, bottom_obj.top_hitbox):  # if collided vertically
        if bottom_obj.is_grounded:  # if bottom object is grounded, stop falling
            top_obj.vel_y -= 1.5


def collision_set_new_velocities(obj1, obj2):
    m1 = obj1.mass  # mass of object 1
    m2 = obj2.mass  # mass of object 2

    # x direction
    v0x1 = obj1.vel_x  # x velocity of object 1
    v0x2 = obj2.vel_x  # x velocity of object 2
    v0y1 = obj1.vel_y  # y velocity of object 1
    v0y2 = obj2.vel_y  # y velocity of object 2

    # m1vf1 + m2vf2 = (m1v01 + m2v02)
    # vf1 - vf2 = v02 - v01
    n_row_momentum = [m1, m2]  # variables: final velocities, coefficients are the masses (conservation momentum)
    n_row_kinetic = [1, -1]  # variables: final velocities, coefficients are 1 and -1 (conservation of Ke)
    n_mat = np.array([n_row_momentum, n_row_kinetic])
    constants = np.array([(m1 * v0x1 + m2 * v0x2), (v0x2 - v0x1)])
    final_velocities_x = np.linalg.solve(n_mat, constants)

    n_row_momentum = [m1, m2]  # variables: final velocities, coefficients are the masses (conservation momentum)
    n_row_kinetic = [1, -1]  # variables: final velocities, coefficients are 1 and -1 (conservation of Ke)
    n_mat = np.array([n_row_momentum, n_row_kinetic])
    constants = np.array([(m1 * v0y1 + m2 * v0y2), (v0y2 - v0y1)])
    final_velocities_y = np.linalg.solve(n_mat, constants)

    obj1.vel_x = final_velocities_x[0]
    obj2.vel_x = final_velocities_x[1]
    obj1.vel_y = final_velocities_y[0]
    obj2.vel_y = final_velocities_y[1]


def take_friction(f_obj):
    # if not f_obj.is_falling(ground.hitbox):  # obj is on ground
    if f_obj.is_grounded:  # obj is on ground
        if f_obj.vel_x < 0:  # if object is moving to the left (negative)
            if f_obj.friction * -1 in f_obj.force_x:  # remove left friction
                f_obj.force_x.remove(f_obj.friction * -1)
            if f_obj.friction not in f_obj.force_x:  # if not any right friction, add it
                # we want to add it, but only to the extent that it stops the car, not turn it around
                f_obj.force_x.append(f_obj.friction)
        elif f_obj.vel_x > 0:  # if object is moving to the right (positive)
            if f_obj.friction in f_obj.force_x:  # remove right friction
                f_obj.force_x.remove(f_obj.friction)
            if f_obj.friction * -1 not in f_obj.force_x:  # if not any left friction, add it
                f_obj.force_x.append(f_obj.friction * -1)
        if abs(f_obj.vel_x) <= 0.31:  # if slow enough to be considered still, stop and remove friction
            if f_obj.friction * -1 in f_obj.force_x:  # remove left friction
                f_obj.force_x.remove(f_obj.friction * -1)
            if f_obj.friction in f_obj.force_x:  # remove right friction
                f_obj.force_x.remove(f_obj.friction)
            f_obj.vel_x = 0
    else:  # if obj is falling
        if f_obj.friction * -1 in f_obj.force_x:  # remove left friction
            f_obj.force_x.remove(f_obj.friction * -1)
        if f_obj.friction in f_obj.force_x:  # remove right friction
            f_obj.force_x.remove(f_obj.friction)


class Game:
    def __init__(self, window, ball, fennec, octane, total_time, frame_rate):
        pygame.init()
        pygame.font.init()
        # create attributes from parameters
        self.ball = ball
        self.fennec = fennec
        self.octane = octane
        self.total_time = total_time
        self.custom_chat_fennec = ''
        self.custom_chat_octane = ''
        self.name_fennec = ''
        self.name_octane = ''
        self.frame_rate = frame_rate
        self.game_objects = [self.ball, self.fennec, self.octane]
        # create class attributes that can't be customized
        self.window = window
        pygame.display.set_caption("Rocket League 2D")  # set title of window
        self.main_font = pygame.font.SysFont('sfprotextthin', 50, True)  # create font
        self.clock = pygame.time.Clock()  # create clock
        self.overtime_timer_beginning = -1  # timer in overtime
        self.start_ticks = pygame.time.get_ticks()  # starter tick

        # create field structures
        self.ground = Structure(0, 680, 1440, 150)  # hitbox for ground
        self.ceiling = Structure(0, 0, 1440, 75)  # hitbox for ceiling
        self.left_wall = Wall(0, 0, 75, 475)  # hitbox for left wall
        self.right_wall = Wall(1365, 0, 75, 475)  # hitbox for right_wall
        self.left_goal = Structure(0, 475, 60, 205)  # hitbox for left goal
        self.right_goal = Structure(1380, 475, 60, 205)  # hitbox for right goal
        self.game_clock = Structure(620, 25, 200, 75)  # structure for clock at top of screen
        self.left_score = Structure(520, 25, 100, 65)  # structure for the blue score
        self.right_score = Structure(820, 25, 100, 65)  # structure for the orange score
        self.left_boost_box = Structure(180, 40, 210, 30)  # structure for boost box
        self.right_boost_box = Structure(1050, 40, 210, 30)  # structure for boost box

        # quick chat features
        self.quick_chats_options = [  # used for both players, with the exception of custom chat
            ['Great pass!', 'Nice shot!', 'What a save!', 'Thanks!'],  # left
            ['Need boost!', 'I got it!', 'Defending...', 'Take the shot!'],  # up
            ['No problem.', '$#@%!', 'Sorry!', 'Whoops...'],  # down
            ['Noooo!', 'OMG!', 'Close one!', 'Wow!']  # right
        ]
        self.quick_chats_blue = []  # list of the quick chats blue has said
        self.quick_chats_orange = []  # list of the quick chats orange has said
        self.quick_chats_blue_start_times = []
        self.quick_chats_orange_start_times = []
        self.blue_first_choice = -1  # which button blue chose first to say quick chats
        self.orange_first_choice = -1  # which button orange chose first to say quick chats
        self.quick_chat_limit = 6  # including the chat disabled message (so really n-1)

        # load images
        self.bg = pygame.image.load('images/background.jpg')  # load background image
        self.ground_image = pygame.image.load('images/ground.png')  # load ground image

        # physics
        self.gravity = 1  # g-field acceleration
        self.friction = .35  # friction coefficient
        self.thrust_speed_limit = 15  # how fast a car's velocity can be while driving on ground
        self.boost_speed_limit = 25  # how fast a car can boost

        # cooldowns
        self.cooldown_ball_and_fennec = [0, 5]  # cooldown for collisions against ball on fennec
        self.cooldown_ball_and_octane = [0, 5]  # cooldown for collisions against ball on octane
        self.cooldown_fennec_and_octane = [0, 5]  # cooldown for collisions against fennec on octane

        self.all_cooldowns = [self.cooldown_ball_and_fennec, self.cooldown_ball_and_octane,
                              self.cooldown_fennec_and_octane]
        # status
        self.run = True
        self.master_run = True  # if the whole loop keeps going
        self.PREGAME = -1  # before game starts (countdown from 3)
        self.MAIN_GAME = 0  # if players are playing
        self.TIME_RAN_OUT = 1  # if time ran out but ball in air
        self.OVERTIME = 2  # if time ran out, ball hit ground, and score is tied
        self.GAME_OVER = 3  # if time ran out, ball hit ground, and player won
        self.status = self.PREGAME  # start game in main game

        self.click = False

        # end countdown
        self.end_countdown_number = 10
        self.end_countdown = False

        pygame.mixer.music.load("sounds/crowd noises.mp3")
        pygame.mixer.music.set_volume(0.15)
        self.announcements = {'begin': pygame.mixer.Sound("sounds/neo tokyo begin game.mp3"),
                              'save 1': pygame.mixer.Sound("sounds/neo tokyo save 1.mp3"),
                              'save 3': pygame.mixer.Sound("sounds/neo tokyo save 3.mp3"),
                              'save 4': pygame.mixer.Sound("sounds/neo tokyo save 4.mp3"),
                              'save 5': pygame.mixer.Sound("sounds/neo tokyo save 5.mp3"),
                              'epic save 1': pygame.mixer.Sound("sounds/neo tokyo epic save 1.mp3"),
                              'epic save 2': pygame.mixer.Sound("sounds/neo tokyo epic save 2.mp3"),
                              'epic save 3': pygame.mixer.Sound("sounds/neo tokyo epic save 3.mp3"),
                              'goal 1': pygame.mixer.Sound("sounds/neo tokyo goal 1.mp3"),
                              'goal 2': pygame.mixer.Sound("sounds/neo tokyo goal 2.mp3"),
                              'goal 3': pygame.mixer.Sound("sounds/neo tokyo goal 3.mp3"),
                              'goal 4': pygame.mixer.Sound("sounds/neo tokyo goal 4.mp3"),
                              'goal 5': pygame.mixer.Sound("sounds/neo tokyo goal 5.mp3"),
                              'goal 6': pygame.mixer.Sound("sounds/neo tokyo goal 6.mp3"),
                              '60s remaining': pygame.mixer.Sound("sounds/champions field 60 seconds remaining.mp3"),
                              '30s remaining': pygame.mixer.Sound("sounds/champions field 30 seconds remaining.mp3"),
                              'overtime': pygame.mixer.Sound("sounds/overtime.mp3"),
                              'match over': pygame.mixer.Sound("sounds/neo tokyo match over.mp3")}

        self.start_screen()
        self.beginning_countdown()
        self.main()

    def reset(self):
        self.fennec.score = 0
        self.fennec.facing = 'right'
        self.fennec.boost_left = 100
        self.fennec.reset()

        self.octane.score = 0
        self.octane.facing = 'left'
        self.octane.boost_left = 100
        self.octane.reset()

        self.ball.reset()

    def start_screen(self):
        intro = True
        active_text_field = [True, False, False, False]  # which text field, if any, is active?
        logo_image = pygame.image.load('images/2D Logo.png')  # load logo image
        # fennec name,    fennec chat,     octane name,    octane chat
        title_font = pygame.font.SysFont('Segoe UI', 100, True)  # create font
        secondary_font = pygame.font.SysFont('sfprotextthin', 65, True)  # create font
        tertiary_font = pygame.font.SysFont('trebuchetmsitalic', 40, True)  # create font
        textfield_font = pygame.font.SysFont('sfprodisplayultralightitalic', 45, True)  # create font
        while intro:
            pygame.draw.rect(self.window, gc('menu dark blue'), (0, 0, 1440, 800))  # fill in color
            self.window.blit(logo_image, (520, 315))
            title_text = title_font.render('Rocket League 2D', True, gc('white'))  # create text
            self.window.blit(title_text, (225, 30, 500, 100))  # draw title text
            
            # mouse
            mx, my = pygame.mouse.get_pos()  # get mouse position
            
            # start and exit buttons
            exit_button = pygame.Rect(95, 600, 350, 75)  # the hitbox for quit button
            exit_button_color = gc('black')
            exit_text = secondary_font.render('EXIT', True, gc('white'))
            start_button = pygame.Rect(1020, 600, 350, 75)  # the hitbox for start button
            start_button_color = gc('black')
            start_text = secondary_font.render('START', True, gc('white'))
            if start_button.collidepoint((mx, my)):
                start_button_color = gc('dark gray')
                if self.click:  # if click on start button, start beginning countdown and game
                    intro = False  # close intro, start game
            if exit_button.collidepoint((mx, my)):
                exit_button_color = gc('dark gray')
                if self.click:  # if click on stop button
                    self.run = False  # doesn't initiate game
                    self.master_run = False
                    intro = False  # close program
            pygame.draw.rect(self.window, gc('white'), (90, 595, 360, 85))  # draw exit button frame
            pygame.draw.rect(self.window, exit_button_color, exit_button)  # draw exit button
            self.window.blit(exit_text, (185, 600, 350, 75))  # draw exit text
            pygame.draw.rect(self.window, gc('white'), (1015, 595, 360, 85))  # draw start button frame
            pygame.draw.rect(self.window, start_button_color, start_button)  # draw start button
            self.window.blit(start_text, (1080, 600, 350, 75))  # draw start text

            # text fields
            fennec_name_textfield = pygame.Rect(25, 200, 600, 75)
            fennec_name_textfield_color = gc('html dark gray') if active_text_field[0] else gc('html gray')
            pygame.draw.rect(self.window, gc('blue'), (20, 195, 610, 85))  # draw text field frame
            pygame.draw.rect(self.window, fennec_name_textfield_color,  fennec_name_textfield)
            fennec_name_text_color = gc('black') if self.name_fennec != '' else gc('white')
            fennec_name_text = textfield_font.render(self.name_fennec, True, fennec_name_text_color)
            if self.name_fennec == '':
                fennec_name_text = textfield_font.render('Enter name', True, fennec_name_text_color)
            self.window.blit(fennec_name_text, (35, 210, 600, 75))

            fennec_chat_textfield = pygame.Rect(25, 310, 500, 65)
            fennec_chat_textfield_color = gc('html dark gray') if active_text_field[1] else gc('html gray')
            pygame.draw.rect(self.window, gc('blue'), (20, 305, 510, 75))  # draw text field frame
            pygame.draw.rect(self.window, fennec_chat_textfield_color, fennec_chat_textfield)
            fennec_chat_text_color = gc('black') if self.custom_chat_fennec != '' else gc('white')
            fennec_chat_text = textfield_font.render(self.custom_chat_fennec, True, fennec_chat_text_color)
            if self.custom_chat_fennec == '':
                fennec_chat_text = textfield_font.render("Enter custom chat", True, fennec_chat_text_color)
            self.window.blit(fennec_chat_text, (35, 315, 600, 75))

            octane_name_textfield = pygame.Rect(815, 200, 600, 75)
            octane_name_textfield_color = gc('html dark gray') if active_text_field[2] else gc('html gray')
            pygame.draw.rect(self.window, gc('orange'), (810, 195, 610, 85))  # draw text field frame
            pygame.draw.rect(self.window, octane_name_textfield_color, octane_name_textfield)
            octane_name_text_color = gc('black') if self.name_octane != '' else gc('white')
            octane_name_text = textfield_font.render(self.name_octane, True, octane_name_text_color)
            if self.name_octane == '':
                octane_name_text = textfield_font.render('Enter name', True, octane_name_text_color)
            self.window.blit(octane_name_text, (825, 210, 600, 75))

            octane_chat_textfield = pygame.Rect(915, 310, 500, 65)
            octane_chat_textfield_color = gc('html dark gray') if active_text_field[3] else gc('html gray')
            pygame.draw.rect(self.window, gc('orange'), (910, 305, 510, 75))  # draw text field frame
            pygame.draw.rect(self.window, octane_chat_textfield_color, octane_chat_textfield)
            octane_chat_text_color = gc('black') if self.custom_chat_octane != '' else gc('white')
            octane_chat_text = textfield_font.render(self.custom_chat_octane, True, octane_chat_text_color)
            if self.custom_chat_octane == '':
                octane_chat_text = textfield_font.render("Enter custom chat", True, octane_chat_text_color)
            self.window.blit(octane_chat_text, (925, 315, 600, 75))

            versus_text = tertiary_font.render('vs.', True, gc('white'))
            self.window.blit(versus_text, (695, 215, 20, 20))
            credit_text = tertiary_font.render('Created by Luke Venkataramanan®', True, gc('white'))
            self.window.blit(credit_text, credit_text.get_rect(center=(720, 750)))

            if self.click:
                for i in range(len(active_text_field)):
                    active_text_field[i] = False
                if fennec_name_textfield.collidepoint((mx, my)):
                    active_text_field[0] = True
                elif fennec_chat_textfield.collidepoint((mx, my)):
                    active_text_field[1] = True
                elif octane_name_textfield.collidepoint((mx, my)):
                    active_text_field[2] = True
                elif octane_chat_textfield.collidepoint((mx, my)):
                    active_text_field[3] = True

            self.click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # if quit, don't start game and then quit
                    self.run = False
                    self.master_run = False
                    intro = False
                elif event.type == pygame.MOUSEBUTTONDOWN:  # if click down, set click to true
                    if event.button == 1:
                        self.click = True
                elif event.type == pygame.KEYDOWN:
                    all_filled = (self.name_fennec != '' and self.custom_chat_fennec != '' and
                                  self.name_octane != '' and self.custom_chat_octane != '')  # every tf has text
                    if event.key == pygame.K_TAB or (event.key == pygame.K_RETURN and not all_filled):
                        for i in range(len(active_text_field)):  # switch to next text field
                            if active_text_field[i]:
                                if i == 3:
                                    active_text_field[0] = True
                                else:
                                    active_text_field[i+1] = True
                                active_text_field[i] = False
                                break
                    elif event.key == pygame.K_RETURN:  # start game because all text fields are filled
                        intro = False
                    else:  # set the edited text to what was previously in the text field
                        current_tf = self.name_fennec
                        if active_text_field[1]:
                            current_tf = self.custom_chat_fennec
                        elif active_text_field[2]:
                            current_tf = self.name_octane
                        elif active_text_field[3]:
                            current_tf = self.custom_chat_octane
                        if event.key == pygame.K_BACKSPACE:  # hit backspace
                            current_tf = current_tf[:-1]
                        else:  # type in a character
                            current_tf += event.unicode

                        # modify the given game attribute depending on what's being typed
                        if active_text_field[0]:
                            self.name_fennec = current_tf
                        elif active_text_field[1]:
                            self.custom_chat_fennec = current_tf
                        elif active_text_field[2]:
                            self.name_octane = current_tf
                        elif active_text_field[3]:
                            self.custom_chat_octane = current_tf
            pygame.display.update()
        pygame.mixer.music.play(-1)

    def redraw_game_window(self):
        self.window.blit(self.bg, (0, 0))  # draw in background
        self.window.blit(self.ground_image, (0, 650))  # draw ground
        # pygame.draw.rect(self.window, (54, 58, 55), ground.hitbox)  # draw the ground rectangle for reference
        pygame.draw.rect(self.window, gc('dark gray'), self.left_wall.hitbox)  # draw left wall
        pygame.draw.rect(self.window, gc('dark gray'), self.right_wall.hitbox)  # draw right wall
        pygame.draw.rect(self.window, gc('dark gray'), self.ceiling.hitbox)  # draw ceiling
        pygame.draw.rect(self.window, gc('blue'), self.left_goal.hitbox)  # draw left goal
        pygame.draw.rect(self.window, gc('orange'), self.right_goal.hitbox)  # draw right goal

        pygame.draw.rect(self.window, gc('black'), self.game_clock.hitbox)  # draw top clock box
        pygame.draw.rect(self.window, gc('blue'), self.left_score.hitbox)  # draw left score
        pygame.draw.rect(self.window, gc('orange'), self.right_score.hitbox)  # draw right score

        name_font = pygame.font.SysFont('sfprotextthin', 25, True)  # create name font
        fennec_name_text = name_font.render(self.name_fennec, True, gc('white'))
        octane_name_text = name_font.render(self.name_octane, True, gc('white'))
        fennec_name_text_rect = fennec_name_text.get_rect(center=(285, 20))
        octane_name_text_rect = octane_name_text.get_rect(center=(1155, 20))

        pygame.draw.rect(self.window, gc('blue'), self.left_boost_box.hitbox)  # draw left boost box
        self.window.blit(fennec_name_text, fennec_name_text_rect)
        pygame.draw.rect(self.window, gc('orange'), self.right_boost_box.hitbox)  # draw right boost box
        self.window.blit(octane_name_text, octane_name_text_rect)

        time_text = self.main_font.render(self.update_time(), True, gc('white'))  # create time text
        fennec_score = self.main_font.render(str(self.fennec.score), True, gc('white'))  # create fennec score text
        octane_score = self.main_font.render(str(self.octane.score), True, gc('white'))  # create octane score text

        self.window.blit(time_text, (657.5, 32.5, 200, 75))  # show time
        self.window.blit(fennec_score, (550, 30, 200, 75))  # show fennec score
        self.window.blit(octane_score, (850, 30, 200, 75))  # show octane score

        left_boost_width = int(float(self.fennec.boost_left / 100) * 200)  # gets width of boost
        pygame.draw.rect(self.window, gc('white'), (185, 45, left_boost_width, 20))  # draw left boost bar
        right_boost_width = int(float(self.octane.boost_left / 100) * 200)  # get width of boost
        pygame.draw.rect(self.window, gc('white'), (1255 - right_boost_width, 45, right_boost_width, 20))

        if self.fennec.images_active[0]:  # draw the left boost for fennec if boosting left
            self.window.blit(self.fennec.images[2], (self.fennec.x + 86, self.fennec.y - 13))
        if self.fennec.images_active[1]:  # draw the left boost for fennec if boosting left
            self.window.blit(self.fennec.images[3], (self.fennec.x - 90, self.fennec.y - 13))
        if self.fennec.images_active[2]:  # draw the hover for fennec if hovering
            self.window.blit(self.fennec.images[4], (self.fennec.x, self.fennec.y + 30))

        if self.octane.images_active[0]:  # draw the left boost for fennec if boosting left
            self.window.blit(self.octane.images[2], (self.octane.x + 78, self.octane.y - 13))
        if self.octane.images_active[1]:  # draw the left boost for fennec if boosting left
            self.window.blit(self.octane.images[3], (self.octane.x - 87, self.octane.y - 13))
        if self.octane.images_active[2]:  # draw the hover for octane if hovering
            self.window.blit(self.octane.images[4], (self.octane.x, self.octane.y + 30))

        self.ball.draw()  # draw ball
        self.fennec.draw()  # draw fennec
        self.octane.draw()  # draw octane

        pygame.display.update()  # update screen

    def hit_bottom_of_wall(self, w_obj):  # sees if object is going to hit either ceiling of wall
        # check left: if left of car is to the left of the right edge of the left wall
        # or
        # check right: if right of car is to the right of the left edge of the right wall
        # if collided but before it collided it was under the wall
        return (w_obj.vel_y < 0 and
                (w_obj.hitbox[0] < self.left_wall.hitbox[0] + self.left_wall.hitbox[2] and
                 w_obj.hitbox[1] < self.left_wall.hitbox[1] + self.left_wall.hitbox[3] < w_obj.hitbox[1] - w_obj.vel_y)
                or
                (w_obj.hitbox[0] + w_obj.hitbox[2] > self.right_wall.hitbox[0] and
                 (w_obj.hitbox[1] < self.right_wall.hitbox[1] + self.right_wall.hitbox[3]
                  < w_obj.hitbox[1] - w_obj.vel_y)))

    def take_gravity(self, g_obj):
        if g_obj.is_falling(self.ground.hitbox):
            g_obj.is_grounded = False
            if g_obj.gravity not in g_obj.force_y:  # if falling, add gravity
                g_obj.force_y.append(g_obj.gravity)
        else:  # if touching ground, don't put gravity
            g_obj.vel_y = g_obj.vel_y * -g_obj.elasticity  # bounce it back up
            if abs(g_obj.vel_y) <= 0.31:
                g_obj.vel_y = 0  # if almost still on ground, hold still
            if g_obj.gravity in g_obj.force_y:  # if grounded, don't use gravity
                g_obj.force_y.remove(g_obj.gravity)

    def draw_countdown(self, num, end):
        font_cd = pygame.font.SysFont('sfprotextthin', 200, True)  # create font
        if not end:
            self.redraw_game_window()
        if num == 0:
            text = font_cd.render('Go!', True, (255, 255, 255))
            text_rect = text.get_rect(center=(1440/2, 800/2))
            self.window.blit(text, text_rect)
        else:
            text = font_cd.render(str(num), True, (255, 255, 255))
            text_rect = text.get_rect(center=(1440 / 2, 800 / 2))
            self.window.blit(text, text_rect)
        pygame.display.update()
        if self.status == self.PREGAME:
            pygame.time.delay(1000)

    def game_over(self, winner):
        self.redraw_game_window()
        font_go = pygame.font.SysFont('sfprotextthin', 100, True)  # create font
        if winner == 'blue':
            text = font_go.render(f'{self.name_fennec} wins!', True, (255, 255, 255))
            text_rect = text.get_rect(center=(1440/2, 800/2))
            self.window.blit(text, text_rect)
            pygame.mixer.Sound.play(self.announcements['match over'])
        elif winner == 'orange':
            text = font_go.render(f'{self.name_octane} wins!', True, (255, 255, 255))
            text_rect = text.get_rect(center=(1440 / 2, 800 / 2))
            self.window.blit(text, text_rect)
            pygame.mixer.Sound.play(self.announcements['match over'])
        else:  # tie
            text = font_go.render('Overtime!', True, (255, 255, 255))
            # self.window.blit(text, (720 - 320, 400 - 100))
            self.window.blit(text, text.get_rect(center=(720, 400)))
            pygame.mixer.Sound.play(self.announcements['overtime'])
        pygame.display.update()
        pygame.time.delay(3000)

    def manage_quick_chats(self):
        # global quick_chats_blue_start_times, quick_chats_orange_start_times
        quick_chats_blue_indexes_to_delete = []
        quick_chats_orange_indexes_to_delete = []

        for b in range(len(self.quick_chats_blue_start_times)):
            if time.time() - self.quick_chats_blue_start_times[b] >= 3:
                quick_chats_blue_indexes_to_delete.append(b)
        for o in range(len(self.quick_chats_orange_start_times)):
            if time.time() - self.quick_chats_orange_start_times[o] >= 3:
                quick_chats_orange_indexes_to_delete.append(o)

        for qcbitd in quick_chats_blue_indexes_to_delete:
            self.quick_chats_blue.pop(qcbitd)
            self.quick_chats_blue_start_times.pop(qcbitd)
            if 'Chat disabled for 3 seconds' in self.quick_chats_blue:
                index = self.quick_chats_blue.index('Chat disabled for 3 seconds')
                self.quick_chats_blue.pop(index)
                self.quick_chats_blue_start_times.pop(index)
        for qcoitd in quick_chats_orange_indexes_to_delete:
            self.quick_chats_orange.pop(qcoitd)
            self.quick_chats_orange_start_times.pop(qcoitd)
            if 'Chat disabled for 3 seconds' in self.quick_chats_orange:
                index = self.quick_chats_orange.index('Chat disabled for 3 seconds')
                self.quick_chats_orange.pop(index)
                self.quick_chats_orange_start_times.pop(index)

    def draw_quick_chats(self):
        font_cd = pygame.font.SysFont('sfprotextthin', 25, True)
        for i in range(len(self.quick_chats_blue)):
            if i == self.quick_chat_limit - 1:
                color = gc('text yellow')
            else:
                color = gc('white')
            text = font_cd.render(self.quick_chats_blue[i], True, color)
            y_position = 28 * i + 80
            self.window.blit(text, (85, y_position))
        for i in range(len(self.quick_chats_orange)):
            if i == self.quick_chat_limit - 1:
                color = gc('text yellow')
                x_position = 1005
            else:
                color = gc('white')
                x_position = 1180
            text = font_cd.render(self.quick_chats_orange[i], True, color)
            y_position = 28 * i + 80
            self.window.blit(text, (x_position, y_position))
        pygame.display.update()

    def choose_quick_chat(self, player, second_choice):
        # custom chats
        if second_choice == 4:
            return 'Chat disabled for 3 seconds'
        if player == 'blue':
            if second_choice == 5:
                return self.custom_chat_fennec
            else:
                chat = self.quick_chats_options[self.blue_first_choice][second_choice]
                if chat == 'What a save!':
                    self.announce_chat('save')
                return chat
        else:  # if player == 'orange'
            if second_choice == 5:
                return self.custom_chat_octane
            else:
                chat = self.quick_chats_options[self.orange_first_choice][second_choice]
                if chat == 'What a save!':
                    self.announce_chat('save')
                return chat

    def announce_chat(self, chat_type):
        if pygame.mixer.Channel(0).get_busy():
            return
        if chat_type == 'save':
            chat_index = randrange(0, 7)
            if chat_index == 0:
                pygame.mixer.Sound.play(self.announcements['save 1'])
            elif chat_index == 1:
                pygame.mixer.Sound.play(self.announcements['save 3'])
            elif chat_index == 2:
                pygame.mixer.Sound.play(self.announcements['save 4'])
            elif chat_index == 3:
                pygame.mixer.Sound.play(self.announcements['save 5'])
            elif chat_index == 4:
                pygame.mixer.Sound.play(self.announcements['epic save 1'])
            elif chat_index == 5:
                pygame.mixer.Sound.play(self.announcements['epic save 2'])
            elif chat_index == 6:
                pygame.mixer.Sound.play(self.announcements['epic save 3'])
        elif chat_type == 'goal':
            chat_index = randrange(0, 6)
            if chat_index == 0:
                pygame.mixer.Sound.play(self.announcements['goal 1'])
            elif chat_index == 1:
                pygame.mixer.Sound.play(self.announcements['goal 2'])
            elif chat_index == 2:
                pygame.mixer.Sound.play(self.announcements['goal 3'])
            elif chat_index == 3:
                pygame.mixer.Sound.play(self.announcements['goal 4'])
            elif chat_index == 4:
                pygame.mixer.Sound.play(self.announcements['goal 5'])
            elif chat_index == 5:
                pygame.mixer.Sound.play(self.announcements['goal 6'])
        elif chat_type == '60s remaining':
            pygame.mixer.Sound.play(self.announcements['60s remaining'])
        elif chat_type == '30s remaining':
            pygame.mixer.Sound.play(self.announcements['30s remaining'])

    def update_time(self):  # returns time text for redraw game window
        if self.status == self.PREGAME:
            minutes_left = int(self.total_time / 60)
            seconds_left = int(self.total_time % 60)
        elif self.status == self.MAIN_GAME:
            seconds_ticked = ((pygame.time.get_ticks() - self.start_ticks) / 1000) - 1
            total_seconds_left = self.total_time - seconds_ticked
            minutes_left = int(total_seconds_left / 60)
            seconds_left = int(total_seconds_left % 60)
        elif self.status == self.OVERTIME:
            overtime_seconds_elapsed = time.time() - self.overtime_timer_beginning
            minutes_left = int(overtime_seconds_elapsed / 60)
            seconds_left = int(overtime_seconds_elapsed % 60)
        else:  # status is time ran out
            minutes_left = 0
            seconds_left = 0

        if minutes_left <= 0 and seconds_left <= 10 and self.status == self.MAIN_GAME:
            self.end_countdown = True
            self.end_countdown_number = seconds_left
        if minutes_left <= 0 and seconds_left <= 0 and self.status == self.MAIN_GAME:
            self.status = self.TIME_RAN_OUT

        if minutes_left == 1 and seconds_left == 0:
            self.announce_chat('60s remaining')
        elif minutes_left == 0 and seconds_left == 30:
            self.announce_chat('30s remaining')

        if seconds_left >= 10:
            return f'{minutes_left}:{seconds_left}'
        else:
            return f'{minutes_left}:0{seconds_left}'

    def beginning_countdown(self):
        pygame.mixer.Sound.play(self.announcements['begin'])
        beginning_countdown_number = 3
        beginning_countdown = True
        while self.run and beginning_countdown:  # don't want to initiate if run won't be true
            self.clock.tick(27)  # sets fps to 27
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    break
            if beginning_countdown_number >= 0:
                self.draw_countdown(beginning_countdown_number, False)
                beginning_countdown_number -= 1
            else:
                self.status = self.MAIN_GAME
                beginning_countdown = False

    def main(self):
        self.start_ticks = pygame.time.get_ticks()  # redefine, starter ticks to right before game
        while self.run:
            self.clock.tick(self.frame_rate)  # set frames per second to 30
            self.update_time()

            chat_keys_blue = [False, False, False, False, False]  # f, t, g, h,   e
            chat_keys_orange = [False, False, False, False, False]  # j, i, k, l,   rightshift
            jump_key_fennec = False  # w
            jump_key_octane = False  # up
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # if press the x button, close window
                    self.run = False  # stop the run loop
                if event.type == pygame.KEYUP:  # quick chats and jumping
                    chat_keys_blue[0] = event.key == pygame.K_f
                    chat_keys_blue[1] = event.key == pygame.K_t
                    chat_keys_blue[2] = event.key == pygame.K_g
                    chat_keys_blue[3] = event.key == pygame.K_h
                    chat_keys_blue[4] = event.key == pygame.K_e
                    chat_keys_orange[0] = event.key == pygame.K_j
                    chat_keys_orange[1] = event.key == pygame.K_i
                    chat_keys_orange[2] = event.key == pygame.K_k
                    chat_keys_orange[3] = event.key == pygame.K_l
                    chat_keys_orange[4] = event.key == pygame.K_SLASH
                if event.type == pygame.KEYDOWN:
                    jump_key_fennec = event.key == pygame.K_w
                    jump_key_octane = event.key == pygame.K_UP

            keys = pygame.key.get_pressed()  # register all keys pressed

            # check if objects are grounded
            for obj in self.game_objects:
                obj.is_grounded = not obj.is_falling(self.ground.hitbox)

            if (self.status == self.TIME_RAN_OUT and
                    self.ball.hitbox[1] + self.ball.hitbox[3] + self.ball.vel_y >= self.ground.hitbox[1]):
                self.status = self.GAME_OVER

            # perform cooldowns
            for cooldown in self.all_cooldowns:
                if cooldown[0] > 0:
                    cooldown[0] += 1
                if cooldown[0] > cooldown[1]:
                    cooldown[0] = 0

            # x-axis
            if self.status == self.MAIN_GAME or self.status == self.TIME_RAN_OUT or self.status == self.OVERTIME:
                if keys[pygame.K_a]:
                    self.fennec.facing = 'left'
                elif keys[pygame.K_d]:
                    self.fennec.facing = 'right'
                # else:
                #     self.fennec.facing = 'neutral'

                if keys[pygame.K_a] and self.fennec.vel_x > -self.thrust_speed_limit and self.fennec.hitbox[0] > 0:
                    self.fennec.drive_forward('left')
                elif self.fennec.thrust * -1 in self.fennec.force_x:  # if not press a, don't let it thrust left
                    self.fennec.force_x.remove(self.fennec.thrust * -1)
                if (keys[pygame.K_d] and self.fennec.vel_x < self.thrust_speed_limit and
                        self.fennec.hitbox[0] + self.fennec.hitbox[2] < 1440):
                    self.fennec.drive_forward('right')
                elif self.fennec.thrust in self.fennec.force_x:  # if not press d, don't let it thrust right
                    self.fennec.force_x.remove(self.fennec.thrust)

                # boost
                if (keys[pygame.K_w] and self.fennec.boost_left > 0 and self.fennec.jumps_remaining <= 0 and
                        self.fennec.boost_thrust_up not in self.fennec.force_y and
                        self.fennec.get_accel_y() > -self.fennec.gravity):
                    self.fennec.boost_forward('up')
                    self.fennec.images_active[2] = True
                else:
                    if self.fennec.boost_thrust_up in self.fennec.force_y:
                        self.fennec.force_y.remove(self.fennec.boost_thrust_up)
                    self.fennec.images_active[2] = False
                if (keys[pygame.K_s] and self.fennec.boost_left > 0 and self.fennec.facing == 'left' and
                        self.fennec.vel_x > -self.boost_speed_limit):
                    self.fennec.boost_forward('left')
                    self.fennec.images_active[0] = True
                else:
                    if self.fennec.boost_thrust * -1 in self.fennec.force_x:
                        self.fennec.force_x.remove(self.fennec.boost_thrust * -1)
                    self.fennec.images_active[0] = False
                if (keys[pygame.K_s] and self.fennec.boost_left > 0 and self.fennec.facing == 'right' and
                        self.fennec.vel_x < self.boost_speed_limit):
                    self.fennec.boost_forward('right')
                    self.fennec.images_active[1] = True
                else:
                    if self.fennec.boost_thrust in self.fennec.force_x:
                        self.fennec.force_x.remove(self.fennec.boost_thrust)
                    self.fennec.images_active[1] = False

                take_friction(self.fennec)  # make self.fennec take friction

                if keys[pygame.K_LEFT]:
                    self.octane.facing = 'left'
                elif keys[pygame.K_RIGHT]:
                    self.octane.facing = 'right'
                # else:
                #     self.octane.facing = 'neutral'

                if keys[pygame.K_LEFT] and self.octane.vel_x > -self.thrust_speed_limit and self.octane.hitbox[0] > 0:
                    self.octane.drive_forward('left')
                elif self.octane.thrust * -1 in self.octane.force_x:  # if not press a, don't let it thrust left
                    self.octane.force_x.remove(self.octane.thrust * -1)
                if (keys[pygame.K_RIGHT] and self.octane.vel_x < self.thrust_speed_limit and
                        self.octane.hitbox[0] + self.octane.hitbox[2] < 1440):
                    self.octane.drive_forward('right')
                elif self.octane.thrust in self.octane.force_x:  # if not press d, don't let it thrust right
                    self.octane.force_x.remove(self.octane.thrust)

                # boost
                if (keys[pygame.K_UP] and self.octane.boost_left > 0 and self.octane.jumps_remaining <= 0 and
                        self.octane.boost_thrust_up not in self.octane.force_y and
                        self.octane.get_accel_y() > -self.octane.gravity):
                    self.octane.boost_forward('up')
                    self.octane.images_active[2] = True
                else:
                    if self.octane.boost_thrust_up in self.octane.force_y:
                        self.octane.force_y.remove(self.octane.boost_thrust_up)
                    self.octane.images_active[2] = False
                if (keys[pygame.K_DOWN] and self.octane.boost_left > 0 and
                        self.octane.facing == 'left' and self.octane.vel_x > -self.boost_speed_limit):
                    self.octane.boost_forward('left')
                    self.octane.images_active[0] = True
                else:
                    if self.octane.boost_thrust * -1 in self.octane.force_x:
                        self.octane.force_x.remove(self.octane.boost_thrust * -1)
                    self.octane.images_active[0] = False
                if (keys[pygame.K_DOWN] and self.octane.boost_left > 0 and
                        self.octane.facing == 'right' and self.octane.vel_x < self.boost_speed_limit):
                    self.octane.boost_forward('right')
                    self.octane.images_active[1] = True
                else:
                    if self.octane.boost_thrust in self.octane.force_x:
                        self.octane.force_x.remove(self.octane.boost_thrust)
                    self.octane.images_active[1] = False

                take_friction(self.octane)  # make self.octane take friction

                boost_regen_rate = 0.05
                self.fennec.boost_left += boost_regen_rate
                self.fennec.boost_left = min(self.fennec.boost_left, 100)
                self.octane.boost_left += boost_regen_rate
                self.octane.boost_left = min(self.octane.boost_left, 100)

                # y-axis
                if self.fennec.is_grounded:
                    self.fennec.jumps_remaining = 2
                if jump_key_fennec:
                    if self.fennec.jumps_remaining == 1:  # can only flip if already used jump in air
                        if keys[pygame.K_a]:
                            self.fennec.flip_forward('left')
                        elif keys[pygame.K_d]:
                            self.fennec.flip_forward('right')
                        else:
                            self.fennec.jump_up()
                    else:  # first jump has to be up, not a flip
                        self.fennec.jump_up()

                if self.octane.is_grounded:
                    self.octane.jumps_remaining = 2
                if jump_key_octane:
                    if self.octane.jumps_remaining == 1:  # can only flip if already used jump in air
                        if keys[pygame.K_LEFT]:
                            self.octane.flip_forward('left')
                        elif keys[pygame.K_RIGHT]:
                            self.octane.flip_forward('right')
                        else:
                            self.octane.jump_up()
                    else:  # first jump has to be up, not a flip
                        self.octane.jump_up()

            # collisions of objects
            if (objects_are_touching(self.fennec, self.octane) and
                    self.cooldown_fennec_and_octane[0] == 0):  # if cars are touching
                collision_set_new_velocities(self.fennec, self.octane)  # cars collide
                objects_collided_vertically(self.fennec, self.octane)  # fix vertical collisions
                objects_collided_vertically(self.octane, self.fennec)
                self.cooldown_fennec_and_octane[0] = 1
            if (objects_are_touching(self.octane, self.ball) and
                    self.cooldown_ball_and_octane[0] == 0):  # if self.octane and ball are touching
                collision_set_new_velocities(self.octane, self.ball)  # self.octane and self.ball collide
                objects_collided_vertically(self.octane, self.ball)
                objects_collided_vertically(self.ball, self.octane)
                self.cooldown_ball_and_octane[0] = 1
            if (objects_are_touching(self.ball, self.fennec) and
                    self.cooldown_ball_and_fennec[0] == 0):  # if self.fennec and ball touching
                collision_set_new_velocities(self.ball, self.fennec)  # self.fennec and ball collide
                objects_collided_vertically(self.ball, self.fennec)
                objects_collided_vertically(self.fennec, self.ball)
                self.cooldown_ball_and_fennec[0] = 1

            # collisions of objects into boundaries
            for obj in self.game_objects:
                if objects_are_touching(obj, self.left_wall) or objects_are_touching(obj, self.right_wall):
                    if not (obj == self.ball and self.hit_bottom_of_wall(obj)):
                        obj.vel_x = -obj.vel_x  # bounce off walls
                if self.hit_bottom_of_wall(obj) or objects_are_touching(obj, self.ceiling):
                    obj.vel_y *= -1
            if self.fennec.hitbox[0] < 0 or self.fennec.hitbox[0] + self.fennec.hitbox[2] > 1440:
                self.fennec.vel_x = -self.fennec.vel_x
            if self.octane.hitbox[0] < 0 or self.octane.hitbox[0] + self.octane.hitbox[2] > 1440:
                self.octane.vel_x = -self.octane.vel_x

            # if someone scores HERE
            if self.ball.hitbox[0] + self.ball.hitbox[2] < 0:  # if oranges scores in blue goal
                self.octane.score += 1
                self.octane.boost_left = min(100, self.octane.boost_left + 25)
                self.fennec.boost_left = min(100, self.fennec.boost_left + 50)
                if self.status == self.MAIN_GAME or self.status == self.TIME_RAN_OUT:
                    self.announce_chat('goal')
                    self.ball.reset()
                    self.fennec.reset()
                    self.octane.reset()
                elif self.status == self.OVERTIME:
                    self.status = self.GAME_OVER
                    self.game_over('orange')
                    break
            if self.ball.hitbox[0] > 1440:  # if blue scores in orange goal
                self.fennec.score += 1
                self.fennec.boost_left = min(100, self.fennec.boost_left + 25)
                self.octane.boost_left = min(100, self.octane.boost_left + 50)
                if self.status == self.MAIN_GAME or self.status == self.TIME_RAN_OUT:
                    self.announce_chat('goal')
                    self.ball.reset()
                    self.fennec.reset()
                    self.octane.reset()
                elif self.status == self.OVERTIME:
                    self.status = self.GAME_OVER
                    self.game_over('blue')
                    break

            # test
            if self.octane.x + self.octane.w < 0 or self.octane.x > 1440:
                self.octane.reset()
            if self.fennec.x + self.fennec.w < 0 or self.fennec.x > 1440:
                self.fennec.reset()

            if self.status == self.MAIN_GAME or self.status == self.TIME_RAN_OUT or self.status == self.OVERTIME:
                for obj in self.game_objects:  # accelerate all objects in both directions
                    self.take_gravity(obj)
                    obj.vel_x += obj.get_accel_x()
                    obj.vel_y += obj.get_accel_y()
                    obj.x += obj.vel_x
                    obj.y += obj.vel_y

            self.ball.update_hitbox()
            self.fennec.update_hitbox()
            self.octane.update_hitbox()
            self.redraw_game_window()

            # quick chats
            if len(self.quick_chats_blue) < self.quick_chat_limit:
                if chat_keys_blue[4]:
                    if len(self.quick_chats_blue) == self.quick_chat_limit - 1:
                        self.quick_chats_blue.append(self.choose_quick_chat('blue', 4))
                        self.quick_chats_blue_start_times.append(time.time())
                    else:
                        self.quick_chats_blue.append(self.choose_quick_chat('blue', 5))
                        self.quick_chats_blue_start_times.append(time.time())
                else:
                    press_anything = chat_keys_blue[0] or chat_keys_blue[1] or chat_keys_blue[2] or chat_keys_blue[3]
                    if self.blue_first_choice == -1:
                        if chat_keys_blue[0]:
                            self.blue_first_choice = 0
                        elif chat_keys_blue[1]:
                            self.blue_first_choice = 1
                        elif chat_keys_blue[2]:
                            self.blue_first_choice = 2
                        elif chat_keys_blue[3]:
                            self.blue_first_choice = 3
                    else:  # making second choice
                        if press_anything:
                            if len(self.quick_chats_blue) == self.quick_chat_limit - 1:
                                self.quick_chats_blue.append(self.choose_quick_chat('blue', 4))
                                self.quick_chats_blue_start_times.append(time.time())
                            else:
                                if chat_keys_blue[0]:  # left f
                                    self.quick_chats_blue.append(self.choose_quick_chat('blue', 0))
                                    self.quick_chats_blue_start_times.append(time.time())
                                elif chat_keys_blue[1]:  # up t
                                    self.quick_chats_blue.append(self.choose_quick_chat('blue', 1))
                                    self.quick_chats_blue_start_times.append(time.time())
                                elif chat_keys_blue[2]:  # down g
                                    self.quick_chats_blue.append(self.choose_quick_chat('blue', 2))
                                    self.quick_chats_blue_start_times.append(time.time())
                                elif chat_keys_blue[3]:  # right h
                                    self.quick_chats_blue.append(self.choose_quick_chat('blue', 3))
                                    self.quick_chats_blue_start_times.append(time.time())
                            self.blue_first_choice = -1

            if len(self.quick_chats_orange) < self.quick_chat_limit:
                if chat_keys_orange[4]:
                    if len(self.quick_chats_orange) == self.quick_chat_limit - 1:
                        self.quick_chats_orange.append(self.choose_quick_chat('orange', 4))
                        self.quick_chats_orange_start_times.append(time.time())
                    else:
                        self.quick_chats_orange.append(self.choose_quick_chat('orange', 5))
                        self.quick_chats_orange_start_times.append(time.time())
                else:
                    press_anything = (chat_keys_orange[0] or chat_keys_orange[1] or
                                      chat_keys_orange[2] or chat_keys_orange[3])
                    if self.orange_first_choice == -1:  # making first choice
                        if chat_keys_orange[0]:
                            self.orange_first_choice = 0
                        elif chat_keys_orange[1]:
                            self.orange_first_choice = 1
                        elif chat_keys_orange[2]:
                            self.orange_first_choice = 2
                        elif chat_keys_orange[3]:
                            self.orange_first_choice = 3
                    else:  # making second choice
                        if press_anything:
                            if len(self.quick_chats_orange) == self.quick_chat_limit - 1:
                                self.quick_chats_orange.append(self.choose_quick_chat('orange', 4))
                                self.quick_chats_orange_start_times.append(time.time())
                            else:
                                if chat_keys_orange[0]:  # left j
                                    self.quick_chats_orange.append(self.choose_quick_chat('orange', 0))
                                    self.quick_chats_orange_start_times.append(time.time())
                                elif chat_keys_orange[1]:  # up i
                                    self.quick_chats_orange.append(self.choose_quick_chat('orange', 1))
                                    self.quick_chats_orange_start_times.append(time.time())
                                elif chat_keys_orange[2]:  # down k
                                    self.quick_chats_orange.append(self.choose_quick_chat('orange', 2))
                                    self.quick_chats_orange_start_times.append(time.time())
                                elif chat_keys_orange[3]:  # right l
                                    self.quick_chats_orange.append(self.choose_quick_chat('orange', 3))
                                    self.quick_chats_orange_start_times.append(time.time())
                            self.orange_first_choice = -1

            self.manage_quick_chats()
            # ending countdown
            if self.end_countdown:
                if self.end_countdown_number >= 1:
                    self.draw_countdown(self.end_countdown_number, True)
                elif self.status == self.TIME_RAN_OUT:
                    self.draw_countdown(1, True)

            if self.status == self.GAME_OVER:
                if self.fennec.score > self.octane.score:
                    self.game_over('blue')
                    break
                elif self.octane.score > self.fennec.score:
                    self.game_over('orange')
                    break
                else:
                    self.game_over('tie')
                    self.status = self.OVERTIME
                    self.overtime_timer_beginning = time.time()  # starts overtime timer
                    self.ball.reset()
                    self.fennec.reset()
                    self.octane.reset()

            self.draw_quick_chats()
        self.reset()
        pygame.mixer.music.stop()
