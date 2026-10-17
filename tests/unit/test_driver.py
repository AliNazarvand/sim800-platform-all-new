from sim800_adapter import TinyGSMAdapter
from sim800_driver import Sim800Driver


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.writes = []

    def write(self, data):
        self.writes.append(data)

    def read_until(self, terminator, timeout):
        return self.responses.pop(0)


def test_command_parses_ok():
    transport = FakeTransport([b"\r\n+CSQ: 20,0\r\nOK\r\n"])
    response = Sim800Driver(transport).command("AT+CSQ")
    assert response.ok and response.payload == ("+CSQ: 20,0",)


def test_retry_then_success():
    transport = FakeTransport([b"ERROR\r\n", b"OK\r\n"])
    assert Sim800Driver(transport, retries=1).check_ready()
    assert len(transport.writes) == 2


def test_adapter_signal_quality():
    transport = FakeTransport([b"+CSQ: 17,99\r\nOK\r\n"])
    assert TinyGSMAdapter(Sim800Driver(transport)).get_signal_quality() == 17


def test_adapter_init_raw_and_sms():
    transport = FakeTransport([b"OK\r\n", b"OK\r\n", b"OK\r\n", b"OK\r\n"])
    adapter = TinyGSMAdapter(Sim800Driver(transport))
    assert adapter.init()
    assert adapter.raw("AT")["ok"] is True
    assert adapter.send_sms("+123", "hello")


def test_driver_rejects_empty_and_parses_cme_error():
    transport = FakeTransport([b"+CME ERROR: 10\r\n"])
    driver = Sim800Driver(transport)
    try:
        driver.command(" ")
    except ValueError:
        pass
    else:
        raise AssertionError("empty command should fail")
    response = driver.command("AT+X", retries=0)
    assert not response.ok and response.error == "+CME ERROR: 10"
