import socket as skt
import sqlite3

class MasterServer():
    def __init__(self, data: str) -> None:
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
        self.con = sqlite3.connect(data)
        self.cur = self.con.cursor()

    def open(self, ip: str, port: int) -> None:
        self.socket.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen(1)

    def close(self) -> None:
        self.socket.close()


