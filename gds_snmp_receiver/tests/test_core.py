import json
import sys
import types

# Provide minimal pysnmp stubs so tests can import the core module without
# having the real pysnmp package installed in the test environment.
_pysnmp = types.ModuleType("pysnmp")
_carrier = types.ModuleType("pysnmp.carrier")
_asynsock = types.ModuleType("pysnmp.carrier.asynsock")
_dgram = types.ModuleType("pysnmp.carrier.asynsock.dgram")

class _UdpTransport:
    def openServerMode(self, addr):
        return None

_udp = types.SimpleNamespace(domainName="udp", UdpTransport=_UdpTransport)
_dgram.udp = _udp

sys.modules["pysnmp"] = _pysnmp
sys.modules["pysnmp.carrier"] = _carrier
sys.modules["pysnmp.carrier.asynsock"] = _asynsock
sys.modules["pysnmp.carrier.asynsock.dgram"] = _dgram

# Minimal entity/engine/config and ntfrcv stubs
_entity = types.ModuleType("pysnmp.entity")
_engine = types.ModuleType("pysnmp.entity.engine")
_config = types.ModuleType("pysnmp.entity.config")
_rfc = types.ModuleType("pysnmp.entity.rfc3413")

class _DummyTransportDispatcher:
    def jobStarted(self, n):
        pass

    def runDispatcher(self):
        pass

    def closeDispatcher(self):
        pass

class _DummySnmpEngine:
    def __init__(self):
        self.transportDispatcher = _DummyTransportDispatcher()

_engine.SnmpEngine = _DummySnmpEngine
_rfc.ntfrcv = types.SimpleNamespace(NotificationReceiver=lambda *a, **k: None)

sys.modules["pysnmp.entity"] = _entity
sys.modules["pysnmp.entity.engine"] = _engine
sys.modules["pysnmp.entity.config"] = _config
sys.modules["pysnmp.entity.rfc3413"] = _rfc

from gds_snmp_receiver.core import SNMPReceiver  # noqa: E402


def test_compute_idempotency_returns_hex_64():
    varbinds = [("1.2.3", "val1"), ("1.2.4", "val2")]
    h = SNMPReceiver.compute_idempotency_from_trap(varbinds)
    assert isinstance(h, str)
    assert len(h) == 64
    # valid hex
    int(h, 16)


def test_publish_alert_uses_pika(monkeypatch):
    published = {}

    class FakeChannel:
        def __init__(self):
            self.declared = False

        def queue_declare(self, *args, **kwargs):
            # accept positional or keyword args (queue=..., durable=...)
            self.declared = True

        def basic_publish(self, *args, **kwargs):
            # routing_key may be positional or keyword
            if 'routing_key' in kwargs:
                rk = kwargs['routing_key']
            elif len(args) >= 2:
                rk = args[1]
            else:
                rk = None
            # body may be positional or keyword
            body = kwargs.get('body') if 'body' in kwargs else (args[2] if len(args) >= 3 else None)
            published['routing_key'] = rk
            published['body'] = body

    class FakeConn:
        def __init__(self, _params):
            self._ch = FakeChannel()
            self.is_open = True

        def channel(self):
            return self._ch

        def close(self):
            self.is_open = False

    # Monkeypatch pika.BlockingConnection used in core
    import gds_snmp_receiver.core as core_mod

    monkeypatch.setattr(core_mod.pika, 'BlockingConnection', FakeConn)

    r = SNMPReceiver(rabbit_url="amqp://guest:guest@rabbitmq:5672/",
                     queue_name="testq")
    payload = {'idempotency_id': 'abc123', 'alert_name': 'test'}

    # publish_alert will create the connection if needed
    r.publish_alert(payload)

    assert published['routing_key'] == 'testq'
    # body should be JSON string containing the id
    body_obj = json.loads(published['body'])
    assert body_obj['idempotency_id'] == 'abc123'
