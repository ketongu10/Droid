import socket
from threading import Thread
import json
import control.movements.move_trucks as HW
import control.monitoring.camera as CAM
import control.movements.move_arm as ARMS

HOST, PORT = '192.168.1.10', 8080  # Адрес сервера
MAX_PLAYERS = 2  # Максимальное кол-во подключений
change_mode = {"forward": HW.move_forward,
        "backward": HW.move_backward,
        "turn_right": HW.turn_right,
        "turn_left": HW.turn_left,
        "stop_move": HW.stop_move,
        "forward_right": HW.forward_right,
        "forward_left": HW.forward_left,
        "backward_right": HW.backward_right,
        "backward_left": HW.backward_left}

class Server:

    def __init__(self, addr, max_conn):
        self.hardware_mode = "stop"
        self.right_arm_mode = "______"
        self.trucks = HW.init()
        self.camera = CAM.init()
        self.right_arm = ARMS.ARM()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(addr)  # запускаем сервер от заданного адреса

        self.max_players = max_conn
        self.players = []  # создаем массив из игроков на сервере

        self.sock.listen(self.max_players)  # устанавливаем максимальное кол-во прослушиваний на сервере
        self.listen()  # вызываем цикл, который отслеживает подключения к серверу

    def listen(self):
        while True:
            if not len(self.players) >= self.max_players:  # проверяем не превышен ли лимит
                # одобряем подключение, получаем взамен адрес и другую информацию о клиенте
                conn, addr = self.sock.accept()

                print("New connection", addr)

                Thread(target=self.handle_client,
                       args=(conn,)).start()  # Запускаем в новом потоке проверку действий игрока

    def handle_client(self, conn):

        # Настраиваем стандартные данные для игрока
        self.player = {
            "id": len(self.players),
            "x": 400,
            "y": 300
        }
        self.players.append(self.player)  # добавляем его в массив игроков

        while True:
            try:

                data = conn.recv(41)  # ждем запросов от клиента

                if not data:  # если запросы перестали поступать, то отключаем игрока от сервера
                    print("Disconnect")
                    break

                # загружаем данные в json формате
                print(data)
                data = json.loads(data.decode('utf-8'))

                # запрос на получение игроков на сервере
                if data["request"] == "get_players":
                    conn.sendall(CAM.get_view(self.camera))
                    """conn.sendall(bytes(json.dumps({
                         "response": self.players
                     }), 'UTF-8'))"""

                # движение
                if data["request"] == "should_move":

                    if 'l' in data["move"]:
                        self.player["x"] -= 1
                    if 'r' in data["move"]:
                        self.player["x"] += 1
                    if 'd' in data["move"]:
                        self.player["y"] += 1
                    if 'u' in data["move"]:
                        self.player["y"] -= 1


                    new_mode = "stop_move"
                    if  data["move"] == 'l|_' :
                        new_mode = "turn_left"
                    elif data["move"] == 'r|_' :
                        new_mode = "turn_right"
                    elif data["move"] == '_|u' :
                        new_mode = "forward"
                    elif data["move"] == '_|d' :
                        new_mode = "backward"
                    elif  data["move"] == 'l|u' :
                        new_mode = "forward_left"
                    elif data["move"] == 'r|u' :
                        new_mode = "forward_right"
                    elif data["move"] == 'l|d' :
                        new_mode = "backward_left"
                    elif data["move"] == 'r|d' :
                        new_mode = "backward_right"

                    if new_mode != self.hardware_mode:
                        print(self.trucks)
                        self.trucks = HW.stop_move(*self.trucks)
                        self.trucks = change_mode[new_mode](*self.trucks)
                        self.hardware_mode = new_mode

                if data["request"] == "arm_move":
                    directives = data["move"]

                    #check whether directives changed
                    for i in range(len(self.right_arm_mode)):
                        if self.right_arm_mode[i] != directives[i]:
                            #setting up new directives
                            self.right_arm_mode[i] = directives[i]
                            self.right_arm.move_i_motor(i, ARMS.Motions.get_by_code(directives[i]), 255)




            except Exception as e:
                print(e, "loh")
                HW.finalize(*self.trucks)
                CAM.finalize(self.camera)
                break

        self.players.remove(self.player)  # если вышел или выкинуло с сервера - удалить персонажа


if __name__ == "__main__":
    server = Server((HOST, PORT), MAX_PLAYERS)