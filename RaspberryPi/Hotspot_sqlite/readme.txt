STEP 1: Initialize RaspberryPi Hotspot: https://github.com/RaspberryConnect/AutoHotspot-Installer
  (i) git clone https://github.com/RaspberryConnect/AutoHotspot-Installer.git
  (ii) sudo chmod u+x /AutoHotspot/AutoHotspot-Installer/AutoHotspot-Setup/Autohotspot/autohotspot-setup.sh
  (iii) ./AutoHotspot/AutoHotspot-Installer/AutoHotspot-Setup/Autohotspot/autohotspot-setup.sh
  (iv) Enter 3
  (v) Reboot and connect to Ethernet
  (vi) sudo nano /etc/dhcpcd.conf
  (vii) interface eth0
        static ip_address=192.168.0.4/24
        static routers=192.168.1.1
        static domain_name_servers=192.168.0.1 # Note this should be the Default IP Address of your routers
  (viii) interface wlan0
         nohook wpa_supplicant
         static ip_address=192.168.4.150/24
         static routers=192.168.4.1
         static domain_name_servers=192.168.1.1
  (ix) sudo nano /etc/dnsmasq.conf # For IP Dyanmic Range
  (x) interface=wlan0
      bind-dynamic
      server=8.8.8.8
      domain-needed
      bogus-priv
      dhcp-range=192.168.50.150,192.168.50.200,12h # Change the Range Ethernet
  (xi) Refer : https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/157-raspberry-pi-auto-wifi-hotspot-switch-internet
               https://www.ionos.com/digitalguide/server/configuration/provide-raspberry-pi-with-a-static-ip-address/

STEP 2:
  python3 InitStatesToLocalDB.py
  python3 main.py
