# ansible-openvpn
Ansible Role to deploy OpenVPN server



## Sample playbook

```yaml
---
# ------------------------------------------------
# Install OpenVPN
# ------------------------------------------------
- name: Install and Configure OpenVPN
  hosts:
    - openvpn
  become: true
  vars_files:
    - vars/openvpn_vars.yml
  roles:
    - role: 'openvpn'
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

