class _Device:
    def __init__(self, available=True):
        self._available = available
    def is_available(self):
        return self._available

class cuda:
    _device = _Device(True)
    is_available = staticmethod(_device.is_available)

def tensor(data):
    return data

float16 = 'float16'
float32 = 'float32'

from contextlib import contextmanager
@contextmanager
def no_grad():
    yield
