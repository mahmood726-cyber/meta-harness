"""Proof-command Python network guard; loopback E2E HTTP remains available."""
import socket

_connect = socket.socket.connect
_connect_ex = socket.socket.connect_ex


def _local(address):
    if isinstance(address, tuple) and str(address[0]) not in ('127.0.0.1', '::1', 'localhost'):
        raise RuntimeError('CGX3B: external network disabled')


def connect(self, address):
    _local(address)
    return _connect(self, address)


def connect_ex(self, address):
    _local(address)
    return _connect_ex(self, address)


socket.socket.connect = connect
socket.socket.connect_ex = connect_ex
