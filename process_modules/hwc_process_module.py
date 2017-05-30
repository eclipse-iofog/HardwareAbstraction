"""
HWC - Hardware Capabilities
Process module and a wrapper around common Linux commands to check hardware information:
- lscpu
- lspci
- lshw
- lsusb
"""

import json
from subprocess import check_output

from constants import *
from process_modules.process_modules_templates import RESTRequestProcessModule


class HWCRESTRequestProcessModule(RESTRequestProcessModule):

    def process_get_request(self, http_handler):
        if HAL_HWC_GET_LSCPU_INFO_PATH in http_handler.path:
            response = self._get_lscpu_info()
        elif HAL_HWC_GET_LSPCI_INFO_PATH in http_handler.path:
            response = self._get_lspci_info()
        elif HAL_HWC_GET_LSHW_INFO_PATH in http_handler.path:
            response = self._get_lshw_info()
        elif HAL_HWC_GET_LSUSB_INFO_PATH in http_handler.path:
            response = self._get_lsusb_info()
        else:
            http_handler.send_error_response('This url is not supported: ' + http_handler.path)
        http_handler.send_ok_response(json.dumps(response))
        return

    def _get_lscpu_info(self):
        return self.process_lscpu_result(self._run_cmd(LSCPU_CMD))

    def _get_lspci_info(self):
        cmd_result = self._run_cmd(LSPCI_CMD)
        return cmd_result

    def _get_lshw_info(self):
        cmd_result = self._run_cmd(LSHW_CMD)
        return cmd_result

    def _get_lsusb_info(self):
        return self.process_lsusb_result(self._run_cmd(LSUSB_CMD))

    @staticmethod
    def _run_cmd(cmd):
        return check_output(cmd)

    @staticmethod
    def process_lsusb_result(result):
        processed_result = []
        lines = result.splitlines()
        for line in lines:
            tokens = line.split()
            if len(tokens) < 7:
                print('Not enough info.')
            else:
                id_tokens = tokens[5].split(b':')
                name = b' '.join(tokens[6:])
                element = {
                    HAL_LSUSB_BUS_NUMBER_PROPERTY_NAME: tokens[1],
                    HAL_LSUSB_DEVICE_NUMBER_PROPERTY_NAME: tokens[3][:-1],
                    HAL_LSUSB_MANUFACTURE_ID_PROPERTY_NAME: id_tokens[0],
                    HAL_LSUSB_DEVICE_ID_PROPERTY_NAME: id_tokens[1],
                    HAL_LSUSB_MANUFACTURE_AND_DEVICE_NAME_PROPERTY_NAME: name
                }
                processed_result.append(element)
        return processed_result

    @staticmethod
    def process_lscpu_result(result):
        processed_result = []
        lines = result.splitlines()
        for line in lines:
            tokens = line.split(b':')
            if len(tokens) < 2:
                print('Not enough info.')
            else:
                processed_result.append(tokens[1])
        # TODO: should we handle multiple languages ?
        return {}

