import json


class AbstractStream:
    BUFFER_LEN = 2048
    ELINER = '`'

    @staticmethod
    def to_bytes(message: dict | str) -> bytes:
        if isinstance(message, dict):
            return bytes(json.dumps(message).ljust(AbstractStream.BUFFER_LEN, AbstractStream.ELINER), 'UTF-8')
        if isinstance(message, str):
            return bytes(message.ljust(AbstractStream.BUFFER_LEN, AbstractStream.ELINER), 'UTF-8')
        raise AttributeError

    @staticmethod
    def from_bytes(buffer: bytes):
        return json.loads(buffer.replace(bytes(AbstractStream.ELINER, 'UTF-8'), bytes('', 'UTF-8')))


if __name__ == "__main__":
    a = AbstractStream()
    print(a.from_bytes(a.to_bytes({"1": [1, 2]})))