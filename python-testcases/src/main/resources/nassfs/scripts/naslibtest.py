import logging
import logging.config
import sys
import unittest

from naslib.log import NasLogger
from naslib.ssh import SSHClient
from naslib.connection import NasConnection

from litp.core.litp_logging import LitpLogger

logging.config.fileConfig("/etc/litp_logging.conf")
log = LitpLogger()
log.trace.setLevel(logging.DEBUG)
NasLogger.set(log)


class NaslibTest(unittest.TestCase):

    def setUp(self):
        self.conn_args = tuple(sys.argv[1:4])
        self.pool_name = "litp2"
        ip = sys.argv[1]
        key = SSHClient.get_remote_host_key(ip)
        SSHClient.save_host_key(ip, key)

    def connect_to_nfs(self):
        return NasConnection(*self.conn_args)
