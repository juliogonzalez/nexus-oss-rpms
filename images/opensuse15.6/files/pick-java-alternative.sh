#!/bin/bash
JAVA_VER="${1}"
JAVA_ALTERNATIVE="$(update-alternatives --display java|grep '^/'|cut -d ' ' -f1|grep ${JAVA_VER})"
update-alternatives --set java "${JAVA_ALTERNATIVE}"
