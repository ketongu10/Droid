import io
import socket
import json
from threading import Thread
from time import sleep, time
HEADERSIZE = 10

class Network:

    def __init__(self, cfg):
        self.gen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gen_sock.connect((cfg["HOST"], cfg["GEN_PORT"]))
        self.video_sock.connect((cfg["HOST"], cfg["VIDEO_PORT"]))
        self.physical_logs = None
        self.ping = {"video": 0}
        self.view = None
        self.gen_thread = Thread(target=self.get_image)
        self.video_thread = Thread(target=self.get_physical_logs)
        self.gen_thread.start()
        self.video_thread.start()
        self.finishing = False

    def get_physical_logs(self):
        while not self.finishing:
            t0 = time()
            self.gen_sock.sendall(bytes(json.dumps({
                "request": "get_ph_logs",
                "move": "_|_"
            }), 'UTF-8'))
            data = self.gen_sock.recv(41)


            # загружаем данные в json формате
            #print(data)
            data = json.loads(data.decode('utf-8'))

            if data["request"] == "get_ph_logs":
                self.physical_logs = data
                #print(f"PING logs: {time()-t0}")

    def get_image(self):
        while not self.finishing:
            t0_ping = time()
            self.video_sock.sendall(bytes(json.dumps({
                "request": "get_players",
                "move": "_|_"
            }), 'UTF-8'))

            """received = self.sock.recv(1024*1024*3) #json.loads(self.sock.recv(1024).decode('UTF-8'))

            #with open('image_received.jpg', 'wb') as f:
            #    f.write(received)
            self.view = received
            print(len(received))
            sleep(0.2)"""
            full_msg = b''
            new_msg = True
            t0 = time()
            while True:
                msg = self.video_sock.recv(1024)  # 32768)
                if new_msg:

                    msglen = int(msg[:HEADERSIZE])
                    new_msg = False


                full_msg += msg

                #print(len(full_msg))

                if len(full_msg) - HEADERSIZE == msglen:
                    new_msg = True
                    print(f"RECEIVING TIME={time() - t0}, MESSAGE LEN={msglen}")
                    self.ping["video"] = int((time() - t0_ping)*1000)
                    self.view = full_msg[HEADERSIZE:]
                    break
                elif len(full_msg) - HEADERSIZE > msglen:
                    break
            #print("finished circle")



    def move(self, side):
        # print((json.dumps({
        #     "request": "should_move",
        #     "move": side
        # }), 'UTF-8'))
        self.gen_sock.send(bytes(json.dumps({
            "request": "should_move",
            "move": side
        }), 'UTF-8')) # Отправляем серверу запрос для получения игроков


    def move_arm(self, mode):
        # print((json.dumps({
        #     "request": "arm_move",
        #     "move": mode
        # }), 'UTF-8'))
        self.gen_sock.send(bytes(json.dumps({
            "request": "arm_move",
            "move": mode
        }), 'UTF-8')) # Отправляем серверу запрос для получения игроков

    def change_speeds(self, mode):
        # print((json.dumps({
        #     "request": "change_speed",
        #     "move": mode
        # }), 'UTF-8'))
        self.gen_sock.send(bytes(json.dumps({
            "request": "change_speed",
            "move": mode
        }), 'UTF-8')) # Отправляем серверу запрос для получения игроков