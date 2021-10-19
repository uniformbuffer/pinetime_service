# Pinetime service daemon

The daemon can detect currently paired devices at launch.
It can also detect newely paired or unpaired devices.
Sometimes (actually very rarely) could happened the bluetooth service miss to publish a device pairing message to dbus, 
so the daemon will miss to add such to it's internal list and activate all the possible services for it.
I will understand the reasoning of this to fix such undesired behaviour. If this happen, just unpair and pair again the device.

The daemon can be launched simply with `python3 main.py`.
Please consider that it is designed to detect only paired devices, so to make it working would require to use some bluetooth pairing tool.
Most desktop environments offer a gui to make possible to pair bluetooth device. Any tool able to make bluetooth pairing should work.

After pairing, all the services offered by the device (and supported by the daemon) will be enabled.
What currently work is:

Generic features:
- :ballot_box_with_check: Gathering all the paired devices and look for services for each of them
- :ballot_box_with_check: Detect when a device is paired or unpaired
- :x: Reconnect device in case of disconnection: it is very difficult to handle it properly from the daemon. It would be better handled by the DE bluetooth service
- :black_square_button: Proper packaging
- :black_square_button: Documentation

System (host) services:
- :ballot_box_with_check: Read desktop notifications
- :ballot_box_with_check: Detect calls from Gnome Calls
- :ballot_box_with_check: Detect opening and closing of MPRIS enabled applications

Generic device services:
- :ballot_box_with_check: Heart rate reading
- :ballot_box_with_check: Heart rate notification
- :ballot_box_with_check: Battery level reading
- :ballot_box_with_check: Battery level notification
- :ballot_box_with_check: Notification send
- :ballot_box_with_check: Hardware revision reading
- :ballot_box_with_check: Software revision reading
- :ballot_box_with_check: Firmware revision reading
- :ballot_box_with_check: Generic device info like alias, address and so on
- :x: Step counter reading:  currently impossible, such service is not exposed by InfiniTime
- :x: Step counter notification:  currently impossible, such service is not exposed by InfiniTime
- :black_square_button: Media control
- :black_square_button: Navigation


InfiniTime services:
- :ballot_box_with_check: Notification send for both the "message style" and "call style"
- :ballot_box_with_check: Notification receive from "call style" messages

Combined features:
- :ballot_box_with_check: Redirect desktop notifications to the smartwatch
- :ballot_box_with_check: Redirect call notifications to the smartwatch
- :ballot_box_with_check: Accept or hangup calls from the smartwatch
- :black_square_button: Make possible to control MPRIS applications from the smartwatch
- :black_square_button: Make possible to receive navigation instructions on the smartwatch

