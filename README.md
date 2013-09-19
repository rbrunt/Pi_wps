
Pi_WPS
======

A utility that allows you to add a device to your Pi's wifi network (hosted using hostapd).

In order for GPIO access (and to be able to communicate with a default setup of hostapd), this needs to be run as root.

Dependancies
-------------

You need the `wpactrl` python library installed as it is used to communicate with hostapd. The source is included in the depends directory.

`cd` into the directory and run the following commands:

    $ make
    $ sudo make install

Configuring `hostapd`
----------------------

`hostapd` doesn't support WPS with the default configuration, so you'll need to put something like this in the config file (located at `/etc/hostapd/hostapd.conf`):

    ctrl_interface=/var/run/hostapd
    ctrl_interface_group=0

    #WPS Stuff:
    wpa_psk_file=/etc/hostapd_wps.psk
    
    eap_server=1
    
    wps_state=2
    ap_setup_locked=1
    
    wps_pin_requests=/var/run/hostapd.pin-req
    device_name=Wireless AP
    manufacturer=Company
    model_name=WAP
    model_number=123
    serial_number=12345
    device_type=6-0050F204-1
    os_version=01020300
    
Bear in mind that the `wpa_psk_file` must be a pre-existing file. It is used to store per-device wpa keys. Feel free to customise the manufacturer etc, but leave the device type as is.
