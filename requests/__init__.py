
class Response:
    def __init__(self, payload=None):
        self._payload = payload or {}
        self.status_code = 200

    def json(self):
        return self._payload

    def raise_for_status(self):
        pass


def post(*args, **kwargs):  # pragma: no cover - to be patched in tests
    raise NotImplementedError("Mock me in tests")


def get(*args, **kwargs):  # pragma: no cover - to be patched in tests
    raise NotImplementedError("Mock me in tests")
