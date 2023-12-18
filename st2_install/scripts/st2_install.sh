#!/bin/bash

BOOTSTRAP_FILE='./st2_install_config.sh'

ARCH=`arch`
DEBTEST=`lsb_release -a 2> /dev/null | grep Distributor | awk '{print $3}'`
RHTEST=`cat /etc/redhat-release 2> /dev/null | sed -e "s~\(.*\)release.*~\1~g"`
VERSION=''
RELEASE='stable'
REPO_TYPE=''
ST2_PKG_VERSION=''
DEV_BUILD=''
USERNAME=''
PASSWORD=''
EXTRA_OPTS=''
SCRIPT=$(readlink -f "$0")
BASEDIR=$(dirname "$SCRIPT")

# Note: This variable needs to default to a branch of the latest stable release
BRANCH='v3.8'
FORCE_BRANCH=""

adddate() {
    while IFS= read -r line; do
        echo "$(date +%Y%m%dT%H%M%S%z) $line"
    done
}

local_setup() {
  sudo sh -c "./st2_install_pre.sh" | sudo tee -a $LOGFILE
}

log_file_setup() {
  LOGFILE="${BASEDIR}/st2_install.log"
  touch $LOGFILE
}

setup_args() {
  for i in "$@"
    do
      case $i in
          -v=*|--version=*)
          VERSION="${i#*=}"
          shift
          ;;
          -s|--stable)
          RELEASE=stable
          shift
          ;;
          -u|--unstable)
          RELEASE=unstable
          shift
          ;;
          --staging)
          REPO_TYPE='staging'
          shift
          ;;
          # Used to install the packages from CircleCI build artifacts
          # Examples: 'st2/5017', 'mistral/1012', 'st2-packages/3021',
          # where first part is repository name, second is CircleCI build number.
          --dev=*)
          DEV_BUILD="${i#*=}"
          shift
          ;;
          --user=*)
          USERNAME="${i#*=}"
          shift
          ;;
          --password=*)
          PASSWORD="${i#*=}"
          shift
          ;;
          # Used to specify which branch of st2-packages repo to use. This comes handy when you
          # need to use a non-master branch of st2-package repo (e.g. when testing installer script
          # changes which are in a branch)
          --force-branch=*)
          FORCE_BRANCH="${i#*=}"
          shift
          ;;
          # Provide a flag to enable installing Python3 from 3rd party insecure PPA for Ubuntu Xenial
          # TODO: Remove once Ubuntu Xenial is dropped
          --u16-add-insecure-py3-ppa)
          EXTRA_OPTS="--u16-add-insecure-py3-ppa"
          shift
          ;;
          *)
          # unknown option
          ;;
      esac
    done

  if [[ "$VERSION" != '' ]]; then
    if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] && [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+dev$ ]]; then
      echo "$VERSION does not match supported formats x.y.z or x.ydev" | sudo tee -a $LOGFILE
      exit 1
    fi

    if [[ "$VERSION" =~ ^[0-9]+\.[0-9]+dev$ ]]; then
     echo "You're requesting a dev version! Switching to unstable!" | sudo tee -a $LOGFILE
     RELEASE='unstable'
    fi
  fi

  if [[ "$USERNAME" = '' || "$PASSWORD" = '' ]]; then
    USERNAME=${USERNAME:-st2admin}
    PASSWORD=${PASSWORD:-Ch@ngeMe}
    echo "You can use \"--user=<CHANGEME>\" and \"--password=<CHANGEME>\" to override following default st2 credentials." | sudo tee -a $LOGFILE
    SLEEP_TIME=10
    echo "Username: ${USERNAME}" | sudo tee -a $LOGFILE
    echo "Password: ${PASSWORD}" | sudo tee -a $LOGFILE
    echo "Sleeping for ${SLEEP_TIME} seconds if you want to Ctrl + C now..." | sudo tee -a $LOGFILE
    sleep ${SLEEP_TIME}
    echo "Resorting to default username and password... You have an option to change password later!" | sudo tee -a $LOGFILE
  fi
}

log_file_setup
setup_args $@

# Note: If either --unstable or --staging flag is provided we default branch to master
if [[ "$RELEASE" == 'unstable' ]]; then
  BRANCH="master"
fi

if [[ "$REPO_TYPE" == 'staging' ]]; then
  BRANCH="master"
fi

if [[ "$DEV_BUILD" != '' ]]; then
  BRANCH="master"
fi

get_version_branch() {
  if [[ "$RELEASE" == 'stable' ]]; then
      BRANCH="v$(echo ${VERSION} | awk 'BEGIN {FS="."}; {print $1 "." $2}')"
  fi
}

if [[ "$VERSION" != '' ]]; then
  get_version_branch $VERSION
  VERSION="--version=${VERSION}"
fi

if [[ "$RELEASE" != '' ]]; then
  RELEASE="--${RELEASE}"
fi

if [[ "$REPO_TYPE" == 'staging' ]]; then
  REPO_TYPE="--staging"
fi

if [[ "$DEV_BUILD" != '' ]]; then
  DEV_BUILD="--dev=${DEV_BUILD}"
fi

if [[ "${FORCE_BRANCH}" != "" ]]; then
  BRANCH=${FORCE_BRANCH}
fi

USERNAME="--user=${USERNAME}"
PASSWORD="--password=${PASSWORD}"

if [[ "$ARCH" != 'x86_64' ]]; then
  echo "Unsupported architecture. Please use a 64-bit OS! Aborting!" | sudo tee -a $LOGFILE
  exit 2
fi

if [[ -n "$RHTEST" ]]; then
  TYPE="rpms"
  echo "*** Detected Distro is ${RHTEST} ***" | sudo tee -a $LOGFILE
  RHMAJVER=`cat /etc/redhat-release | sed 's/[^0-9.]*\([0-9.]\).*/\1/'`
  echo "*** Detected distro version ${RHMAJVER} ***" | sudo tee -a $LOGFILE
  if [[ "$RHMAJVER" != '6' && "$RHMAJVER" != '7' && "$RHMAJVER" != '8' ]]; then
    echo "Unsupported distro version $RHMAJVER! Aborting!" | sudo tee -a $LOGFILE
    exit 2
  fi
elif [[ -n "$DEBTEST" ]]; then
  TYPE="debs"
  echo "*** Detected Distro is ${DEBTEST} ***" | sudo tee -a $LOGFILE
  SUBTYPE=`lsb_release -a 2>&1 | grep Codename | grep -v "LSB" | awk '{print $2}'`
  echo "*** Detected flavor ${SUBTYPE} ***" | sudo tee -a $LOGFILE
  if [[ "$SUBTYPE" != 'xenial' && "$SUBTYPE" != 'focal' && "$SUBTYPE" != 'bionic' ]]; then
    echo "Unsupported ubuntu codename ${SUBTYPE}. Please use 16.04 (xenial) or Ubuntu 18.04 (bionic) or Ubuntu 20.04 (focal) as base system!" | sudo tee -a $LOGFILE
    exit 2
  fi
else
  echo "Unknown Operating System" | sudo tee -a $LOGFILE
  exit 2
fi

echo "Running deployment script for st2 ${VERSION}..." | sudo tee -a $LOGFILE
echo "OS specific script cmd: bash ${BOOTSTRAP_FILE} ${VERSION} ${RELEASE} ${REPO_TYPE} ${DEV_BUILD} ${USERNAME} --password=****" | sudo tee -a $LOGFILE
TS=$(date +%Y%m%dT%H%M%S) | sudo tee -a $LOGFILE
sudo mkdir -p /var/log/st2
local_setup
echo "Version :  $VERSION"
echo "Release : $RELEASE"
echo "Repo Type : $REPO_TYPE"
echo "Dev Build : $DEV_BUILD"
echo "Username : $USERNAME"
#echo "Password : $PASSWORD"
echo "Extra Opts : $EXTRA_OPTS"

bash ${BOOTSTRAP_FILE} ${VERSION} ${RELEASE} ${REPO_TYPE} ${DEV_BUILD} ${USERNAME} ${PASSWORD} ${EXTRA_OPTS} 2>&1 | adddate | sudo tee -a $LOGFILE
exit ${PIPESTATUS[0]}
