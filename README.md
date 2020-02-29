# Build status

- Nexus2: [![Build Status](https://jenkins.juliogonzalez.es/job/nexus2-oss-rpms-build/badge/icon)](https://jenkins.juliogonzalez.es/job/nexus2-oss-rpms-build/)
- Nexus3: [![Build Status](https://jenkins.juliogonzalez.es/job/nexus3-oss-rpms-build/badge/icon)](https://jenkins.juliogonzalez.es/job/nexus3-oss-rpms-build/)

# Introduction

This repository holds files and scripts to build Sonatype Nexus 2.x and 3.x RPM packages. It also has required stuff to perform Continuous Integration.

# Licenses

- Nexus OSS: EPL-2.0, Sonatype
- Scripts and Spec: AGPL, Jens Braeuer <braeuer.jens@googlemail.com>,
  Julio Gonzalez Gil <git@juliogonzalez.es>

# Requirements, building and configuring:

- [Nexus 2.x](NEXUS2.md)
- [Nexus 3.x](NEXUS3.md)

# Current state

The SPEC is [verified to build](https://build.opensuse.org/project/show/home:juliogonzalez:devops), and the produce RPMs able to install on:
- SLE12SP3-SP5 x86_64
- SLE15GA-SP2 x86_64
- openSUSE Leap 42.3 x86_64
- openSUSE Leap 15.0-15.2 x86_64
- openSUSE Tumbleweed x86_64 
- CentOS6-8 x86_64
- RHEL6-8 x86_64
- Fedora 30-31 x86_64
- Amazon Linux 1 x86_64

The following distributions are not tested but building and installing should work:
- Amazon Linux 2

Besides, Nexus2/3 installations done by the RPMs are [verified to work](#build-status) fine at:
- CentOS6 x86_64
- CentOS7 x86_64
- Amazon Linux 2018.03 x86_64
- openSUSE Leap 15.1 x86_64
