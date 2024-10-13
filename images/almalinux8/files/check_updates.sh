#!/bin/bash
# This script will check for package upgrades and will return:
# - 0 if no upgrades were available
# - 1 if upgrades were available for at least one package not present at parent
#     image
# - 2 if upgrades were available for at least one packages at parent image
# - 3 if upgrades were available fot at least one package not present at parent
#     image, and at least one present at the parent image

PACKAGES_ORIG='/opt/packages-image.txt'
PACKAGES_UPDATES='/opt/packages-updates.txt'

yum list updates|awk 'f;/^Updated Packages/{f=1}'|cut -d'.' -f1 > ${PACKAGES_UPDATES}

EXIT=0
PFOUND=0
CFOUND=0
PPACKAGES_UPDATES=''
CPACKAGES_UPDATES=''

while read UPDATE; do
  FOUND=0
  while read ORIGINAL; do
    if [ "${UPDATE}" == "${ORIGINAL}" ]; then
      FOUND=1
      PPACKAGES_UPDATES="${PPACKAGES_UPDATES} ${UPDATE}"
    fi
  done < ${PACKAGES_ORIG}
  if [ $FOUND -eq 1 ]; then
    PFOUND=2
  else
    CFOUND=1
    CPACKAGES_UPDATES="${CPACKAGES_UPDATES} ${UPDATE}"
  fi
done < ${PACKAGES_UPDATES}

if [ "${PPACKAGES_UPDATES}" != "" ]; then
  echo "=================================================================="
  echo "            PACKAGES FROM PARENT IMAGE REQUIRING UPDATE"
  echo "=================================================================="
  for PACKAGE in ${PPACKAGES_UPDATES}; do
    echo "${PACKAGE}"
  done;
fi

if [ "${CPACKAGES_UPDATES}" != "" ]; then
  echo "=================================================================="
  echo "           PACKAGES FROM CURRENT IMAGE REQUIRING UPDATE"
  echo "=================================================================="
  for PACKAGE in ${CPACKAGES_UPDATES}; do
    echo "${PACKAGE}"
  done;
fi

exit $((${EXIT}+${PFOUND}+${CFOUND}))
