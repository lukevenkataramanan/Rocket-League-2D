from objects import *
from Game import Game
import pygame

if __name__ == '__main__':
    print('Welcome, user.')
    pygame.display.set_caption("Rocket League 2D")  # set title of window
    game_window = pygame.display.set_mode((1440, 800))  # create full screen window
    ball_image = pygame.image.load('images/ball.png')
    fennec_images = [pygame.image.load('images/fennec_left.png'),  # in website, did 86x60
                     pygame.image.load('images/fennec_right.png'),
                     pygame.image.load('images/fennec_boost_left.png'),
                     pygame.image.load('images/fennec_boost_right.png'),
                     pygame.image.load('images/fennec_hover.png')]
    octane_images = [pygame.image.load('images/octane_left.png'),  # load octane image
                     pygame.image.load('images/octane_right.png'),
                     pygame.image.load('images/octane_boost_left.png'),
                     pygame.image.load('images/octane_boost_right.png'),
                     pygame.image.load('images/octane_hover.png')]
    game_ball_template = Ball(window=game_window, x=720, y=200, radius=30, mass=1, image=ball_image,
                              gravity=1, friction=.35, elasticity=.8)
    game_fennec_template = Car(window=game_window, x=200, y=645, w=86, h=35, mass=3, images=fennec_images,
                               gravity=1, friction=.35, elasticity=.1, thrust=1.5, facing='right')  # create fennec
    game_octane_template = Car(window=game_window, x=1190, y=645, w=86, h=35, mass=3, images=octane_images,
                               gravity=1, friction=.35, elasticity=.1, thrust=1.5, facing='left')  # create octane

    master_run = True
    while master_run:
        game_ball = game_ball_template
        game_fennec = game_fennec_template
        game_octane = game_octane_template

        game = Game(window=game_window, ball=game_ball, fennec=game_fennec, octane=game_octane,
                    total_time=45, frame_rate=30)
        master_run = game.master_run
pygame.quit()
