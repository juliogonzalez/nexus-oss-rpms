FROM docker.io/library/almalinux:8
MAINTAINER Julio Gonzalez Gil <git@juliogonzalez.es>

USER root

# Default UID/GID for mounting folders (used at jenkins slaves)
ARG UID=500
ARG GID=500

# Add the wrapper to check for updates and the systemd replacement
ADD files/* /opt/

# Pass the output of date command as DATE argument if you want 
# make sure that the image is generated using the lastest 
# packages (cache will be used for previous steps)
ARG DATE=None

# Generate a list of original packages, update, install needed
# packages and replace systemd
RUN rpm -qa --qf "%{NAME}\n" > /opt/packages-image.txt && \
    dnf -y -q update && \
    dnf -y -q install \
     java-1.8.0-openjdk \ 
     java-17-openjdk \
     systemd-sysv \
     rpm-build && \
    cp /opt/systemctl.py /usr/bin/systemctl && \
    yum -q clean all # ${DATE}

# Create ci group and user according to arguments UID/GID
RUN groupadd -g ${GID} ci && \
    useradd -d /home/ci -m -u ${UID} -g ${GID} ci

STOPSIGNAL SIGRTMIN+3

CMD ["/bin/bash", "/opt/start_wait.sh"]
