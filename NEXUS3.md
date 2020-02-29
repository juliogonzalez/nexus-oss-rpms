# Requirements

To build the RPM:
- rpm-build
- curl
- tar
- gz

To run Nexus:
- Any JDK/JRE (Oracle or OpenJDK) 1.8 installed (it is not included
  as dependency because CentOS 7 does not provide a virtual package for
  Java).

# How to build

```
./nexus-oss-rpm -v 3
```

# Upgrading from 2.x

According to [Nexus documentation](https://books.sonatype.com/nexus-book/reference3/upgrading.html) it is possible to upgrade from
Nexus 2.14.4 to Nexus 3.3.1 (among other options). You can generate all the required RPMs with this repository, but please carefully
read the documentation, and keep in mind that at this moment [Yum repositories are not available yet](https://support.sonatype.com/hc/en-us/articles/222426568-Nexus-Repository-Manager-Feature-Compatibility-Matrix)

# Daemon

Nexus configuration has been customized, so Nexus behaves more like a
"real" daemon, listening at port 8081 (you can change it at
/etc/nexus3/org.sonatype.nexus.cfg).

The RPM will create a user called 'nexus3' to run Nexus OSS.

Nexus will not be configured to start automatically on boot and will
not even start after installation.

You can do both things by running:

```
chkconfig --add nexus3
service nexus3 start
```
Or if your system uses systemd (Fedora >= 18, RHEL/CentOS >=7,
openSUSE >= 42.1, Amazon Linux >= 2...):
```
systemctl enable nexus3
systemctl start nexus3
```

# Linux-like directories

- Data: /var/lib/nexus3
- Logfiles: /var/log/nexus3
- Conf: /etc/nexus3
- Init file: /etc/init.d/nexus3
