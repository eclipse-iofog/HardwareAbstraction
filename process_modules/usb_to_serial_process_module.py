import json
import threading
from time import sleep

import serial
import serial.tools.list_ports

from constants import *
from process_modules.process_modules_templates import WSRequestProcessModule, RESTRequestProcessModule
from exception import HALException


class WSUSBSerialProcessModule(WSRequestProcessModule):
    def __init__(self, ws_server):
        self.alive = False
        self.serialUSB = None
        self.listener_worker = None
        self.ws_server = ws_server
        self.data_read_timeout = HAL_USB_TO_SERIAL_DATA_READ_TIMEOUT_DEFAULT_VALUE

    def handle_open_connection(self):
        self.alive = True
        self.serialUSB = serial.Serial()
        return

    def handle_close_connection(self, code=HAL_WS_CLOSE_FRAME_STATUS_EXCEPTION, reason='Unexpected error',
                                on_close_event=False):
        print('USB-to-Serial : Closing socket')
        self.alive = False
        self.listener_worker = None
        if self.serialUSB and self.serialUSB.isOpen():
            self.serialUSB.close()
        self.serialUSB = None
        if not on_close_event:
            self.ws_server.send_close_frame(code, reason)
        return

    def open_connection(self, config):
        if config is not None:
            if HAL_USB_TO_SERIAL_PORT_PROPERTY_NAME in config:
                self._apply_config(config)
                try:
                    self.serialUSB.open()
                    self.listener_worker = threading.Thread(target=self._listen_to_incoming_data)
                    self.listener_worker.start()
                    self.ws_server.send_connection_opened()
                except Exception as e:
                    # SerialException – In case the device can not be found or can not be configured.
                    # ValueError – Will be raised when parameter are out of range, e.g. baud rate, data bits.
                    self.handle_exception(e, 'Error opening USB to Serial port or reading data')
            else:
                self.handle_close_connection(reason='No PORT to open USB to Serial connection was provided.')
        else:
            self.handle_close_connection(reason='No config to open USB to Serial connection was provided.')
        return

    def send_data(self, data):
        try:
            self.serialUSB.write(data)
        except Exception as e:
            self.handle_exception(e, 'Error writing data to USB to Serial port')
        return

    def handle_exception(self, ex, msg):
        msg_exc = (msg + ': {}').format(ex)
        #if isinstance(ex, serial.SerialException) or isinstance(ex, ValueError):
        self.handle_close_connection(reason=msg_exc)

    def _listen_to_incoming_data(self):
        while self.alive:
            if self.data_read_timeout > 0:
                sleep(self.data_read_timeout)
            data = self.serialUSB.read(self.serialUSB.in_waiting or 1)
            if data:
                self.ws_server.send_got_data(data)

    def _apply_config(self, config):
        # TODO INFO: maybe use get_settings and apply_settings for usb-to-serial module
        # port
        if HAL_USB_TO_SERIAL_PORT_PROPERTY_NAME in config:
            self.serialUSB.port = config[HAL_USB_TO_SERIAL_PORT_PROPERTY_NAME]
        # baudrate
        if HAL_USB_TO_SERIAL_BAUDRATE_PROPERTY_NAME in config:
            self.serialUSB.baudrate = config[HAL_USB_TO_SERIAL_BAUDRATE_PROPERTY_NAME]
        # bytesize
        if HAL_USB_TO_SERIAL_BYTESIZE_PROPERTY_NAME in config:
            self.serialUSB.bytesize = config[HAL_USB_TO_SERIAL_BYTESIZE_PROPERTY_NAME]
        # parity
        if HAL_USB_TO_SERIAL_PARITY_PROPERTY_NAME in config:
            self.serialUSB.parity = config[HAL_USB_TO_SERIAL_PARITY_PROPERTY_NAME]
        # stopbits
        if HAL_USB_TO_SERIAL_STOPBITS_PROPERTY_NAME in config:
            self.serialUSB.stopbits = config[HAL_USB_TO_SERIAL_STOPBITS_PROPERTY_NAME]
        # timeout
        if HAL_USB_TO_SERIAL_TIMEOUT_PROPERTY_NAME in config:
            self.serialUSB.timeout = config[HAL_USB_TO_SERIAL_TIMEOUT_PROPERTY_NAME]
        # xonxoff
        if HAL_USB_TO_SERIAL_XONXOFF_PROPERTY_NAME in config:
            self.serialUSB.xonxoff = config[HAL_USB_TO_SERIAL_XONXOFF_PROPERTY_NAME]
        # rtscts
        if HAL_USB_TO_SERIAL_RTSCTS_PROPERTY_NAME in config:
            self.serialUSB.rtscts = config[HAL_USB_TO_SERIAL_RTSCTS_PROPERTY_NAME]
        # dsrdtr
        if HAL_USB_TO_SERIAL_DSRDTR_PROPERTY_NAME in config:
            self.serialUSB.dsrdtr = config[HAL_USB_TO_SERIAL_DSRDTR_PROPERTY_NAME]
        # write_timeout
        if HAL_USB_TO_SERIAL_WRITE_TIMEOUT_PROPERTY_NAME in config:
            self.serialUSB.write_timeout = config[HAL_USB_TO_SERIAL_WRITE_TIMEOUT_PROPERTY_NAME]
        # inter_byte_timeout
        if HAL_USB_TO_SERIAL_INTER_BYTE_TIMEOUT_PROPERTY_NAME in config:
            self.serialUSB.inter_byte_timeout = config[HAL_USB_TO_SERIAL_INTER_BYTE_TIMEOUT_PROPERTY_NAME]
        # data_read_timeout (custom property)
        if HAL_USB_TO_SERIAL_DATA_READ_TIMEOUT_PROPERTY_NAME in config:
            self.data_read_timeout = config[HAL_USB_TO_SERIAL_DATA_READ_TIMEOUT_PROPERTY_NAME]


class RESTUSBSerialProcessModule(RESTRequestProcessModule):

    def process_get_request(self, http_handler):
        if HAL_USB_TO_SERIAL_GET_LIST_PATH in http_handler.path:
            list = self._list_to_json(serial.tools.list_ports.comports())
            http_handler.send_ok_response(json.dumps(list))
        else:
            raise HALException(message='This url is not supported: {}'.format(http_handler.path))
        return

    @staticmethod
    def _list_to_json(list):
        json_array = []
        for usb_to_serial in list:
            usb_json = {
                HAL_USB_TO_SERIAL_PORT_PROPERTY_NAME: usb_to_serial.device,
                'description': usb_to_serial.description,
                'device_path': usb_to_serial.device_path,
                'hwid': usb_to_serial.hwid,
                'interface': usb_to_serial.interface,
                'location': usb_to_serial.location,
                'manufacturer': usb_to_serial.manufacturer,
                'name': usb_to_serial.name,
                'pid': usb_to_serial.pid,
                'product': usb_to_serial.product,
                'serial_number': usb_to_serial.serial_number,
                'subsystem': usb_to_serial.subsystem,
                'usb_device_path': usb_to_serial.usb_device_path,
                'vid': usb_to_serial.vid
            }
            json_array.append(usb_json)
        return json_array

