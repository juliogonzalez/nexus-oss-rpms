# Requirements

To build the RPM:
- rpm-build
- curl
- tar
- gz

To run Nexus:
- Any JDK/JRE (Oracle or OpenJDK) 1.7 or 1.8 installed (it is not
  included as dependency because CentOS 7 does not provide a virtual
  package for Java).

# How to build

```
./nexus-oss-rpm -v 2
```
# Daemon

Nexus configuration has been customized, so Nexus behaves more like a
"real" daemon, listening at port 8081 (you can change it at
/etc/nexus/nexus.properties).

The RPM will create a user called 'nexus' to run Nexus OSS.

Nexus will not be configured to start automatically on boot and will
not even start after installation.

You can do both things by running:

```
chkconfig --add nexus
service nexus start
```
Or if your system uses systemd (Fedora >= 18, RHEL/CentOS >=7,
openSUSE >= 42.1, Amazon Linux >= 2...):
```
systemctl enable nexus
systemctl start nexus
```

# Linux-like directories

- Data: /var/lib/nexus
- Logfiles: /var/log/nexus
- Pidfile: /var/run/
- Conf: /etc/nexus
- Init file: /etc/init.d/nexus
