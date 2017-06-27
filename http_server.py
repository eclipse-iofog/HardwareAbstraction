import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from process_modules.usb_to_serial_process_module import RESTUSBSerialProcessModule
from process_modules.hwc_process_module import HWCRESTRequestProcessModule
from process_modules.gpio.rpi_gpio_layer import GPIORPiRESTRequestProcessModule
from constants import *
from exception import HALException


class HALRESTServer:
    def __init__(self):
        try:
            self.server = HTTPServer(('', HAL_REST_PORT), HALRESTHandler)
            print('HTTP Server listening on port {}'.format(HAL_REST_PORT))
            self.server.serve_forever()
        except KeyboardInterrupt as e:
            print('HTTP Server shutting down, received error: {}'.format(e))
            self.server.socket.close()
        return


class HALRESTHandler(BaseHTTPRequestHandler):
    process_module = None
    logging = LOGGING

    def log_message(self, format, *args):
        if self.logging:
            BaseHTTPRequestHandler.log_message(self, format, *args)

    def do_GET(self):
        # self.headers.dict['content-type']
        try:
            self._get_request_process_module().process_get_request(self)
        except HALException as hal_e:
            self.send_error_response(hal_e.to_json())
        return

    def do_POST(self):
        try:
            data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            self._get_request_process_module().process_post_request(self, data)
        except Exception as e:
            if not isinstance(e, HALException):
                e = HALException('Error parsing json body: {}'.format(e))
            self.send_error_response(e.to_json())
        return

    def send_ok_response(self, response_body):
        self._build_response(OK_HTTP_RESPONSE_CODE, response_body)

    def send_not_found_response(self, response_body):
        self._build_response(NOT_FOUND_HTTP_RESPONSE_CODE, response_body)

    def send_error_response(self, response_body):
        response_body_str = json.dumps(response_body)
        print('Sending error response: {}'.format(response_body_str))
        self._build_response(ERROR_HTTP_RESPONSE_CODE, response_body_str)

    def _build_response(self, status_code, response_body):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        if isinstance(response_body, bytearray):
            self.wfile.write(bytearray(response_body))
        elif isinstance(response_body, str):
            raw_body = bytearray()
            raw_body.extend(map(ord, response_body))
            self.wfile.write(raw_body)
        else:
            print('Response body for HTTP should be represented as bytearray or str.')
        return

    def _get_request_process_module(self):
        if self.process_module is None:
            self._init_process_module()
        return self.process_module

    def _init_process_module(self):
        if HAL_USB_TO_SERIAL_BASE_URL in self.path:
            self.process_module = RESTUSBSerialProcessModule()
        elif HAL_HWC_BASE_URL in self.path:
            self.process_module = HWCRESTRequestProcessModule()
        elif HAL_GPIO_RPI_BASE_URL in self.path:
            self.process_module = GPIORPiRESTRequestProcessModule()
        else:
            raise HALException(message='This url is not supported: {}'.format(self.path))
        return self.process_module


if __name__ == '__main__':
    # to DEBUG separately
    rest_server = HALRESTServer()
