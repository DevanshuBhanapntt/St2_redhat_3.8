#!/usr/bin/env bash

echo "Starting prerequisite steps and package installs"
echo "Installing Package GPG and Repo GPG Keys"
rpm --import '../key/server-4.0.asc'
rpm --import '../key/nginx_signing.key'
rpm --import '../key/erlang_gpg.key'
rpm --import '../key/erlang_signing.asc'
rpm --import '../key/rabbitmq_gpg.key'
rpm --import '../key/rabbitmq-release-signing-key.asc'
rpm --import '../key/st2_gpg.key'

echo "Disabling nodejs module"
yum module disable -y nodejs

echo "Setting up static repos"
cp '../repo/mongo.repo' '/etc/yum.repos.d/mongodb-org-4.repo'
cp '../repo/st2.repo' '/etc/yum.repos.d/StackStorm_stable.repo'
cp '../repo/nginx.repo' '/etc/yum.repos.d/nginx.repo'
cp '../repo/erlang.repo' '/etc/yum.repos.d/rabbitmq_erlang.repo'
cp '../repo/rabbitmq.repo' '/etc/yum.repos.d/rabbitmq_rabbitmq-server.repo'

echo "Disabling epel nginx"
sudo sed -i 's/^\(enabled=1\)$/exclude=nginx\n\1/g' /etc/yum.repos.d/epel.repo

echo "Installing and Setting up Nodejs 14 for Chatops"
rpm -i --nosignature --force '../nodepackage/*.rpm'
sudo sed -i 's/enabled=1/enabled=0/g' /etc/yum.repos.d/nodesource-el8.repo
sudo sed -i 's/gpgcheck=1/gpgcheck=0/g' /etc/yum.repos.d/nodesource-el8.repo
sudo sed -i '/failovermethod=priority/d' /etc/yum.repos.d/nodesource-el8.repo

echo "Installing local packages"
#cd ../packages && yum -y localinstall --skip-broken *.rpm
cd ../packages && yum -y localinstall *.rpm

echo "Moving back to the scripts directory"
cd ../scripts
echo "Finished prerequisite steps and package installs"
