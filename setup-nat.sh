#!/bin/bash

# Replace with actual external interface and public IP
WAN_IF="ens33"
PUBLIC_IP="192.168.222.132"

# Enable IP forwarding
sysctl -w net.ipv4.ip_forward=1

# Clear old NAT rules
iptables -t nat -F

# SSH and Telnet Port Forwarding Rules
# Forward appliance ssh connections to internal IP and port
iptables -t nat -A PREROUTING -p tcp -d $PUBLIC_IP --dport 2222 -j DNAT --to-destination 192.168.100.10:22
# Forward lighting ssh connections to internal IP and port
iptables -t nat -A PREROUTING -p tcp -d $PUBLIC_IP --dport 2223 -j DNAT --to-destination 192.168.100.20:22
# Forward thermostat ssh connections to internal IP and port
iptables -t nat -A PREROUTING -p tcp -d $PUBLIC_IP --dport 2224 -j DNAT --to-destination 192.168.100.30:22
# Forward diagnostics telenet connections to internal IP and port
iptables -t nat -A PREROUTING -p tcp -d $PUBLIC_IP --dport 2325 -j DNAT --to-destination 192.168.100.100:23

# SNAT so responses route correctly
iptables -t nat -A POSTROUTING -s 192.168.100.0/24 -o $WAN_IF -j SNAT --to-source $PUBLIC_IP

echo "[*] Adding FORWARD rules..."
iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $WAN_IF -d 192.168.100.0/24 -j ACCEPT

echo "[*] NAT setup complete."