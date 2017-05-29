from ws_server import HALWSServer
from http_server import HALRESTServer
from multiprocessing import Process


if __name__ == '__main__':
    """ Starts REST and WS servers in separate processes """
    Process(target=HALWSServer).start()
    Process(target=HALRESTServer).start()

