# CAUTION

Sonatype retired Nexus 3.67.0-03 (3.67.0.03-1 at this repository) because of two important failures.

Read all the details at the [3.67.0 release notes](https://help.sonatype.com/en/sonatype-nexus-repository-3-67-0-release-notes.html) and do not upgrade if you are affected.

Update to 3.67.1-01 or later (3.67.1.01-1 at this repository, or later) as soon as possible.

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
