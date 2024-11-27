import pygame
from player import Player
import numpy as np
from old_network import Network
from monitoring.AbstractMonitoring import AbstractMonitor
from time import time
import yaml








def main():
    with open('./config.yml', 'r') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)

    pygame.init()  # Инициализируем pygame

    #HOST, GEN_PORT = str(cfg["HOST"]), 8080  # Адрес сервера
    MAX_SIZE = 2592, 1944
    NOW_SIZE = 768, 768
    SCREEN_SIZE = 1280, 768 # 1024, 1024
    client_network = Network(cfg)  # Создаем объект клиента
    CurrentManagerInstance = AbstractMonitor(100, (2.3, 2.8))
    screen = pygame.display.set_mode(SCREEN_SIZE)  # Создаем окно с разрешением 800x600

    clock = pygame.time.Clock()  # Создаем объект для работы со временем внутри игры
    pygame.font.init() # for text
    speed_text = pygame.font.SysFont('Comic Sans MS', 30)

    IS_PRESSED = {"left": False,
                  "right": False,
                  "up": False,
                  "down": False,
                  "r_shoulder_forward": False, "r_shoulder_backward": False,
                  "r_shoulder_up": False, "r_shoulder_down": False,
                  "r_shoulder_right": False, "r_shoulder_left": False,
                  "r_elbow_forward": False, "r_elbow_backward": False,
                  "r_elbow_right": False, "r_elbow_left": False,
                  "r_grab": False, "r_ungrab": False,
                  "trucks_speed_up": False, "trucks_speed_down": False,
                  "arm_speed_up": False, "arm_speed_down": False,
                  }

    CONTROL_SETTINGS = {ord('a'): "left",
                        ord('d'): "right",
                        ord('w'): "up",
                        ord('s'): "down",
                        ord('t'): 'r_shoulder_forward',
                        ord('g'): 'r_shoulder_backward',
                        ord('y'): 'r_shoulder_up',
                        ord('h'): 'r_shoulder_down',
                        ord('u'): 'r_shoulder_right',
                        ord('j'): 'r_shoulder_left',
                        ord('i'): 'r_elbow_forward',
                        ord('k'): 'r_elbow_backward',
                        ord('o'): 'r_elbow_right',
                        ord('l'): 'r_elbow_left',
                        ord('p'): 'r_grab',
                        ord(';'): 'r_ungrab',
                        ord('r'): "trucks_speed_up",
                        ord('f'): "trucks_speed_down",
                        ord('e'): "arm_speed_up",
                        ord('q'): "arm_speed_down",
                        }

    SPEEDS = {"trucks": 2, "arm": 2}
    SPEEDS_TIMER =  {"trucks": 0, "arm": 0}
    default_image = pygame.image.load("../tmp/test111.jpg").convert_alpha()

    while True:
        for event in pygame.event.get():  # Перебираем все события которые произошли с программой
            # if event.type == pygame.KEYDOWN:
            #     if event.key == ord('a'):
            #         IS_PRESSED["left"] = True
            #     if event.key == ord('d'):
            #         IS_PRESSED["right"] = True
            #     if event.key == ord('w'):
            #         IS_PRESSED["up"] = True
            #     if event.key == ord('s'):
            #         IS_PRESSED["down"] = True
            # elif event.type == pygame.KEYUP:
            #     if event.key == ord('a'):
            #         IS_PRESSED["left"] = False
            #     if event.key == ord('d'):
            #         IS_PRESSED["right"] = False
            #     if event.key == ord('w'):
            #         IS_PRESSED["up"] = False
            #     if event.key == ord('s'):
            #         IS_PRESSED["down"] = False
            if event.type == pygame.KEYDOWN:
                movement_name = CONTROL_SETTINGS.get(event.key)
                if movement_name is not None:
                    IS_PRESSED[movement_name] = True
            elif event.type == pygame.KEYUP:
                movement_name = CONTROL_SETTINGS.get(event.key)
                if movement_name is not None:
                    IS_PRESSED[movement_name] = False

            if event.type == pygame.QUIT:  # Проверяем на выход из игры
                client_network.gen_sock.close()
                exit()

        # TRUCKS MOVEMENT
        x_mode = y_mode = ""
        if IS_PRESSED["left"] != IS_PRESSED["right"]:
            x_mode = "l" if IS_PRESSED["left"] else "r"
        else:
            x_mode = "_"

        if IS_PRESSED["down"] != IS_PRESSED["up"]:
            y_mode = "d" if IS_PRESSED["down"] else "u"
        else:
            y_mode = "_"

        client_network.move(x_mode + '|' + y_mode)

        # ARM MOVEMENT
        arm_move = ""
        if IS_PRESSED["r_shoulder_forward"] != IS_PRESSED["r_shoulder_backward"]:
            arm_move += "r" if IS_PRESSED["r_shoulder_forward"] else "l"
        else:
            arm_move += '_'
        if IS_PRESSED["r_shoulder_up"] != IS_PRESSED["r_shoulder_down"]:
            arm_move += "r" if IS_PRESSED["r_shoulder_up"] else "l"
        else:
            arm_move += '_'
        if IS_PRESSED["r_shoulder_right"] != IS_PRESSED["r_shoulder_left"]:
            arm_move += "r" if IS_PRESSED["r_shoulder_right"] else "l"
        else:
            arm_move += '_'
        if IS_PRESSED["r_elbow_forward"] != IS_PRESSED["r_elbow_backward"]:
            arm_move += "r" if IS_PRESSED["r_elbow_forward"] else "l"
        else:
            arm_move += '_'
        if IS_PRESSED["r_elbow_right"] != IS_PRESSED["r_elbow_left"]:
            arm_move += "r" if IS_PRESSED["r_elbow_right"] else "l"
        else:
            arm_move += '_'
        if IS_PRESSED["r_grab"] != IS_PRESSED["r_ungrab"]:
            arm_move += "r" if IS_PRESSED["r_grab"] else "l"
        else:
            arm_move += '_'

        client_network.move_arm(arm_move)


        speed_mode = None
        if IS_PRESSED["trucks_speed_up"] or IS_PRESSED["trucks_speed_down"]:
            SPEEDS_TIMER["trucks"]+=1
        else:
            SPEEDS_TIMER["trucks"] = 0

        if SPEEDS_TIMER["trucks"] == 1 and IS_PRESSED["trucks_speed_up"] and not IS_PRESSED["trucks_speed_down"] and SPEEDS["trucks"] < 4:
            SPEEDS["trucks"]+=1
            speed_mode = str(SPEEDS["trucks"])+str(SPEEDS["arm"])
        elif SPEEDS_TIMER["trucks"] == 1 and not IS_PRESSED["trucks_speed_up"] and IS_PRESSED["trucks_speed_down"] and SPEEDS["trucks"] > 0:
            SPEEDS["trucks"]-=1
            speed_mode = str(SPEEDS["trucks"])+str(SPEEDS["arm"])

        if IS_PRESSED["arm_speed_up"] or IS_PRESSED["arm_speed_down"]:
            SPEEDS_TIMER["arm"]+=1
        else:
            SPEEDS_TIMER["arm"] = 0

        if SPEEDS_TIMER["arm"] == 1 and IS_PRESSED["arm_speed_up"] and not IS_PRESSED["arm_speed_down"] and SPEEDS["arm"] < 4:
            SPEEDS["arm"]+=1
            speed_mode = str(SPEEDS["trucks"])+str(SPEEDS["arm"])
        elif SPEEDS_TIMER["arm"] == 1 and not IS_PRESSED["arm_speed_up"] and IS_PRESSED["arm_speed_down"] and SPEEDS["arm"] > 0:
            SPEEDS["arm"]-=1
            speed_mode = str(SPEEDS["trucks"])+str(SPEEDS["arm"])

        if speed_mode is not None:
            client_network.change_speeds(speed_mode)

        render_t0 = time()
        screen.fill((0, 0, 0))  # Заполняем экран черным = clear screen
        if client_network.view is not None:
            #print(f"len {len(client.view)}", client.view)

            with open('../tmp/image_received2.png', 'wb') as f:
                f.write(client_network.view)
            #received_img = pygame.image.frombytes(client.view, (1023, 1023), "RGBA") # pygame.image.load("image_received.jpg").convert_alpha()
            received_img = pygame.image.load("../tmp/image_received2.png").convert_alpha()
            screen.blit(received_img, received_img.get_rect())

            #print(f"RENDERING TIME={time() - t0}")

        else:
            screen.fill((0, 0, 0))

            #sсreen.blit(default_image,  default_image.get_rect())
        """for i in client.players:
            #print(i)
            player = Player((i["x"], i["y"]))
            sсreen.blit(player.image, player.rect)  # Рисуем игрока"""

        CurrentManagerInstance.update_buffer(float(client_network.physical_logs['lg']))
        CurrentManagerInstance.render(_screen=screen, pos=(800, 0))
        text_surface = speed_text.render(f"TRUCKS     |{SPEEDS['trucks']}|"
                                         f"\nARMS       |{SPEEDS['arm']}|"
                                         f"\nPING       |{client_network.ping['video']}|"
                                         f"\nRENDER     |{int((time()-render_t0)*1000)}|"
                                         f"\nCURRENT    |{np.mean(CurrentManagerInstance.last_values[-50:]):.4f}|"
                                         f"\nCURRENT_sig|{np.std(CurrentManagerInstance.last_values):.4f}|", False, (0, 255, 0))
        screen.blit(text_surface, (800, 200))
        pygame.display.update()  # Обновляем дисплей

        clock.tick(60)  # Ограничиваем частоту кадров игры до 60


if __name__ == "__main__":
    main()
