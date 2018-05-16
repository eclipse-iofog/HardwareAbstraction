#********************************************************************************
#  Copyright (c) 2018 Edgeworx, Inc.
#
#  This program and the accompanying materials are made available under the
#  terms of the Eclipse Public License v. 2.0 which is available at
#  http://www.eclipse.org/legal/epl-2.0
#
#  SPDX-License-Identifier: EPL-2.0
#********************************************************************************

from ws_server import HALWSServer
from http_server import HALRESTServer
from multiprocessing import Process


if __name__ == '__main__':
    """ Starts REST and WS servers in separate processes """
    Process(target=HALWSServer).start()
    Process(target=HALRESTServer).start()

