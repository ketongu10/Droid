import pygame
import time
import random



class C:
    white = (255, 255, 255)
    yellow = (255, 255, 102)
    black = (0, 0, 0)
    red = (213, 50, 80)
    green = (0, 255, 0)
    dark_green = (0, 150, 0)
    blue = (50, 153, 213)
    
    dis_width = 720
    dis_height = 720
    snake_block = 60
    snake_speed_fast = 100
    snake_speed_slow = 5
    



class Snake:
    
    def __init__(self):
        pygame.init()
        self.dis = pygame.display.set_mode((C.dis_width, C.dis_height))
        self.snake_speed = C.snake_speed_fast
        self.game_close = True
        self.game_over = True
        pygame.display.set_caption('Snake Game by Pythonist')

        self.clock = pygame.time.Clock()

        self.font_style = pygame.font.SysFont("bahnschrift", 25)
        self.score_font = pygame.font.SysFont("comicsansms", 35)

    def set_server(self, server):
        self.server = server

    def Your_score(self, score):
        value = self.score_font.render("Your Score: " + str(score), True, C.yellow)
        self.dis.blit(value, [0, 0])
    
    
    def our_snake(self, snake_block, snake_list):
        for i, x in enumerate(snake_list):
            if i == len(snake_list) - 1:
                pygame.draw.rect(self.dis, C.dark_green, [x[0], x[1], snake_block, snake_block])
            else:
                pygame.draw.rect(self.dis, C.green, [x[0], x[1], snake_block, snake_block])
    
    def border(self):
        pygame.draw.rect(self.dis, C.black, [0, 0, C.dis_width, C.snake_block])
        pygame.draw.rect(self.dis, C.black, [0, C.dis_height-C.snake_block, C.dis_width, C.snake_block])
        pygame.draw.rect(self.dis, C.black, [C.dis_width-C.snake_block, 0, C.snake_block, C.dis_height])
        pygame.draw.rect(self.dis, C.black, [0, 0, C.snake_block, C.dis_height])
    
    
    def message(self, msg, color):
        mesg = self.font_style.render(msg, True, color)
        self.dis.blit(mesg, [C.dis_width / 6, C.dis_height / 3])
    
    
    def control_engine(self, dx, dy, snake_len, game_over_flag, prev_key, events):
        if not self.server.guided:  # means master helps droid
            for event in events:
                if event.type == pygame.QUIT:
                    game_over_flag = True
                    self.server.is_active = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and prev_key != pygame.K_RIGHT or event.key == pygame.K_LEFT and snake_len <= 2:
                        dx = -C.snake_block
                        dy = 0
                        prev_key = event.key
                        self.server.world.choiceINT = 4
                    elif event.key == pygame.K_RIGHT and prev_key != pygame.K_LEFT or event.key == pygame.K_RIGHT and snake_len <= 2:
                        dx = C.snake_block
                        dy = 0
                        prev_key = event.key
                        self.server.world.choiceINT = 2
                    elif event.key == pygame.K_UP and prev_key != pygame.K_DOWN or event.key == pygame.K_UP and snake_len <= 2:
                        dy = -C.snake_block
                        dx = 0
                        prev_key = event.key
                        self.server.world.choiceINT = 1
                    elif event.key == pygame.K_DOWN and prev_key != pygame.K_UP or event.key == pygame.K_DOWN and snake_len <= 2:
                        dy = C.snake_block
                        dx = 0
                        prev_key = event.key
                        self.server.world.choiceINT = 3
        else:
            for event in events:
                if event.type == pygame.QUIT:
                    game_over_flag = True
                    self.server.is_active = False

            a = self.server.world.choice
            if a == pygame.K_LEFT and prev_key != pygame.K_RIGHT or a == pygame.K_LEFT and snake_len <= 2:
                dx = -C.snake_block
                dy = 0
                prev_key = a
            elif a == pygame.K_RIGHT and prev_key != pygame.K_LEFT or a == pygame.K_RIGHT and snake_len <= 2:
                dx = C.snake_block
                dy = 0
                prev_key = a
            elif a == pygame.K_UP and prev_key != pygame.K_DOWN or a == pygame.K_UP and snake_len <= 2:
                dy = -C.snake_block
                dx = 0
                prev_key = a
            elif a == pygame.K_DOWN and prev_key != pygame.K_UP or a == pygame.K_DOWN and snake_len <= 2:
                dy = C.snake_block
                dx = 0
                prev_key = a
                    
        return dx, dy, game_over_flag, prev_key
    
    
    def main(self):
        self.gameLoop()

    def reset(self):
        pass
    
    
    def gameLoop(self):
        timer = 0
        self.game_over = False
        self.game_close = False
    
        x1 = C.dis_width / 2
        y1 = C.dis_height / 2
    
        x1_change = 0
        y1_change = 0
    
        snake_List = []
        Length_of_snake = 1

        foodx = round(random.randrange(C.snake_block, C.dis_width - 2 * C.snake_block) / C.snake_block) * C.snake_block
        foody = round(random.randrange(C.snake_block, C.dis_height - 2 * C.snake_block) / C.snake_block) * C.snake_block
        prev_key = pygame.K_ESCAPE
        while not self.game_over:


            """GAME MENU"""
            while self.game_close == True:
                self.dis.fill(C.blue)
                self.message("You Lost! Press C-Play Again or Q-Quit", C.red)
                self.Your_score(Length_of_snake - 1)
                pygame.display.update()
    
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            self.game_over = True
                            self.game_close = False
                            self.server.is_active = False
                        if event.key == pygame.K_c:
                            self.main()
                if self.server.guided:
                    self.main()

            """INPUT"""
            x1_change, y1_change, self.game_over, prev_key = self.control_engine(x1_change, y1_change, len(snake_List), self.game_over, prev_key, pygame.event.get())
    
            if x1 >= C.dis_width-C.snake_block or x1 < C.snake_block or y1 >= C.dis_height-C.snake_block or y1 < C.snake_block:
                self.game_close = True

            """CHECK APPLE"""
            has_eaten = False
            if x1 == foodx and y1 == foody:
                print("Yummy!!")
                has_eaten = True
                foodx = round(random.randrange(C.snake_block, C.dis_width - 2 * C.snake_block) / C.snake_block) * C.snake_block
                foody = round(random.randrange(C.snake_block, C.dis_height - 2 * C.snake_block) / C.snake_block) * C.snake_block
                Length_of_snake += 1

            x1 += x1_change
            y1 += y1_change
    
            """SNAKE MOVEMENT"""
            snake_Head = (x1, y1)
            snake_List.append(snake_Head)
            if len(snake_List) > Length_of_snake:
                del snake_List[0]
    
            for x in snake_List[:-1]:
                if x == snake_Head:
                    self.game_close = True

    
            """RENDER"""
            self.dis.fill(C.blue)
            pygame.draw.rect(self.dis, C.red, [foodx, foody, C.snake_block, C.snake_block])
            self.border()
            self.our_snake(C.snake_block, snake_List)
            self.Your_score(Length_of_snake - 1)
            pygame.display.update()
            timer += 1  #TIMER
            self.clock.tick(self.snake_speed)
    
            """OTHER"""
            if self.game_close:
                self.server.world.prev_feedback, self.server.world.feedback = self.server.world.feedback, 0
                #print("IT'S FAIL BRO")
            elif has_eaten:
                self.server.world.prev_feedback, self.server.world.feedback = self.server.world.feedback, 1
            else:
                self.server.world.prev_feedback, self.server.world.feedback = self.server.world.feedback, 1


            #print(clock.get_fps())
    
    
    
        pygame.quit()
        quit()
