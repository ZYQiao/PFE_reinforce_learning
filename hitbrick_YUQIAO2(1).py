# 导入模块
import pygame
from pygame.locals import *
import sys
import random
import time
import math
import numpy as np

INITIAL_EPSILON = 1.0
FINAL_EPSILON = 0.0001
GAMMA = 0.99
EPISODE = 10000
STEP = 1500
DELT_X = 50
ALPHA = 0.2
THRESHOLD = 0.001
DELTA = 0.0001
class GameWindow(object):
    '''Create the game window class'''

    def __init__(self, *args, **kw):
        self.window_length = 600
        self.window_wide = 500
        # Draw the game window, set the window size
        self.game_window = pygame.display.set_mode(
            (self.window_length, self.window_wide))
        # Set game window title
        pygame.display.set_caption("打砖块-Hit Bricks")
        # Define the game window background color parameters
        self.window_color = (135, 206, 250)

    def backgroud(self):
        # Paint game window background color
        self.game_window.fill(self.window_color)


class Ball(object):
    '''Create ball'''

    def __init__(self, *args, **kw):
        # Set the radius, color, moving speed parameters of the ball
        self.ball_color = (255, 215, 0)
        self.move_x = 1
        self.move_y = 1
        self.radius = 10
        self.brick = Brick()
        self.ball_x = self.window_length // 2
        self.ball_y = self.window_wide - self.rect_wide - self.radius

    def ballready(self):
        # Set the initial position of the ball
        self.ball_x = self.rect_x + self.rect_length // 2
        self.ball_y = self.window_wide - self.rect_wide - self.radius  # 游戏窗口宽度- 板子宽度- 球半径
        # Draw the ball, set the bounce trigger condition
        pygame.draw.circle(self.game_window, self.ball_color,
                           (self.ball_x, self.ball_y), self.radius)

    def ballmove(self):
        # Draw the ball, set the bounce trigger condition
        pygame.draw.circle(self.game_window, self.ball_color,
                           (self.ball_x, self.ball_y), self.radius)

        # Call the collision detection function
        self.ball_window()
        self.ball_rect()
        # print(self.ball_y)
        # Ball speed doubles for every 5 catches
        # if self.distance < self.radius:
        #     self.frequency += 1
        #     if self.frequency == 5:
        #         self.frequency = 0
        #         self.move_x += self.move_x
        #         self.move_y += self.move_y
        #         self.point += self.point
        # Set game failure conditions
        if self.ball_y >= self.window_wide - self.radius:
            self.ball_x += 0
            self.ball_y -= 0
            # self.gameover = self.over_font.render("Game Over", False, (0, 0, 0))
            # self.game_window.blit(self.gameover, (100, 280))  # (100,130) 代表数组的值
            self.over_sign = 1
        else:
            self.ball_x += self.move_x
            self.ball_y -= self.move_y

    def ballstate(self):
        return self.ball_x//10, self.ball_y//10, 0 if self.move_x > 0 else 1, 0 if self.move_y > 0 else 1
            ## 速度大于0，正向0，小于0，负向，0

    def ball_backpoint(self):  ## 返回球状态以及游戏是否结束 over_sign为1结束
        return self.ball_x, self.ball_y, self.move_x, self.move_y, self.over_sign

    def ball_backup(self, ball_x, ball_y, move_x, move_y, over_sign):
        self.ball_x, self.ball_y, self.move_x, self.move_y, self.over_sign = ball_x, ball_y, move_x, move_y, over_sign


class Rect(object):
    '''Create racket class'''

    def __init__(self, *args, **kw):
        # Set the racket color parameters
        self.rect_color = (255, 100, 0)
        self.rect_length = 100
        self.rect_wide = 10
        self.rect_x = 250

    def rectmove(self, delt_x=0):
        self.rect_x += delt_x
        # Draw the racket, define the horizontal boundary
        if self.rect_x >= self.window_length - self.rect_length:  # //整除
            self.rect_x = self.window_length - self.rect_length
        if self.rect_x <= 0:
            self.rect_x = 0
        pygame.draw.rect(self.game_window, self.rect_color, (  # The position of the top left corner of the racket
            self.rect_x, (self.window_wide - self.rect_wide), self.rect_length, self.rect_wide))
        # print("rect state",self.rect_x,(self.window_wide - self.rect_wide))

    def rectstate(self):
        return self.rect_x//DELT_X  ## 移动50一次
    def rect_backpoint(self):
        return self.rect_x 
    def rect_backup(self,rect_x):
        self.rect_x = rect_x

class Brick(object):
    def __init__(self, *args, **kw):
        # Set brick color parameters
        self.brick_color = (139, 126, 102)
        # Set whether there are bricks: 1 means yes, 0 means no
        self.brick_list = [[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0],
                           [1, 0, 0, 1, 0, 0, 1]]
        self.brick_length = 80
        self.brick_wide = 20

    def brickarrange(self):  # Set the position of the bricks
        for i in range(len(self.brick_list)):
            for j in range(len(self.brick_list[0])):
                self.brick_x = j * (self.brick_length + 5) + 5
                self.brick_y = i * (self.brick_wide + 20) + 40
                if self.brick_list[i][j] == 1:
                    # draw bricks
                    pygame.draw.rect(self.game_window, self.brick_color,
                                     (self.brick_x, self.brick_y, self.brick_length, self.brick_wide))
                    # Call the collision detection function
                    self.ball_brick()
                    if self.distanceb < self.radius:
                        self.brick_list[i][j] = 0
                        self.score += self.point
        # Set game win conditions
        if self.brick_list == [[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0]]:
            # self.win = self.win_font.render("You Win", False, (0, 0, 0))
            # self.game_window.blit(self.win, (100, 130))
            # self.win_sign = 0
            self.win_sign = 1

    def brickstate(self):
        bits = [self.brick_list[4][0], self.brick_list[4]
                [3], self.brick_list[4][6]]
        return bits[0]*4+bits[1]*2+bits[2]

    def brick_backpoint(self):
        return self.brick_list.copy(), self.win_sign

    def brick_backup(self, brick_list,win_sign):
        self.brick_list, self.win_sign = brick_list, win_sign

# class Reward(object):
#     def __init__(self,*args, **kw):
#         self.reward = 0
#         self.ball_rect_reward = 0.1
#         self.ball_brick_reward = 1
#         self.run_reward = -0.1
        
#     def getreward(self):
#         return self.reward

class Score(object):
    '''Create a fraction class'''

    def __init__(self, *args, **kw):
        # set initial score
        self.score = 0
        # set fraction font
        self.score_font = pygame.font.SysFont('arial', 22)
        # Set the initial bonus points
        self.point = 1
        # Set initial catch count
        self.frequency = 0

    def countscore(self):
        # Plot the player score
        my_score = self.score_font.render(
            "Score: "+str(self.score), False, (255, 255, 255))
        self.game_window.blit(my_score, (500, 10))


class BricksCount(object):
    "Create a technology block class"

    def __init__(self, *args, **kw):
        self.bricks_font = pygame.font.SysFont('arial', 22)
        self.list = np.array(self.brick_list)
        self.bricks = len(self.list.ravel()[np.flatnonzero(self.list)])

    def countbricks(self):
        self.list = np.array(self.brick_list)
        self.bricks = len(self.list.ravel()[np.flatnonzero(self.list)])
        brick_num = self.bricks_font.render(
            "Bricks: "+str(self.bricks), False, (255, 255, 255))
        self.game_window.blit(brick_num, (350, 10))


class GameOver(object):
    '''Create a game over class'''

    def __init__(self, *args, **kw):
        # Set Game Over font
        self.over_font = pygame.font.SysFont('arial', 80)
        # Define the GameOver logo
        self.over_sign = 2


class Win(object):
    '''Create a game victory class'''

    def __init__(self, *args, **kw):
        # Set You Win font
        self.win_font = pygame.font.SysFont('arial', 80)
        #Define Win ID
        self.win_sign = 0


class Collision(object):
    '''Collision detection class'''

    # Collision detection between ball and window border
    def ball_window(self):
        if self.ball_x <= self.radius or self.ball_x >= (self.window_length - self.radius):
            self.move_x = -self.move_x
        if self.ball_y <= self.radius:
            self.move_y = -self.move_y

    # Ball and racket collision detection

    def ball_rect(self):
        ball_rect_reward = 0.1
        #Define Collision IDs
        self.collision_sign_x = 0
        self.collision_sign_y = 0

        if self.ball_x < self.rect_x:  # The ball is on the left side of the board
            self.closestpoint_x = self.rect_x
            self.collision_sign_x = 1
        elif self.ball_x > (self.rect_x + self.rect_length):  # The ball is on the right side of the board
            self.closestpoint_x = self.rect_x + self.rect_length
            self.collision_sign_x = 2
        else:
            self.closestpoint_x = self.ball_x   # The ball is above the middle of the board
            self.collision_sign_x = 3

        if self.ball_y < (self.window_wide - self.rect_wide):  # The ball is above the board
            self.closestpoint_y = (self.window_wide - self.rect_wide)
            self.collision_sign_y = 1
        elif self.ball_y > self.window_wide:  # the ball is under the board
            self.closestpoint_y = self.window_wide
            self.collision_sign_y = 2
        else:
            self.closestpoint_y = self.ball_y  # The ball is within the width of the board
            self.collision_sign_y = 3
        # Define the distance between the closest point of the racket to the center of the circle and the center of the circle
        self.distance = math.sqrt(
            math.pow(self.closestpoint_x - self.ball_x, 2) + math.pow(self.closestpoint_y - self.ball_y, 2))
        # Collision detection for three situations in which the ball is on the top left, top middle and top right of the racket
        if self.distance < self.radius and self.collision_sign_y == 1 and (
                self.collision_sign_x == 1 or self.collision_sign_x == 2):
            if self.collision_sign_x == 1 and self.move_x > 0:
                self.move_x = - self.move_x
                self.move_y = - self.move_y
            if self.collision_sign_x == 1 and self.move_x < 0:
                self.move_y = - self.move_y
            if self.collision_sign_x == 2 and self.move_x < 0:
                self.move_x = - self.move_x
                self.move_y = - self.move_y
            if self.collision_sign_x == 2 and self.move_x > 0:
                self.move_y = - self.move_y
                
            self.ball_rect_reward = ball_rect_reward 
            
        if self.distance < self.radius and self.collision_sign_y == 1 and self.collision_sign_x == 3:
            self.move_y = - self.move_y
            
            self.ball_rect_reward = ball_rect_reward 
        # Collision detection of the ball between the left and right sides of the racket
        if self.distance < self.radius and self.collision_sign_y == 3:
            self.move_x = - self.move_x
            
            self.ball_rect_reward = ball_rect_reward 
        

    # Collision detection between balls and bricks
    def ball_brick(self):
        # Define Collision IDs
        self.collision_sign_bx = 0
        self.collision_sign_by = 0

        if self.ball_x < self.brick_x:  #The ball is to the left of the brick
            self.closestpoint_bx = self.brick_x
            self.collision_sign_bx = 1
        elif self.ball_x > self.brick_x + self.brick_length:  # The ball is to the right of the brick
            self.closestpoint_bx = self.brick_x + self.brick_length
            self.collision_sign_bx = 2
        else:   # 球在砖块中间
            self.closestpoint_bx = self.ball_x
            self.collision_sign_bx = 3

        if self.ball_y < self.brick_y:    # the ball is above the brick
            self.closestpoint_by = self.brick_y
            self.collision_sign_by = 1
        elif self.ball_y > self.brick_y + self.brick_wide:  # the ball is under the brick
            self.closestpoint_by = self.brick_y + self.brick_wide
            self.collision_sign_by = 2
        else:   #ball between bricks
            self.closestpoint_by = self.ball_y
            self.collision_sign_by = 3
        # Defines the distance from the brick to the closest point to the center of the circle
        self.distanceb = math.sqrt(
            math.pow(self.closestpoint_bx - self.ball_x, 2) + math.pow(self.closestpoint_by - self.ball_y, 2))
        # Collision detection for three situations where the ball is on the brick, left, middle, and right
        if self.distanceb < self.radius and self.collision_sign_by == 1 and (
                self.collision_sign_bx == 1 or self.collision_sign_bx == 2):
            if self.collision_sign_bx == 1 and self.move_x > 0:
                self.move_x = - self.move_x
                self.move_y = - self.move_y
            if self.collision_sign_bx == 1 and self.move_x < 0:
                self.move_y = - self.move_y
            if self.collision_sign_bx == 2 and self.move_x < 0:
                self.move_x = - self.move_x
                self.move_y = - self.move_y
            if self.collision_sign_bx == 2 and self.move_x > 0:
                self.move_y = - self.move_y
        if self.distanceb < self.radius and self.collision_sign_by == 1 and self.collision_sign_bx == 3:
            self.move_y = - self.move_y
        # The collision detection of the ball under the brick left, middle, and right
        if self.distanceb < self.radius and self.collision_sign_by == 2 and (
                self.collision_sign_bx == 1 or self.collision_sign_bx == 2):
            if self.collision_sign_bx == 1 and self.move_x > 0:
                self.move_x = - self.move_x
                self.move_y = - self.move_y
            if self.collision_sign_bx == 1 and self.move_x < 0:
                self.move_y = - self.move_y
            if self.collision_sign_bx == 2 and self.move_x < 0:
                self.move_x = - self.move_x
                self.move_y = - self.move_y
            if self.collision_sign_bx == 2 and self.move_x > 0:
                self.move_y = - self.move_y
        if self.distanceb < self.radius and self.collision_sign_by == 2 and self.collision_sign_bx == 3:
            self.move_y = - self.move_y
        # 球在砖块左、右两侧中间的碰撞检测
        if self.distanceb < self.radius and self.collision_sign_by == 3:
            self.move_x = - self.move_x


class Main(GameWindow, Rect, Ball, Brick, Collision, Score, BricksCount, Win, GameOver):
    '''创建主程序类'''

    def __init__(self, *args, **kw):
        super(Main, self).__init__(*args, **kw)
        super(GameWindow, self).__init__(*args, **kw)
        super(Rect, self).__init__(*args, **kw)
        super(Ball, self).__init__(*args, **kw)
        super(Brick, self).__init__(*args, **kw)
        super(Collision, self).__init__(*args, **kw)
        super(Score, self).__init__(*args, **kw)
        super(BricksCount, self).__init__(*args, **kw)
        super(Win, self).__init__(*args, **kw)
        # self.init_states()
        # 定义游戏开始标识
        self.start_sign = 0
        pygame.key.set_repeat(10, 15)
        while True:
            self.backgroud()  #Paint game window background color
            self.rectmove()  # Set the racket range of motion
            self.countscore()  #Calculate the score
            self.countbricks()  # count bricks
            # Get game window state
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.start_sign = 1
                    elif event.key == pygame.K_RIGHT:
                        self.rectmove(DELT_X)  # Set the racket range of motion
                    elif event.key == pygame.K_LEFT:
                        self.rectmove(-DELT_X)  # Set the racket range of motion
                    elif event.key == pygame.K_ESCAPE:
                        sys.exit()
                    elif event.key == pygame.K_RETURN:
                        if self.over_sign == 1 or self.win_sign == 1:
                            super(Main, self).__init__(*args, **kw)
                            super(GameWindow, self).__init__(*args, **kw)
                            super(Rect, self).__init__(*args, **kw)
                            super(Ball, self).__init__(*args, **kw)
                            super(Brick, self).__init__(*args, **kw)
                            super(Collision, self).__init__(*args, **kw)
                            super(Score, self).__init__(*args, **kw)
                            super(BricksCount, self).__init__(*args, **kw)
                            super(Win, self).__init__(*args, **kw)
                            # Define the game start flag
                            start_sign = 0
            if self.start_sign == 0:
                self.ballready()
            else:
                self.c()

            self.brickarrange()
            # Update game window
            pygame.display.update()
            # Control how often the game window refreshes
            time.sleep(0.010)
            
class Train(GameWindow, Rect, Ball, Brick, Collision, Score, BricksCount, Win, GameOver):
    '''Create a trainer class'''

    def __init__(self, *args, **kw):
        super(Train, self).__init__(*args, **kw)
        super(GameWindow, self).__init__(*args, **kw)
        super(Rect, self).__init__(*args, **kw)
        super(Ball, self).__init__(*args, **kw)
        super(Brick, self).__init__(*args, **kw)
        super(Collision, self).__init__(*args, **kw)
        super(Score, self).__init__(*args, **kw)
        super(BricksCount, self).__init__(*args, **kw)
        super(Win, self).__init__(*args, **kw)
        total_reward_decade = 0
        self.epsilon = INITIAL_EPSILON
        self.ball_rect_reward = 0
        self.init_values()
        for episode in range(EPISODE):
            super(Train, self).__init__(*args, **kw)
            super(GameWindow, self).__init__(*args, **kw)
            super(Rect, self).__init__(*args, **kw)
            super(Ball, self).__init__(*args, **kw)
            super(Brick, self).__init__(*args, **kw)
            super(Collision, self).__init__(*args, **kw)
            super(Score, self).__init__(*args, **kw)
            super(BricksCount, self).__init__(*args, **kw)
            super(Win, self).__init__(*args, **kw)
            state = self.getstate()
            total_reward = 0
            # self.ballmove()
            pygame.key.set_repeat(10, 15)
            # Define the game start flag
            self.start_sign = 1
            done = False
            for step in range(STEP):
                self.backgroud()  # Paint game window background color
                self.rectmove()  # Set the racket range of motion
                self.countscore()  # Calculate the score
                self.countbricks()  # count bricks
                # #获取游戏窗口状态
                # if self.start_sign == 0:
                #     self.ballready()
                # else:
                #     self.ballmove()

                self.brickarrange()
                # Update game window
                # pygame.display.update()
                # # Control how often the game window refreshes
                # time.sleep(0.010)
                self.ball_rect_reward = 0
                action = self.get_action(state)
                (bs_x_,bs_y_,bs_m_x_,bs_m_y_,rs_,brs_) = state
                next_state, reward, done, _ = self.step(action)
                (bs_x,bs_y,bs_m_x,bs_m_y,rs,brs) = next_state

                # Update game window
                pygame.display.update()
                # Control how often the game window refreshes
                time.sleep(0.010)


                print(reward)
                self.values[bs_x_][bs_y_][bs_m_x_][bs_m_y_][rs_][brs_][action]+=ALPHA*(reward+
                                                                               GAMMA*max(self.values[bs_x][bs_y][bs_m_x][bs_m_y][rs][brs][0],
                                                                                         self.values[bs_x][bs_y][bs_m_x][bs_m_y][rs][brs][1])-
                                                                               self.values[bs_x_][bs_y_][bs_m_x_][bs_m_y_][rs_][brs_][action])
                
                state = next_state
                total_reward += reward
                if done :
                    break
                
            print('Episode:', episode, 'Total Point this Episode is:', total_reward)
            total_reward_decade += total_reward
            if episode % 10 == 0:
                print('-------------')
                print('Decade:', episode / 10, 'Total Reward in this Decade is:', total_reward_decade)
                print('-------------')
                total_reward_decade = 0

    
    def init_values(self):
        self.values = np.zeros((581, 481, 2, 2, 11, 8, 2))#ball_x,ball_y,move_x,move_y,rect_x,brick_list,action
        # print(self.values)

    def backpoint(self):
        self.backpoint =[[self.ball_backpoint()],
                        [self.brick_backpoint()],
                        [self.rect_backpoint()]]
        
    def backup(self):
        self.ball_backup(self.backpoint[0][0],self.backpoint[0][1],self.backpoint[0][2],self.backpoint[0][3],self.backpoint[0][4])
        self.brick_backup(self.backpoint[1][0],self.backpoint[1][1])
        self.rect_backup(self.backpoint[2][0])
        
    def getstate(self):
        bs_x, bs_y, bs_m_x, bs_m_y = self.ballstate()
        rs = self.rectstate()
        brs = self.brickstate()
        return (bs_x,bs_y,bs_m_x,bs_m_y,rs,brs)
    
    def step(self, action):
        done = False
        reward = -0.01
        # backpoint = self.backpoint()
        (bs_x_,bs_y_,bs_m_x_,bs_m_y_,rs_,brs_) = self.getstate()
        if action == 0:  # 等于0 负向移动，1 正向移动
            self.rectmove(-DELT_X)
        elif action == 1:
            self.rectmove(DELT_X)

        if self.start_sign == 0:
            self.ballready()
        else:
            self.ballmove()
        self.brickarrange()
        

        (bs_x,bs_y,bs_m_x,bs_m_y,rs,brs) = self.getstate()
        next_state = (bs_x,bs_y,bs_m_x,bs_m_y,rs,brs)
        if brs < brs_:
            reward = 2
        elif self.ball_rect_reward > 0:  # reward 0.1
            reward = self.ball_rect_reward 
        elif self.over_sign == 1:
            reward = -1
    
        if self.win_sign == 1 or self.over_sign == 1:
            done = True
        info = {'score':'the score is:'+str(self.score),
                'done':done}
        # print(info)
        # self.backup(backpoint)
                                                                               
        return next_state, reward, done, info

    def get_greedy_action(self, state):
        (bs_x,bs_y,bs_m_x,bs_m_y,rs,brs) = state
        return 0 if self.values[bs_x][bs_y][bs_m_x][bs_m_y][rs][brs][0] >= self.values[bs_x][bs_y][bs_m_x][bs_m_y][rs][brs][1] else 1


    def get_action(self, state):
        if self.epsilon >= FINAL_EPSILON:
            self.epsilon -= (INITIAL_EPSILON - FINAL_EPSILON) / 10000

        if random.random() < self.epsilon:
            action = random.randint(0, 1)
        else:
            action = self.get_greedy_action(state)

        return action



## Value iteration

class Value_iteration(GameWindow, Rect, Ball, Brick, Collision, Score, BricksCount, Win, GameOver):
    '''Create a trainer class'''

    def __init__(self, *args, **kw):
        super(Train, self).__init__(*args, **kw)
        super(GameWindow, self).__init__(*args, **kw)
        super(Rect, self).__init__(*args, **kw)
        super(Ball, self).__init__(*args, **kw)
        super(Brick, self).__init__(*args, **kw)
        super(Collision, self).__init__(*args, **kw)
        super(Score, self).__init__(*args, **kw)
        super(BricksCount, self).__init__(*args, **kw)
        super(Win, self).__init__(*args, **kw)
        total_reward_decade = 0
        self.epsilon = INITIAL_EPSILON
        self.ball_rect_reward = 0
        self.init_P()
        self.init_values()
        for episode in range(EPISODE):
            super(Train, self).__init__(*args, **kw)
            super(GameWindow, self).__init__(*args, **kw)
            super(Rect, self).__init__(*args, **kw)
            super(Ball, self).__init__(*args, **kw)
            super(Brick, self).__init__(*args, **kw)
            super(Collision, self).__init__(*args, **kw)
            super(Score, self).__init__(*args, **kw)
            super(BricksCount, self).__init__(*args, **kw)
            super(Win, self).__init__(*args, **kw)
            state = self.getstate()
            pygame.key.set_repeat(10, 15)
            # Define the game start flag
            self.start_sign = 1
            done = False
            for step in range(STEP):
                self.backgroud()  # Paint game window background color
                self.rectmove()  # Set the racket range of motion
                self.countscore()  # Calculate the score
                self.countbricks()  # count bricks
                # 获取游戏窗口状态
                if self.start_sign == 0:
                    self.ballready()
                else:
                    self.ballmove()

                self.brickarrange()
                # Update game window
                pygame.display.update()
                # Control how often the game window refreshes
                time.sleep(0.010)
                self.ball_rect_reward = 0
                for i in range(581):
                    for j in range(481):
                        for k in range(2):
                            for m in range(2):
                                for n in range(11):
                                    for t in range(8):
                                        if t != 0:
                                            Values_temp = self.values









    def init_P(self):
        self.P = np.zeros((581, 481, 2, 2, 11, 8, 2))

    def transition_P(self, state, action):
        self.P = np.zeros_like(self.P)
        if action == 0:  # 等于0 负向移动，1 正向移动
            self.rectmove(-DELT_X)

        elif action == 1:
            self.rectmove(DELT_X)
        (bs_x,bs_y,bs_m_x,bs_m_y,rs,brs) = state
        self.P[bs_x][bs_y][bs_m_x][bs_m_y][rs][brs][action]=1
        return self.P[bs_x][bs_y][bs_m_x][bs_m_y][rs][brs][action],state

    def init_values(self):
        self.values = np.zeros((581, 481, 2, 2, 11, 8))



if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    catchball = Train()
    # catchball = Main()
