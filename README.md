# ansible-openvpn
Ansible Role to deploy OpenVPN server

ansible-promtail
ansible role to install promtail as a service for log aggregation locally detailed here

## Overview
OpenVPN can be deployed in the following models
 - OpenVPN Access Server
 - OpenVPN Community Edition

### OpenVPN Community Edition (CE)
Comunity Edition is opensource and has no licensing limits. This is only manageable via CLI.

This Role will execute the following
- Install OpenVPN CE Server
- Generate a CA authority using EasyRSA
- Generate Signed Certificate and Private Key for OpenVPN Server
- Generate Signed Certificate and Private Key for specified list of users
- Create Server configuration files
- Create Client configuration files that can be used to initiate a VPN session


### OpenVPN Access Server (AS)
Access Server includes a GUI for managment but limits access to 2 concurrent VPN session without a license. This should be used for testing new infrastructures only.

This role will install AS but will not configure the service, Configuration of clients will need to be executed manually.

This role will provide initial login information as it is generated during the install

Sample output
```
TASK [miarec.openvpn : Print default Login [AS-RHEL/Centos]]] ************************************************************************************
ok: [openvpn.openvpn] => {
    "msg": "openvpn.openvpn: 'To login please use the \"openvpn\" account with \"5wVodVEJnevf\" password.'"
```

AS is installed based on boolean `install_as` defined in variables, default is `false`


## Role Variables
The following variables define how openvpn functions

AS variables
- `install_as` deteremines if AS or CE is installed, default = `false`

CE Required Variables
- `users` list of users to build client infrastructure for, example: ["luke", "Leia", "han_solo"]
- `client_routes` list of subnets to route vpn clients to. This should match your internal subnets that you want to reach via teh vpn session, example `["10.0.1.0 255.255.255.0", "10.0.2.0 255.255.255.0"]`

CE Optional Variables
- `client_subnet` subnet that vpn clients will be assigned, this will be nat'd to openvpn private address, default = `10.8.0.0 255.255.255.0`
- `openvpn_vpn_port` port number vpn clients will use to access server, default = `443`
- `openvpn_vpn_protocol` protocol vpn clients will use to access server, default = `tcp`
- `max_clients` maximum clients that can connect to vpn sessions, default = `10`

Certificate Autority Variables
- `easyrsa_ca_country` default = `US`
- `easyrsa_ca_province`: province or state
- `easyrsa_ca_city` City
- `easyrsa_ca_org` Orginization or Company
- `easyrsa_ca_email` email address to attach to certificate, default = `ssl@example.com`

## Dependencies
In order to successfully route VPN traffic to internal subnets via OPENVPN, the local firewall also has to be configured to NAT traffic from VPN clients to the local interface

an ansible role such as https://github.com/miarec/ansible-role-iptables can be used to configure this action.

Sample Playbooks below include this role.

## Sample playbook

Sample playbook to install CE
```yaml
---
# ------------------------------------------------
# Install OpenVPN
# ------------------------------------------------
- name: Install and Configure OpenVPN
  hosts:
    - openvpn
  become: true
  roles:
    - role: 'openvpn'
      users: ["luke", "leia", "han_solo"]
      client_routes: ["10.0.1.0 255.255.255.0", "10.0.2.0 255.255.255.0"]
  tags: 'openvpn'

- name: Configure iptables
  hosts:
    - openvpn
  become: true
  pre_tasks:
    - name: Set Interface name
      set_fact:
        iface_name: "{{ ansible_interfaces | difference('lo') | first }}"
        iptables_default_tail: "-A INPUT -j REJECT"
    - debug:
        msg: "{{ iface_name }}"
  roles:
    - role: 'miarec.iptables'
      iptables_keep_unmanaged: no
      iptables_custom_rules:
        - name: allow_incoming_vpn_traffic
          rules: '-A INPUT -p tcp --dport 443 -j ACCEPT'
          state: present
        - name: setup_nat
          rules: '-A POSTROUTING -s 10.8.0.0/24 -o {{ iface_name }} -j MASQUERADE'
          state: present
          table: nat
  tags: 'iptables'
```

Sample playbook to install AS
```yaml
---
# ------------------------------------------------
# Install OpenVPN AS
# ------------------------------------------------
- name: Install and Configure OpenVPN
  hosts:
    - openvpn
  become: true
  roles:
    - role: 'openvpn'
      install_as: true
  tags: 'openvpn'

```