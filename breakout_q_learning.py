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
THRESHOLD = 0.01
DELTA = 0.0001

class Q_learning():
    '''Create a Q_learning class'''

    def __init__(self, *args, **kw):
        super(Q_learning, self).__init__(*args, **kw)
        
        self.window_length = 600
        self.window_wide = 500
        self.move_x = 5
        self.move_y = 5
        self.radius = 10
        self.rect_length = 100
        self.rect_move_x = 50
        self.rect_wide = 10
        self.brick_length = 80
        self.brick_wide = 20
        self.bricks_x = [5,260,515]
        self.bricks_y = 200
        self.over_sign = 0
        self.win_sign = 0
        self.epsilon = INITIAL_EPSILON

        
        
        
        self.ball_x_sate = int((self.window_length-2*self.radius)/self.move_x)+1 #ball state depends on x position(59 position)
        self.ball_y_sate = int((self.window_wide-2*self.radius)/self.move_y)+1 #ball state depends on y position(49 position)
        self.ball_move_x_state = 2 #ball state depends on x move speed(2 direction left right)
        self.ball_move_y_state = 2 #ball state depends on y move speed(2 direction up down)
        self.rect_state = int((self.window_length-self.rect_length)/self.rect_move_x)+1 #paddle state depends on move spped(11 position)
        self.brick_state = 8 #3 bircks has 8 state (111 110 101 100 011 010 001 000)
        self.ball_x_po = [_ for _ in range(self.radius, self.window_length-self.radius+self.move_x, self.move_x)] #ball x position(10,20,30...590)
        self.ball_y_po = [_ for _ in range(self.radius, self.window_wide-self.radius+self.move_y, self.move_y)] #ball y position(10,20,30...490)
        self.n_action = 3
        
        self.bs_x, self.bs_y, self.bs_m_x, self.bs_m_y = len(self.ball_x_po)//2, len(self.ball_y_po)-2, 0, 0
        self.rs = self.rect_state//2
        self.brs = 7
        
        self.values = np.zeros((self.ball_x_sate, self.ball_y_sate, self.ball_move_x_state, self.ball_move_y_state, self.rect_state, self.brick_state, self.n_action))
        
        
    def cal_state(self, state_iter):
        brs_tmp = state_iter%self.brick_state
        rs_tmp = int(state_iter/self.brick_state)%self.rect_state
        bs_m_y_tmp = int((state_iter/self.brick_state)/self.rect_state)%self.ball_move_y_state
        bs_m_x_tmp = int(((state_iter/self.brick_state)/self.rect_state)/self.ball_move_y_state)%self.ball_move_x_state
        bs_y_tmp = int((((state_iter/self.brick_state)/self.rect_state)/self.ball_move_y_state)/self.ball_move_x_state)%self.ball_y_sate
        bs_x_tmp = int(((((state_iter/self.brick_state)/self.rect_state)/self.ball_move_y_state)/self.ball_move_x_state)/self.ball_y_sate)%self.ball_x_sate
        return (bs_x_tmp, bs_y_tmp, bs_m_x_tmp, bs_m_y_tmp, rs_tmp, brs_tmp)
        
    def save_values(self,file_path):
        np.save(file_path, self.values)
    
    def load_values(self, file_path):
        self.values = np.load(file_path)
        
    def rect_move(self, rs, action):
        if action == 0 and rs != 0:
            rs = rs - 1
        if action == 1 and rs != 10:
            rs = rs + 1
        return rs
    
    def ball_ready(self, rs):
        ball_x = rs*self.rect_move_x + self.rect_length//2
        bs_x =  ball_x//self.move_x - 1
        return bs_x
    
    # Collision detection between balls and window
    def ball_window(self, bs_x, bs_y, bs_m_x, bs_m_y):
        ball_x, ball_y = self.ball_x_po[bs_x], self.ball_y_po[bs_y]
        move_x = self.move_x if bs_m_x == 0 else -self.move_x
        move_y = -self.move_y if bs_m_y == 0 else self.move_y
        if (ball_x <= self.radius and move_x < 0) or (ball_x >= (self.window_length - self.radius) and move_x > 0):
            move_x = -move_x
        if ball_y <= self.radius and move_y < 0:
            move_y = -move_y
        bs_m_x = 0 if move_x > 0 else 1
        bs_m_y = 0 if move_y < 0 else 1
        return bs_m_x, bs_m_y
    
    # Collision detection between balls and paddle  
    def ball_rect(self, bs_x, bs_y, bs_m_x, bs_m_y, rs):
        ball_rect_reward = 0.5
        ball_rect_reward = 0
        # Define Collision IDs
        collision_sign_x = 0
        collision_sign_y = 0
        ball_x, ball_y = self.ball_x_po[bs_x], self.ball_y_po[bs_y]
        move_x = self.move_x if bs_m_x == 0 else -self.move_x
        move_y = -self.move_y if bs_m_y == 0 else self.move_y
        rect_x = rs*self.rect_move_x + self.rect_length
        
        if ball_x < rect_x:  # The ball is on the left side of the board
            closestpoint_x = rect_x
            collision_sign_x = 1
        elif ball_x > (rect_x + self.rect_length):  # The ball is on the right side of the board
            closestpoint_x = rect_x + self.rect_length
            collision_sign_x = 2
        else:
            closestpoint_x = ball_x  # The ball is above the middle of the board
            collision_sign_x = 3

        if ball_y < (self.window_wide - self.rect_wide):  # The ball is above the board
            closestpoint_y = (self.window_wide - self.rect_wide)
            collision_sign_y = 1
        elif ball_y > self.window_wide:  # the ball is under the board
            closestpoint_y = self.window_wide
            collision_sign_y = 2
        else:
            closestpoint_y = ball_y  # The ball is within the width of the board
            collision_sign_y = 3
        # Define the distance between the closest point of the racket to the center of the circle and the center of the circle
        distance = math.sqrt(
            math.pow(closestpoint_x - ball_x, 2) + math.pow(closestpoint_y - ball_y, 2))
        # Collision detection for three situations in which the ball is on the top left, top middle and top right of the racket
        if distance < self.radius and collision_sign_y == 1 and (
                collision_sign_x == 1 or collision_sign_x == 2):
            if collision_sign_x == 1 and move_x > 0:
                move_x = - move_x
                move_y = - move_y
            if collision_sign_x == 1 and move_x < 0:
                move_y = - move_y
            if collision_sign_x == 2 and move_x < 0:
                move_x = - move_x
                move_y = - move_y
            if collision_sign_x == 2 and move_x > 0:
                move_y = - move_y

            ball_rect_reward = ball_rect_reward

        if distance < self.radius and collision_sign_y == 1 and collision_sign_x == 3:
            move_y = - move_y
            
            ball_rect_reward = ball_rect_reward
            # Collision detection of the ball between the left and right sides of the racket
        if distance < self.radius and collision_sign_y == 3:
            move_x = - move_x
            
            ball_rect_reward = ball_rect_reward
        bs_m_x = 0 if move_x > 0 else 1
        bs_m_y = 0 if move_y < 0 else 1
        
        return bs_m_x, bs_m_y, ball_rect_reward
    
    # Collision detection between balls and bricks  
    def ball_brick(self, bs_x, bs_y, bs_m_x, bs_m_y, brick_x, brick_y):
        # Define Collision IDs
        ball_brick_reward = 2
        ball_brick_reward = 0
        collision_sign_bx = 0
        collision_sign_by = 0
        ball_x, ball_y = self.ball_x_po[bs_x], self.ball_y_po[bs_y]
        move_x = self.move_x if bs_m_x == 0 else -self.move_x
        move_y = -self.move_y if bs_m_y == 0 else self.move_y
        
        if ball_x < brick_x:  # The ball is to the left of the brick
            closestpoint_bx = brick_x
            collision_sign_bx = 1
        elif ball_x > brick_x + self.brick_wide:  # The ball is to the right of the brick
            closestpoint_bx = brick_x + self.brick_wide
            collision_sign_bx = 2
        else:  # ball between bricks
            closestpoint_bx = ball_x
            collision_sign_bx = 3

        if ball_y < brick_y:  # the ball is above the brick
            closestpoint_by = brick_y
            collision_sign_by = 1
        elif ball_y > brick_y + self.brick_wide:  # the ball is under the brick
            closestpoint_by = brick_y + self.brick_wide
            collision_sign_by = 2
        else:  # ball between bricks
            closestpoint_by = ball_y
            collision_sign_by = 3
        # Defines the distance from the brick to the closest point to the center of the circle
        distanceb = math.sqrt(
            math.pow(closestpoint_bx - ball_x, 2) + math.pow(closestpoint_by - ball_y, 2))
        # Collision detection for three situations where the ball is on the brick, left, middle, and right
        if distanceb < self.radius and collision_sign_by == 1 and (
                collision_sign_bx == 1 or collision_sign_bx == 2):
            if collision_sign_bx == 1 and move_x > 0:
                move_x = - move_x
                move_y = - move_y
            if collision_sign_bx == 1 and move_x < 0:
                move_y = - move_y
            if collision_sign_bx == 2 and move_x < 0:
                move_x = - move_x
                move_y = - move_y
            if collision_sign_bx == 2 and move_x > 0:
                move_y = - move_y
                
            ball_brick_reward = ball_brick_reward
        if distanceb < self.radius and collision_sign_by == 1 and collision_sign_bx == 3:
            move_y = - move_y
            
            ball_brick_reward = ball_brick_reward
        # The collision detection of the ball under the brick left, middle, and right
        if distanceb < self.radius and collision_sign_by == 2 and (
                collision_sign_bx == 1 or collision_sign_bx == 2):
            if collision_sign_bx == 1 and move_x > 0:
                move_x = - move_x
                move_y = - move_y
            if collision_sign_bx == 1 and move_x < 0:
                move_y = - move_y
            if collision_sign_bx == 2 and move_x < 0:
                move_x = - move_x
                move_y = - move_y
            if collision_sign_bx == 2 and move_x > 0:
                move_y = - move_y
                
            ball_brick_reward = ball_brick_reward
        if distanceb < self.radius and collision_sign_by == 2 and collision_sign_bx == 3:
            move_y = - move_y
            ball_brick_reward = ball_brick_reward
        # 球在砖块左、右两侧中间的碰撞检测
        if distanceb < self.radius and collision_sign_by == 3:
            move_x = - move_x
            ball_brick_reward = ball_brick_reward
            
        bs_m_x = 0 if move_x > 0 else 1
        bs_m_y = 0 if move_y < 0 else 1
        
        return bs_m_x, bs_m_y, ball_brick_reward
    
    def ball_move(self, bs_x, bs_y, bs_m_x, bs_m_y, rs):
        bs_m_x, bs_m_y = self.ball_window(bs_x, bs_y, bs_m_x, bs_m_y)
        bs_m_x, bs_m_y, ball_rect_reward = self.ball_rect(bs_x, bs_y, bs_m_x, bs_m_y, rs)
        
        ball_x, ball_y = self.ball_x_po[bs_x], self.ball_y_po[bs_y]
        
        move_x = self.move_x if bs_m_x == 0 else -self.move_x
        move_y = -self.move_y if bs_m_y == 0 else self.move_y
        
        if ball_y >= self.window_wide - self.radius:
            ball_x += 0
            ball_y -= 0
            print("game_over")
            self.over_sign = 1
        else:
            ball_x += move_x
            ball_y += move_y
        
        bs_x, bs_y = self.ball_x_po.index(ball_x), self.ball_y_po.index(ball_y)
        
        return bs_x, bs_y, ball_rect_reward
    
    def cal_reward(self, state, action):
        (bs_x, bs_y, bs_m_x, bs_m_y, rs, brs) = state
        reward, ball_rect_reward, ball_brick_reward = 0,0,0 #ball_rect_reward is ball rect reward, ball_brick_reward is ball brick reward
        rs = self.rect_move(rs, action)
        if self.start_sign == 0:
            bs_x = self.ballready(rs)
            return (bs_x, bs_y, bs_m_x, bs_m_y, rs, brs), reward
        bs_x, bs_y, ball_rect_reward = self.ball_move(bs_x, bs_y, bs_m_x, bs_m_y, rs)

        
        # Collision detection between balls and bricks
        if brs == 1:
            bs_m_x, bs_m_y, ball_brick_reward = self.ball_brick(bs_x, bs_y, bs_m_x, bs_m_y, self.bricks_x[2], self.bricks_y)
            if ball_brick_reward > 0:
                brs = 0
        elif brs == 2:
            bs_m_x, bs_m_y, ball_brick_reward = self.ball_brick(bs_x, bs_y, bs_m_x, bs_m_y, self.bricks_x[1], self.bricks_y)
            if ball_brick_reward > 0:
                brs = 0
        elif brs == 3:
            bs_m_x1, bs_m_y1, ball_brick_reward1 = self.ball_brick(bs_x, bs_y, bs_m_x, bs_m_y, self.bricks_x[1], self.bricks_y)
            bs_m_x2, bs_m_y2, ball_brick_reward2 = self.ball_brick(bs_x, bs_y, bs_m_x, bs_m_y, self.bricks_x[2], self.bricks_y)
            if ball_brick_reward1 > 0:
                ball_brick_reward = ball_brick_reward1
                bs_m_x, bs_m_y = bs_m_x1, bs_m_y1
                brs = 1
            elif ball_brick_reward2 > 0:
                ball_brick_reward = ball_brick_reward2
                bs_m_x, bs_m_y = bs_m_x2, bs_m_y2
                brs = 2
        elif brs == 4:
            bs_m_x1, bs_m_y1, ball_brick_reward1 = self.ball_brick(bs_x, bs_y, bs_m_x, bs_m_y, self.bricks_x[0], self.bricks_y)
            if ball_brick_reward > 0:
                brs = 0
        elif brs == 5:
            bs_m_x1, bs_m_y1, ball_brick_reward1 = self.ball_brick(bs_x, bs_y, bs_m_x, bs_m_y, self.bricks_x[0], self.bricks_y)
            bs_m_x2, bs_m_y2, ball_brick_reward2 = self.ball_brick(bs_x, bs_y, bs_m_x, bs_m_y, self.bricks_x[2], self.bricks_y)
            if ball_brick_reward1 > 0:
                ball_brick_reward = ball_brick_reward1
                bs_m_x, bs_m_y = bs_m_x1, bs_m_y1
                brs = 4
            elif ball_brick_reward2 > 0:
                ball_brick_reward = ball_brick_reward2
                bs_m_x, bs_m_y = bs_m_x2, bs_m_y2
                brs = 1
        elif brs == 6:
            bs_m_x1, bs_m_y1, ball_brick_reward1 = self.ball_brick(bs_x, bs_y, bs_m_x, bs_m_y, self.bricks_x[0], self.bricks_y)
            bs_m_x2, bs_m_y2, ball_brick_reward2 = self.ball_brick(bs_x, bs_y, bs_m_x, bs_m_y, self.bricks_x[1], self.bricks_y)
            if ball_brick_reward1 > 0:
                ball_brick_reward = ball_brick_reward1
                bs_m_x, bs_m_y = bs_m_x1, bs_m_y1
                brs = 2
            elif ball_brick_reward2 > 0:
                ball_brick_reward = ball_brick_reward2
                bs_m_x, bs_m_y = bs_m_x2, bs_m_y2
                brs = 4
        elif brs == 7:
            bs_m_x1, bs_m_y1, ball_brick_reward1 = self.ball_brick(bs_x, bs_y, bs_m_x, bs_m_y, self.bricks_x[0], self.bricks_y)
            bs_m_x2, bs_m_y2, ball_brick_reward2 = self.ball_brick(bs_x, bs_y, bs_m_x, bs_m_y, self.bricks_x[1], self.bricks_y)
            bs_m_x3, bs_m_y3, ball_brick_reward3 = self.ball_brick(bs_x, bs_y, bs_m_x, bs_m_y, self.bricks_x[2], self.bricks_y)
            if ball_brick_reward1 > 0:
                ball_brick_reward = ball_brick_reward1
                bs_m_x, bs_m_y = bs_m_x1, bs_m_y1
                brs = 3
            elif ball_brick_reward2 > 0:
                ball_brick_reward = ball_brick_reward2
                bs_m_x, bs_m_y = bs_m_x2, bs_m_y2
                brs = 5
            elif ball_brick_reward3 > 0:
                ball_brick_reward = ball_brick_reward3
                bs_m_x, bs_m_y = bs_m_x3, bs_m_y3
                brs = 1
        elif brs == 0:
            self.win_sign = 1
            print("game_win")
        if ball_brick_reward > 0: # reward 2
            reward = 2
        elif ball_rect_reward > 0:  # reward 0.1
            reward = 0.1
        elif self.over_sign == 1:
            reward = -1
        else:
            reward = -0.05
        # print(reward)
        return (bs_x, bs_y, bs_m_x, bs_m_y, rs, brs), reward

    def best_policy(self, state):
    
        (bs_x, bs_y, bs_m_x, bs_m_y, rs, brs) = state
        (bs_x_l, bs_y_l, bs_m_x_l, bs_m_y_l, rs_l, brs_l), reward_left = self.cal_reward(
            (bs_x, bs_y, bs_m_x, bs_m_y, rs, brs), 0)
        (bs_x_r, bs_y_r, bs_m_x_r, bs_m_y_r, rs_r, brs_r), reward_right = self.cal_reward(
            (bs_x, bs_y, bs_m_x, bs_m_y, rs, brs), 1)
        if (reward_left + GAMMA * 1 * self.values[bs_x_l][bs_y_l][bs_m_x_l][bs_m_y_l][rs_l][brs_l]) > (
                reward_right + GAMMA * 1 *
                self.values[bs_x_r][bs_y_r][bs_m_x_r][bs_m_y_r][rs_r][brs_r]):
            print(' At this state, the best policy is Left')
            return 0
        else:

            print(' At this state, the best policy is Right')
            return 1

    def get_state(self):
        bs_x, bs_y, bs_m_x, bs_m_y = self.bs_x, self.bs_y, self.bs_m_x, self.bs_m_y
        rs = self.rs
        brs = self.brs
        return (bs_x,bs_y,bs_m_x,bs_m_y,rs,brs)
    
    def step(self, action):
        done = False
        state = self.get_state()
        next_state, reward = self.cal_reward(state, action)
    
        if self.win_sign == 1 or self.over_sign == 1:
            print(self.over_sign)
            done = True
        info = {'reward':'the reward is:'+str(reward),
                'done':done}
                                                                               
        return next_state, reward, done, info
    
    def get_greedy_action(self, state):
        
        (bs_x,bs_y,bs_m_x,bs_m_y,rs,brs) = state
        value_l = self.values[bs_x][bs_y][bs_m_x][bs_m_y][rs][brs][0] 
        value_r =  self.values[bs_x][bs_y][bs_m_x][bs_m_y][rs][brs][1] 
        value_n = self.values[bs_x][bs_y][bs_m_x][bs_m_y][rs][brs][2]
        
        if value_l == max(value_l,value_r,value_n):
            # print(' At this state, the best policy is Left')
            return 0
        if value_r == max(value_l,value_r,value_n):
            # print(' At this state, the best policy is Right')
            return 1
        if value_n == max(value_l,value_r,value_n):
            # print(' At this state, the best policy is Do not move')
            return 2

    
    def get_action(self,state):
        if self.epsilon >= FINAL_EPSILON:
            self.epsilon -= (INITIAL_EPSILON - FINAL_EPSILON) / 10000

        if random.random() < self.epsilon:
            action = random.randint(0, 2)
        else:
            action = self.get_greedy_action(state)

        return action
    
    def train(self):
        total_reward_decade = 0
        for episode in range(20):
            state = self.get_state()
            total_reward = 0
            self.start_sign = 1
            done = False
            step = 0
            while True:
                action = self.get_action(state)
                (bs_x_,bs_y_,bs_m_x_,bs_m_y_,rs_,brs_) = state
                next_state, reward, done, _ = self.step(action)
                (bs_x,bs_y,bs_m_x,bs_m_y,rs,brs) = next_state

                self.values[bs_x_][bs_y_][bs_m_x_][bs_m_y_][rs_][brs_][action]+=ALPHA*(reward+
                                                                               GAMMA*max(self.values[bs_x][bs_y][bs_m_x][bs_m_y][rs][brs][0],
                                                                                         self.values[bs_x][bs_y][bs_m_x][bs_m_y][rs][brs][1],
                                                                                         self.values[bs_x][bs_y][bs_m_x][bs_m_y][rs][brs][2])-
                                                                               self.values[bs_x_][bs_y_][bs_m_x_][bs_m_y_][rs_][brs_][action])
                
                state = next_state
                total_reward += reward
                print(step)
                step+=1
                if done :
                    break
            print('Episode:', episode, 'Total Reward this Episode is:', total_reward)
            total_reward_decade += total_reward
            if episode % 10 == 0:
                print('-------------')
                print('Decade:', episode / 10, 'Total Reward in this Decade is:', total_reward_decade)
                print('-------------')
                total_reward_decade = 0
    
    def test(self):
        # Test
        i = random.randint(0, 58)
        j = random.randint(0, 48)
        k = random.randint(0, 1)
        m = random.randint(0, 1)
        n = random.randint(0, 10)
        t = random.randint(0, 7)

        self.best_policy((i, j, k, m, n, t))

if __name__ == '__main__':
    policy_QL = Q_learning()
    policy_QL.train()
    save_path = 'q_learning.npy'
    policy_QL.save_values(save_path)
    

