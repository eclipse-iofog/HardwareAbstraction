#********************************************************************************
#  Copyright (c) 2018 Edgeworx, Inc.
#
#  This program and the accompanying materials are made available under the
#  terms of the Eclipse Public License v. 2.0 which is available at
#  http://www.eclipse.org/legal/epl-2.0
#
#  SPDX-License-Identifier: EPL-2.0
#********************************************************************************

class RESTRequestProcessModule:
    def __init__(self):
        pass

    def process_post_request(self, handler, data):
        pass

    def process_get_request(self, handler):
        pass


class WSRequestProcessModule:
    def __init__(self):
        pass

    def handle_open_connection(self):
        pass

    def handle_close_connection(self, code, reason, on_close_event):
        pass

    def open_connection(self, config):
        pass

    def send_data(self, data):
        pass

    def handle_exception(self, ex, msg):
        pass

