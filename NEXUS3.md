# Requirements

To build the RPM:
- rpm-build
- curl
- tar
- gz

To run Sonatype Nexus Repository:
- [OpenJDK JRE 1.8 installed](https://help.sonatype.com/repomanager3/product-information/sonatype-nexus-repository-system-requirements#SonatypeNexusRepositorySystemRequirements-Java) (no other Java versions are supported by Sonatype Nexus Repository right now)


# How to build

```
./nexus-oss-rpm -v 3
```

# Upgrading from 2.x

According to [Sonatype Nexus Repository documentation](https://help.sonatype.com/repomanager3/installation-and-upgrades/supported-nexus-repository-manager-upgrade-paths) it is possible to upgrade from
the latest Sonatype Nexus Repository 2.x to the latest 3.x.

You can generate all the required RPMs with this repository, but please
carefully read the documentation

# Daemon

Sonatype Nexus Repository configuration has been customized, so it behaves
more like a "real" daemon, listening at port 8081 (you can change it at
/etc/nexus3/org.sonatype.nexus.cfg).

The RPM will create a user called 'nexus3' to run Sonatype Nexus Repository.

Sonatype Nexus Repository will not be configured to start automatically on
boot and will not even start after installation.

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
