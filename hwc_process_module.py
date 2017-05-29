"""
HWC - Hardware Capabilities
Process module and a wrapper around common Linux commands to check hardware information:
- lscpu
- lspci
- lshw
- lsusb
"""

from process_modules_templates import RESTRequestProcessModule
from constants import *

import json
from subprocess import check_output


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
        cmd_result = self._run_cmd(LSCPU_CMD)
        return cmd_result

    def _get_lspci_info(self):
        cmd_result = self._run_cmd(LSPCI_CMD)
        return cmd_result

    def _get_lshw_info(self):
        cmd_result = self._run_cmd(LSHW_CMD)
        return cmd_result

    def _get_lsusb_info(self):
        cmd_result = self._run_cmd(LSUSB_CMD)
        return cmd_result

    @staticmethod
    def _run_cmd(cmd):
        return check_output(cmd)
