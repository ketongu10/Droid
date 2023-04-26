
from API.Server import Server
from Worlds.Snake import Snake
from time import sleep
from threading import Thread




def loh():
    for i in range(5):
        sleep(2)
        print(i)


if __name__ == '__main__':
    snake = Snake()
    server = Server(snake)
    snake.set_server(server)
    t1 = Thread(target=server.main)
    t1.start()
    snake.main()

