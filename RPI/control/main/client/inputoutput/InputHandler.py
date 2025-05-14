import pygame

from RPI.control.main.client.inputoutput.ClientMainScreen import ClientMainScreen
from RPI.control.main.client.inputoutput.GUI.MainMenu import MainMenu
from RPI.control.main.monitoring.Profiler import Profiler

class SpecDict:
    def __init__(self):
        self.dict = {"trucks": 2, "arm": 2}

class InputHandler:
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


    def __init__(self, main_menu):
        self.SPEEDS_TIMER = {"trucks": 0, "arm": 0}
        self.main_menu: MainMenu = main_menu


    @Profiler.register("input_handler")
    def get_control_input(self) -> dict:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                movement_name = InputHandler.CONTROL_SETTINGS.get(event.key)
                if movement_name is not None:
                    InputHandler.IS_PRESSED[movement_name] = True
            elif event.type == pygame.KEYUP:
                movement_name = InputHandler.CONTROL_SETTINGS.get(event.key)
                if movement_name is not None:
                    InputHandler.IS_PRESSED[movement_name] = False

            self.main_menu.process_events_all(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.main_menu.CONTROL_MODE *= -1

            if event.type == pygame.QUIT:  # Проверяем на выход из игры
                return {"status": "Quit"}


        # TRUCKS MOVEMENT
        x_mode = y_mode = ""
        if InputHandler.IS_PRESSED["left"] != InputHandler.IS_PRESSED["right"]:
            x_mode = "l" if InputHandler.IS_PRESSED["left"] else "r"
        else:
            x_mode = "_"

        if InputHandler.IS_PRESSED["down"] != InputHandler.IS_PRESSED["up"]:
            y_mode = "d" if InputHandler.IS_PRESSED["down"] else "u"
        else:
            y_mode = "_"

        trucks_move_command = x_mode + '|' + y_mode

        # ARM MOVEMENT
        arm_move = ""
        if InputHandler.IS_PRESSED["r_shoulder_forward"] != InputHandler.IS_PRESSED["r_shoulder_backward"]:
            arm_move += "r" if InputHandler.IS_PRESSED["r_shoulder_forward"] else "l"
        else:
            arm_move += '_'
        if InputHandler.IS_PRESSED["r_shoulder_up"] != InputHandler.IS_PRESSED["r_shoulder_down"]:
            arm_move += "r" if InputHandler.IS_PRESSED["r_shoulder_up"] else "l"
        else:
            arm_move += '_'
        if InputHandler.IS_PRESSED["r_shoulder_right"] != InputHandler.IS_PRESSED["r_shoulder_left"]:
            arm_move += "r" if InputHandler.IS_PRESSED["r_shoulder_right"] else "l"
        else:
            arm_move += '_'
        if InputHandler.IS_PRESSED["r_elbow_forward"] != InputHandler.IS_PRESSED["r_elbow_backward"]:
            arm_move += "r" if InputHandler.IS_PRESSED["r_elbow_forward"] else "l"
        else:
            arm_move += '_'
        if InputHandler.IS_PRESSED["r_elbow_right"] != InputHandler.IS_PRESSED["r_elbow_left"]:
            arm_move += "r" if InputHandler.IS_PRESSED["r_elbow_right"] else "l"
        else:
            arm_move += '_'
        if InputHandler.IS_PRESSED["r_grab"] != InputHandler.IS_PRESSED["r_ungrab"]:
            arm_move += "r" if InputHandler.IS_PRESSED["r_grab"] else "l"
        else:
            arm_move += '_'

        # CHANGING SPEEDS
        speed_mode = None
        if InputHandler.IS_PRESSED["trucks_speed_up"] or InputHandler.IS_PRESSED["trucks_speed_down"]:
            self.SPEEDS_TIMER["trucks"] += 1
        else:
            self.SPEEDS_TIMER["trucks"] = 0

        if self.SPEEDS_TIMER["trucks"] == 1 and InputHandler.IS_PRESSED["trucks_speed_up"] and not InputHandler.IS_PRESSED[
            "trucks_speed_down"] and self.main_menu.SPEEDS["trucks"] < 4:
            self.main_menu.SPEEDS["trucks"] += 1
            speed_mode = str(self.main_menu.SPEEDS["trucks"]) + str(self.main_menu.SPEEDS["arm"])
        elif self.SPEEDS_TIMER["trucks"] == 1 and not InputHandler.IS_PRESSED["trucks_speed_up"] and InputHandler.IS_PRESSED[
            "trucks_speed_down"] and self.main_menu.SPEEDS["trucks"] > 0:
            self.main_menu.SPEEDS["trucks"] -= 1
            speed_mode = str(self.main_menu.SPEEDS["trucks"]) + str(self.main_menu.SPEEDS["arm"])

        if InputHandler.IS_PRESSED["arm_speed_up"] or InputHandler.IS_PRESSED["arm_speed_down"]:
            self.SPEEDS_TIMER["arm"] += 1
        else:
            self.SPEEDS_TIMER["arm"] = 0

        if self.SPEEDS_TIMER["arm"] == 1 and InputHandler.IS_PRESSED["arm_speed_up"] and not InputHandler.IS_PRESSED[
            "arm_speed_down"] and self.main_menu.SPEEDS["arm"] < 4:
            self.main_menu.SPEEDS["arm"] += 1
            speed_mode = str(self.main_menu.SPEEDS["trucks"]) + str(self.main_menu.SPEEDS["arm"])
        elif self.SPEEDS_TIMER["arm"] == 1 and not InputHandler.IS_PRESSED["arm_speed_up"] and InputHandler.IS_PRESSED[
            "arm_speed_down"] and self.main_menu.SPEEDS["arm"] > 0:
            self.main_menu.SPEEDS["arm"] -= 1
            speed_mode = str(self.main_menu.SPEEDS["trucks"]) + str(self.main_menu.SPEEDS["arm"])

        return {"trucks_movements": trucks_move_command,
                "arm_movements": arm_move,
                "change_speeds": speed_mode,
                "status": "Successfully"}