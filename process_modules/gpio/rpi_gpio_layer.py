import RPi.GPIO as GPIO
import json
import numbers

from constants import *
from process_modules.process_modules_templates import RESTRequestProcessModule
from exception import HALException


class GPIORPiRESTRequestProcessModule(RESTRequestProcessModule):

    def process_get_request(self, http_handler):
        response = None
        if HAL_GPIO_RPI_SET_BCM_MODE_URL in http_handler.path:
            response = self._set_mode()
        elif HAL_GPIO_RPI_SET_BOARD_MODE_URL in http_handler.path:
            response = self._set_mode(board=True)
        else:
            raise HALException(message='This url is not supported or has invalid HTTP Method: {}'
                               .format(http_handler.path))
        if response is not None:
            http_handler.send_ok_response(json.dumps(response))
        return

    def process_post_request(self, http_handler, data):
        response = None
        if HAL_GPIO_RPI_SET_UP_PINS_URL in http_handler.path:
            response = self._set_up_pins(data)
        elif HAL_GPIO_RPI_GET_PIN_VALUE_URL in http_handler.path:
            response = self._get_pin_value(data)
        elif HAL_GPIO_RPI_SET_PIN_VALUE_URL in http_handler.path:
            if HAL_GPIO_RPI_SET_HIGH_PIN_URL in http_handler.path:
                response = self._set_pin_value_high(data)
            elif HAL_GPIO_RPI_SET_LOW_PIN_URL in http_handler.path:
                response = self._set_pin_value_low(data)
            else:
                response = self._set_pin_value(data)
        elif HAL_GPIO_RPI_CLEANUP_URL in http_handler.path:
            response = self._cleanup_gpio(data)
        else:
            raise HALException(message='This url is not supported or has invalid HTTP Method: {}'
                               .format(http_handler.path))
        if response is not None:
            http_handler.send_ok_response(json.dumps(response))
        return

    @staticmethod
    def _cleanup_gpio(data=None):
        try:
            if len(data) == 0:
                GPIO.cleanup()
            else:
                GPIO.cleanup(data)
            return 'clean up success'
        except Exception as e:
            raise HALException(message=str(e))

    @staticmethod
    def _set_mode(board=False):
        try:
            current_mode = GPIO.getmode()
            if current_mode is None:
                if board:
                    GPIO.setmode(GPIO.BOARD)
                else:
                    GPIO.setmode(GPIO.BCM)
                return 'GPIO mode set successfully'
            else:
                message = 'GPIO is already in mode \'{}\''
                if current_mode == GPIO.BCM:
                    return message.format('BCM')
                elif current_mode == GPIO.BOARD:
                    return message.format('BOARD')
                else:
                    return message.format(current_mode)
        except Exception as e:
            raise HALException(message=str(e))

    def _set_up_pins(self, data):
        for pin in data:
            if HAL_GPIO_RPI_SET_UP_PIN_NUMBER_PROPERTY_NAME in pin and HAL_GPIO_RPI_SET_UP_PIN_TYPE_PROPERTY_NAME in pin:
                if self._check_number_type(pin[HAL_GPIO_RPI_SET_UP_PIN_NUMBER_PROPERTY_NAME]):
                    pin_type = GPIO.OUT
                    if pin[HAL_GPIO_RPI_SET_UP_PIN_TYPE_PROPERTY_NAME].lower() == 'in':
                        pin_type = GPIO.IN
                    if HAL_GPIO_RPI_SET_UP_PIN_INITIAL_VALUE_PROPERTY_NAME in pin:
                        initial_value = GPIO.HIGH
                        if pin[HAL_GPIO_RPI_SET_UP_PIN_INITIAL_VALUE_PROPERTY_NAME].lower() == 'low':
                            initial_value = GPIO.LOW
                        if HAL_GPIO_RPI_SET_UP_PIN_PULL_UP_DOWN_PROPERTY_NAME in pin:
                            p_u_d = GPIO.PUD_UP
                            if pin[HAL_GPIO_RPI_SET_UP_PIN_PULL_UP_DOWN_PROPERTY_NAME].lower() == 'down':
                                p_u_d = GPIO.PUD_DOWN
                            GPIO.setup(pin[HAL_GPIO_RPI_SET_UP_PIN_NUMBER_PROPERTY_NAME], pin_type, initial_value, p_u_d)
                        else:
                            GPIO.setup(pin[HAL_GPIO_RPI_SET_UP_PIN_NUMBER_PROPERTY_NAME], pin_type, initial_value)
                    elif HAL_GPIO_RPI_SET_UP_PIN_PULL_UP_DOWN_PROPERTY_NAME in pin:
                        p_u_d = GPIO.PUD_UP
                        if pin[HAL_GPIO_RPI_SET_UP_PIN_PULL_UP_DOWN_PROPERTY_NAME].lower() == 'down':
                            p_u_d = GPIO.PUD_DOWN
                        GPIO.setup(pin[HAL_GPIO_RPI_SET_UP_PIN_NUMBER_PROPERTY_NAME], pin_type, p_u_d)
                    else:
                        GPIO.setup(pin[HAL_GPIO_RPI_SET_UP_PIN_NUMBER_PROPERTY_NAME], pin_type)
                else:
                    raise HALException(message='\'{}\' property should be a number'
                                       .format(HAL_GPIO_RPI_SET_UP_PIN_NUMBER_PROPERTY_NAME))
            else:
                raise HALException(message='\'{}\' and \'{}\' are required to set up pin'.format(
                    HAL_GPIO_RPI_SET_UP_PIN_NUMBER_PROPERTY_NAME, HAL_GPIO_RPI_SET_UP_PIN_TYPE_PROPERTY_NAME))
        return 'successfully set up all pins'

    def _get_pin_value(self, data):
        values = {}
        for pin in data:
            if self._check_number_type(pin):
                try:
                    value = GPIO.input(pin)
                    values[pin] = value
                except Exception as e:
                    values[pin] = str(e)
            else:
                raise HALException(message='\'{}\' property should be a number'
                                   .format(HAL_GPIO_RPI_SET_UP_PIN_NUMBER_PROPERTY_NAME))
        return values

    def _set_pin_value(self, data):
        values = {}
        for pin in data:
            if HAL_GPIO_RPI_SET_UP_PIN_NUMBER_PROPERTY_NAME in pin:
                pin_number = pin[HAL_GPIO_RPI_SET_UP_PIN_NUMBER_PROPERTY_NAME]
                if self._check_number_type(pin_number):
                    value = GPIO.HIGH
                    if pin[HAL_GPIO_RPI_SET_UP_PIN_VALUE_PROPERTY_NAME].lower() == 'low':
                        value = GPIO.LOW
                    try:
                        GPIO.output(pin_number, value)
                        values[pin_number] = 'ok'
                    except Exception as e:
                        raise HALException(message=str(e))
                else:
                    raise HALException(message='\'{}\' property should be a number'
                                       .format(HAL_GPIO_RPI_SET_UP_PIN_NUMBER_PROPERTY_NAME))
            else:
                raise HALException(message='\'{}\' property is required'
                                   .format(HAL_GPIO_RPI_SET_UP_PIN_NUMBER_PROPERTY_NAME))
        return values

    def _set_pin_value_high(self, data):
        values = {}
        for pin in data:
            if self._check_number_type(pin):
                try:
                    GPIO.output(pin, GPIO.HIGH)
                    values[pin] = 'ok'
                except Exception as e:
                    values[pin] = str(e)
            else:
                raise HALException(message='the list should contain only numbers for pin numbering')
        return values

    def _set_pin_value_low(self, data):
        values = {}
        for pin in data:
            if self._check_number_type(pin):
                try:
                    GPIO.output(pin, GPIO.LOW)
                    values[pin] = 'ok'
                except Exception as e:
                    values[pin] = str(e)
            else:
                raise HALException(message='the list should contain only numbers for pin numbering')
        return values

    @staticmethod
    def _check_number_type(value):
        if isinstance(value, numbers.Number):
            return True
        else:
            return False
