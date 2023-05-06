# Requirements

To build the RPM:
- rpm-build
- curl
- tar
- gz

To run Sonatype Nexus Repository:
- [OpenJDK JRE 1.8 installed](https://help.sonatype.com/repomanager2/system-requirements) (no other Java versions are supported by Sonatype Nexus Repository right now)

# How to build

```
./nexus-oss-rpm -v 2
```
# Daemon

Sonatype Nexus Reposutory configuration has been customized, so it behaves
more like a "real" daemon, listening at port 8081 (you can change it at
/etc/nexus/nexus.properties).

The RPM will create a user called 'nexus' to run Nexus OSS.

Sonatype Nexus Repository will not be configured to start automatically on
boot and will not even start after installation.

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
