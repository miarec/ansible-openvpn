
import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_directories(host):
    dirs = [
        "/etc/openvpn",
        "/etc/openvpn/client-configs",
        "/etc/openvpn/client-configs/keys"
        "/etc/easyrsa/ca",
        "/etc/easyrsa/server",
        "/etc/easyrsa/clients",

    ]
    for dir in dirs:
        d = host.file(dir)
        assert d.is_directory
        assert d.exists


def test_files(host):
    files = [
        "/etc/openvpn/server.conf",
        "/etc/openvpn/server/ca.crt",
        "/etc/openvpn/server/instance.crt",
        "/etc/openvpn/server/instance.key",
        "/etc/openvpn/server/instance-ta.key",
        "/etc/openvpn/client-configs/keys/user1.key"

    ]
    for file in files:
        f = host.file(file)
        assert f.exists
        assert f.is_file


def test_service(host):
    s = host.service("openvpn-server@server")
    assert s.is_enabled
    assert s.is_running


def test_socket(host):
    sockets = [
        "tcp://0.0.0.0:443"
    ]
    for socket in sockets:
        s = host.socket(socket)
        assert s.is_listening