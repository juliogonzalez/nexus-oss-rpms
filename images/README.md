# Nexus Docker images for Continous Integration

Current distributions available:

* CentoS 7 (EoL)
* Amazon Linux 2018.03 (EoL)
* AlmaLinux 8
* Amazon Linux 2
* openSUSE Leap 15.5
* openSUSE Leap 15.6

# Building images

Run:

```
./manage_images -h
```

# docker-systemctl-replacement

The systemd replacement used for the docker images comes from https://github.com/gdraheim/docker-systemctl-replacement (commit [03e8582](https://github.com/gdraheim/docker-systemctl-replacement/tree/03e8582d8096c0c5261b2261b892348504ce9553))and it is licensed under the [EUROPEAN UNION PUBLIC LICENCE v. 1.2](EUPL-LICENSE.md)
