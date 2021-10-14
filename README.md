# Pinetime service daemon

Currently the daemon is capable to detect devices only on start, there is no "new device discovery" nor reconnection. 
I'm currently working to improve this situation, it is just a matter to decide the best approach to the problem.
Differently from other daemons for such purpose, the smartwatch must be paired to be detected.

So, overall, the steps are:
- Pair the smartwatch using some system tool (for example from Gnome control center or Plasma settings)
- Launch the daemon with `python3 main.py`

At launch it will detect all the paired devices and it will enable all the services both the host and the smartwatch support. What currently work is:

Generic features:
- [x] Gathering all the paired devices and look for services for each of them
- [ ] Reconnect device in case of disconnection
- [ ] Proper packaging
- [ ] Documentation

Device services:
- [x] Heart rate reading
- [x] Heart rate notification
- [x] Battery level reading
- [x] Battery level notification
- [x] Notification send (for both the "message" style and "call" style)
- [x] Hardware revision reading
- [x] Software revision reading
- [x] Firmware revision reading
- [x] Generic device info like alias, address and so on
- [ ] Step counter reading (currently impossible, such service is not exposed by InfiniTime)
- [ ] Step counter notification (currently impossible, such service is not exposed by InfiniTime)

System (host) services:
- [x] Read desktop notifications
- [x] Detect calls from Gnome Calls
- [x] Detect opening and closing of MPRIS enabled applications

Combined features:
- [x] Redirect desktop notifications to the smartwatch
- [x] Redirect call notifications to the smartwatch
- [ ] Make possible to control MPRIS applications from the smartwatch
