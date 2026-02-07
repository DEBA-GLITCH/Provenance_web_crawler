

class TransportError(Exception):
    pass

class TimeoutError(TransportError):
    pass

class ProtocolError(TransportError):
    pass
