import pytest

from greenfield_python_sdk.config import NetworkConfiguration

pytestmark = [pytest.mark.unit]


def test_network_configuration_initialization():
    host = "localhost"
    port = 443

    # Test default ssl value (False)
    network_config_default = NetworkConfiguration(host=host, port=port)
    assert network_config_default.host == host
    assert network_config_default.port == port

    # Test custom ssl value (True)
    network_config_custom = NetworkConfiguration(host=host, port=port)
    assert network_config_custom.host == host
    assert network_config_custom.port == port
