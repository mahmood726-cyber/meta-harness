"""Process-wide offline lane guard; loopback browser tests remain available."""
import socket
_connect=socket.socket.connect
_connect_ex=socket.socket.connect_ex
def _local(address):
    return isinstance(address,tuple) and address[0] in ('127.0.0.1','localhost','::1')
def connect(self,address):
    if not _local(address):
        raise RuntimeError('IN3 prohibits non-loopback network connections')
    return _connect(self,address)
def connect_ex(self,address):
    if not _local(address):
        raise RuntimeError('IN3 prohibits non-loopback network connections')
    return _connect_ex(self,address)
socket.socket.connect=connect
socket.socket.connect_ex=connect_ex
