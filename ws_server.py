import asyncio
import json
from struct import pack

from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory

from constants import *
from process_modules.usb_to_serial_process_module import WSUSBSerialProcessModule


class HALWSServer:

    def __init__(self):
        factory = WebSocketServerFactory()
        factory.protocol = HALWSProtocol

        loop = asyncio.get_event_loop()
        coro = loop.create_server(factory, '', HAL_WS_PORT)
        server = loop.run_until_complete(coro)
        try:
            print('WS Server listening on port {}'.format(HAL_WS_PORT))
            loop.run_forever()
        except KeyboardInterrupt as e:
            print('WS Server shutting down, received error: {}'.format(e))
        finally:
            server.close()
            loop.close()
        return


class HALWSProtocol(WebSocketServerProtocol):

    def __init__(self):
        self.process_module = None
        super(HALWSProtocol, self).__init__()

    def onConnect(self, request):
        print('Client connecting: {0}'.format(request.peer))
        self._init_process_module(request)

    def onOpen(self):
        print('WS connection open.')
        self._get_process_module().handle_open_connection()

    def onMessage(self, payload, isBinary):
        if isBinary:
            print('Binary command with ')
            opcode = payload[0]
            if opcode == HAL_WS_OPEN_CONNECTION_OPCODE:
                print(' OPCODE to open connection ')
                config_data = self._read_config(payload)
                self._get_process_module().open_connection(config_data)
            elif opcode == HAL_WS_SEND_DATA_OPCODE:
                print(' OPCODE to send data ')
                self._get_process_module().send_data(payload[1:])
        else:
            print('Text message received: {0}'.format(payload.decode('utf8')))

    def onClose(self, wasClean, code, reason):
        print('WS connection closed: code = {0}, reason = {1}'.format(code, reason))
        if self.state == WebSocketServerProtocol.STATE_OPEN:
            self._get_process_module().handle_close_connection(code, reason, on_close_event=True)

    def send_got_data(self, message):
        self._send_data(HAL_WS_GOT_DATA_OPCODE, message)

    def send_connection_opened(self):
        self._send_data(HAL_WS_CONNECTION_OPENED_OPCODE, message=None)

    def send_close_frame(self, code=HAL_WS_CLOSE_FRAME_STATUS_EXCEPTION, reason='Unexpected error'):
        print('WS Server sending close frame with code = {} and reason: {}'.format(code, reason))
        self.sendClose(code, reason)
        return

    def _get_process_module(self):
        if self.process_module is None:
            self._init_process_module(self.request)
        return self.process_module

    def _init_process_module(self, request):
        if HAL_USB_TO_SERIAL_BASE_URL in request.path:
            self.process_module = WSUSBSerialProcessModule(self)
        else:
            msg = 'This url is not supported: {}'.format(request.path)
            self.send_close_frame(reason=msg)

    def _send_data(self, opcode, message):
        package = bytearray([opcode])
        if message is not None:
            package.extend(message)
        print('sending data with opcode = {} and message : {}'.format(opcode, message))
        if self.state == WebSocketServerProtocol.STATE_OPEN:
            self.sendMessage(bytes(package), isBinary=True)
        else:
            print('Can\'t send message. WS Server state is: {}'.format(ws_states[self.state]))
        return

    def _read_config(self, data):
        pure_data = data[1:]
        try:
            return json.loads(pure_data.decode())
        except Exception as e:
            msg = 'Error parsing config data: {}'.format(e)
            print(msg)
            self.send_close_frame(reason=msg)


if __name__ == '__main__':
    # to DEBUG separately
    ws_server = HALWSServer()
