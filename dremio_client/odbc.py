# -*- coding: utf-8 -*-
import logging

#
# Copyright (c) 2019 Ryan Murray.
#
# This file is part of Dremio Client
# (see https://github.com/rymurr/dremio_client).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import sys


_WINDOWS_DRIVER = "Dremio Connector"
_OSX_DRIVER = "Dremio ODBC Driver"
_LINUX32_DRIVER = "Dremio ODBC Driver 32-bit"
_LINUX64_DRIVER = "Dremio ODBC Driver 64-bit"
_DRIVER = None


def _get_driver_name():
    if "linux" in sys.platform:
        if sys.maxsize > 2 ** 32:
            return _LINUX64_DRIVER
        else:
            return _LINUX32_DRIVER

    if "darwin" in sys.platform:
        return _OSX_DRIVER

    if "win" in sys.platform:
        return _WINDOWS_DRIVER

    return _DRIVER


try:
    import pyodbc
    import pandas

    def connect(hostname="localhost", port=31010, username="dremio", password="dremio123", driver=None):
        """
        Connect to and authenticate against Dremio's odbc server. Auth is skipped if username is None

        :param hostname: Dremio coordinator hostname
        :param port: Dremio coordinator port
        :param username: Username on Dremio
        :param password: Password on Dremio
        :param driver: ODBC driver name or file path
        :return: arrow flight client
        """
        if driver is None:
            driver = _get_driver_name()

        logging.debug("Using %s as the odbc driver", driver)

        connection_string = (
            "Driver={driver};ConnectionType=Direct;HOST={hostname};"
            + "PORT={port};AuthenticationType=Plain;UID={username};PWD={password}"
        ).format(
            driver=driver,
            hostname=hostname,
            port=port,
            username=username,
            password=password,
        )

        c = pyodbc.connect(
            connection_string,
            autocommit=True,
        )

        return c

    def query(sql, client=None, hostname="localhost", port=31010, username="dremio", password="dremio123"):
        """
        Run an sql query against Dremio and return a pandas dataframe

        Either host,port,user,pass tuple or a pre-connected client should be supplied. Not both

        :param sql: sql query to execute on dremio
        :param client: pre-connected client (optional)
        :param hostname: Dremio coordinator hostname (optional)
        :param port: Dremio coordinator port (optional)
        :param username: Username on Dremio (optional)
        :param password: Password on Dremio (optional)
        :return:
        """
        if not client:
            client = connect(hostname, port, username, password)
        return pandas.read_sql(sql, client)


except ImportError:

    def connect(*args, **kwargs):
        raise NotImplementedError("Python Flight bindings require Python 3 and pyarrow > 0.14.0")

    def query(*args, **kwargs):
        raise NotImplementedError("Python Flight bindings require Python 3 and pyarrow > 0.14.0")
