#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import pygame
import sys
import random
from pygame.locals import *

# 1.定义颜色变量
# 目标方块的颜色
redColor = pygame.Color(255, 0, 0)
# 游戏界面颜色
blackColor = pygame.Color(0, 0, 0)
# 贪吃蛇的颜色
whiteColor = pygame.Color(255, 255, 255)


# .定义游戏结束的函数
def gameOver():
    pygame.quit()
    sys.exit()


# .定义入口函数
def main():
    # 初始化pygame
    pygame.init()
    # 3.2定义一个变量控制游戏速度
    fpsClock = pygame.time.Clock()

    # 3.3创建显示窗口
    playSurface = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('贪吃蛇')

    # 3.4初始化变量

    # 初始化贪吃蛇的起始坐标位置
    snakePosition = [100, 100]

    # 初始化贪吃蛇的长度
    snakeBody = [[100, 100], [80, 100], [60, 100]]

    # 初始化目标方块的位置
    targetPosition = [300, 300]

    # 初始化一个目标方块的标记  来判断是否吃掉这个目标方块
    targetflag = 1

    # 初始化方向  往右
    direction = 'right'

    # 定义一个方向  人为控制 和按键有关
    changeDirection = direction


    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    changeDirection = 'right'
                if event.key == K_LEFT:
                    changeDirection = 'left'
                if event.key ==K_UP:
                    changeDirection = 'up'
                if event.key == K_DOWN:
                    changeDirection = 'down'
                if event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))

        # 3.6 确定方向
        if changeDirection == 'left' and not direction == 'right':
            direction = changeDirection
        if changeDirection == 'right' and not direction == 'left':
            direction = changeDirection
        if changeDirection == 'up' and not direction == 'down':
            direction = changeDirection
        if changeDirection == 'down' and not direction == 'up':
            direction = changeDirection

        # 3.7根据方向移动蛇头坐标
        if direction == 'right':
            snakePosition[0] += 20
        if direction == 'left':
            snakePosition[0] -=20
        if direction == 'up':
            snakePosition[1] -=20
        if direction == 'down':
            snakePosition[1] +=20

        # 增加蛇的长度
        snakeBody.insert(0, list(snakePosition))

        # 蛇和目标位置重合
        if snakePosition[0] == targetPosition[0] and snakePosition[1] == targetPosition[1]:
            targetflag = 0
        else:
            snakeBody.pop()

        # 目标吃完 随机生成一个
        if targetflag == 0:
            x = random.randrange(1, 32)
            y = random.randrange(1, 24)
            targetPosition = [int(x*20), int(y*20)]
            targetflag = 1

        # 填充显示层的颜色
        playSurface.fill(blackColor)

        for position in snakeBody:
            pygame.draw.rect(playSurface,whiteColor,Rect(position[0], position[1], 20, 20)) #化蛇
            pygame.draw.rect(playSurface,redColor,Rect(targetPosition[0],targetPosition[1],20,20))

        # 显示到屏幕
        pygame.display.flip()

        if snakePosition[0] > 620 or snakePosition[0] < 0:
            gameOver()
        elif snakePosition[1] > 460 or snakePosition[1] < 0 :
            gameOver()

        # 控制游戏速度
        fpsClock.tick(5)


if __name__ == '__main__':
    main()






