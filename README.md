# CAUTION

Nexus 3.71.0-06 and newer will not support neither Java 1.8 or OrientDB (which used to be the default database).

The migration to Java 17 is performed automatically by the package, if the OS provides it (so for example CentOS7 and clones will not be supported anymore)

However the migration to H2/PostgreSQL needs to be performed MANUALLY. If you are still using OrientDB (you did not perform a migration), Make sure you read the [Sonatype Nexus Database Migration documentation](https://help.sonatype.com/en/migrating-to-a-new-database.html) and run the procedure before updating to Nexus 3.71.0-06 or any newer version!

# Buy me a beer

If you find this repository useful, you can [Buy me a beer](https://www.buymeacoffee.com/juliogonzalez) 🍺

# Build status

- Sonatype Nexus Repository 2: [![Build Status](https://jenkins.juliogonzalez.es/job/nexus2-oss-rpms-build/badge/icon)](https://jenkins.juliogonzalez.es/job/nexus2-oss-rpms-build/)
- Sonatype Nexus Repository 3: [![Build Status](https://jenkins.juliogonzalez.es/job/nexus3-oss-rpms-build/badge/icon)](https://jenkins.juliogonzalez.es/job/nexus3-oss-rpms-build/)

# Introduction

This repository holds files and scripts to build Sonatype Nexus Repository 2.x and 3.x RPM packages. It also has required stuff to perform Continuous Integration.

# Licenses

- Sonatype Nexus Repository: EPL-2.0, Sonatype
- docker-systemctl-replacement: EUPL 1.2, Guido U. Draheim
- Scripts and Spec and everything else: AGPL, Jens Braeuer <braeuer.jens@googlemail.com>, Julio Gonzalez Gil <git@juliogonzalez.es>

# Requirements, building and configuring:

- [Sonatype Nexus Repository 2.x](NEXUS2.md)
- [Sonatype Nexus Repository 3.x](NEXUS3.md)

# Current state

The SPEC is [verified to build](https://build.opensuse.org/project/show/home:juliogonzalez:devops), and the produce RPMs able to install on:
- SLE12 (supported SPs) x86_64
- SLE15 (supported SPs) x86_64
- openSUSE Leap 15.X (supported versions) x86_64
- openSUSE Tumbleweed x86_64 
- AlmaLinux 8-9 x86_64
- RHEL7-8 x86_64
- Fedora (supported versions) x86_64
- Fedora Rawhide x86_64


The following distributions are not tested but building and installing should work:
- Amazon Linux 2

Besides, Sonatype Nexus Repository 2/3 installations done by the RPMs are [verified to work](#build-status) fine at:
- AlmaLinux 8 x86_64
- Amazon Linux 2 x86_64
- openSUSE Leap 15.6 x86_64
