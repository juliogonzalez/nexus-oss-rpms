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
- CentOS7 x86_64
- AlmaLinux 8-9 x86_64
- RHEL7-8 x86_64
- Fedora (supported versions) x86_64
- Fedora Rawhide x86_64


The following distributions are not tested but building and installing should work:
- Amazon Linux 2

Besides, Sonatype Nexus Repository 2/3 installations done by the RPMs are [verified to work](#build-status) fine at:
- CentOS7 x86_64
- Amazon Linux 2018.03 x86_64
- Amazon Linux 2 x86_64
- openSUSE Leap 15.5 x86_64
