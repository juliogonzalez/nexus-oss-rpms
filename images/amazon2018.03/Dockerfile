FROM docker.io/amazonlinux:2018.03 
MAINTAINER Julio Gonzalez Gil <git@juliogonzalez.es>

USER root

# Default UID/GID for mounting folders (used at jenkins slaves)
ARG UID=500
ARG GID=500

# Create the wrappers to check for updates and to keep the container running
ADD files/*.sh /opt/

# Pass the output of date command as DATE argument if you want 
# make sure that the image is generated using the lastest 
# packages (cache will be used for previous steps)
ARG DATE=None

# Generate a list of original packages, install EPEL repository, update,
# install needed packages and create symlink for qmake-qt5
RUN rpm -qa --qf "%{NAME}\n" > /opt/packages-image.txt && \
    yum -y -q update && \
    yum -y -q install \
     java-1.8.0 \
     procps \
     rpm-build \
     shadow-utils \
     systemd-sysv \
     util-linux && \
    yum -q clean all # ${DATE}

# Create ci group and user according to arguments UID/GID
RUN groupadd -g ${GID} ci && \
    useradd -d /home/ci -m -u ${UID} -g ${GID} ci

CMD ["/bin/bash", "/opt/start_wait.sh"]
