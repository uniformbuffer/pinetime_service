# Pinetime service daemon

This daemon can detect paired devices and enable features based on the bluetooth services they offer. 
It detect paired devices at launch and listen for new paired or unpaired devices.
For pairing it is possible to use any tool that allow it. The daemon will listen directly to `org.bluez` bus to detect such operation, so any pairing tool should work.

The daemon can be launched simply with `python3 main.py`.

After pairing, all the services offered by the device (and supported by the daemon) will be enabled.
What currently works is:

Project features:
- :ballot_box_with_check: Gathering all the paired devices and look for services for each of them
- :ballot_box_with_check: Detect when a device is paired or unpaired
- :x: Reconnect device in case of disconnection: it is very difficult to handle it properly from the daemon. It would be better handled by the DE bluetooth service
- :black_square_button: Proper packaging
- :black_square_button: Documentation

Host services:
- :ballot_box_with_check: Detect desktop notifications
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
- :black_square_button: Sync time
- :black_square_button: Navigation


InfiniTime services:
- :ballot_box_with_check: Send alert notifications  to the smartwatch
- :ballot_box_with_check: Send call notifications to the smartwatch
- :ballot_box_with_check: Hangup, accept and mute notifications from the call notification
- :ballot_box_with_check: Media control

Interaction services:
- :ballot_box_with_check: Redirect desktop notifications to the smartwatch
- :ballot_box_with_check: Redirect call notifications to the smartwatch
- :ballot_box_with_check: Accept or hangup calls from the smartwatch
- :ballot_box_with_check: Control MPRIS applications from the smartwatch
- :black_square_button: Receive navigation instructions on the smartwatch

