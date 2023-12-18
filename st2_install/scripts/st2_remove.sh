#!/usr/bin/env bash

echo "Finished Uninstalling Stackstorm and its components"
echo "Stopping Services"
sudo sh -c "st2ctl stop || true"
sudo sh -c "systemctl stop nginx mongod rabbitmq-server redis || true"

echo "Cleaning up all core packages"
sudo sh -c "yum erase -y st2 st2chatops st2web mongodb-org* rabbitmq-server erlang* nginx nodejs redis"

echo "Delete User"
sudo sh -c "userdel -r stanley"
sudo sh -c "userdel -r redis"

echo "Delete User sudo"
sudo sh -c "rm -f /etc/sudoers.d/st2"

echo "Removing repos"
sudo sh -c "rm -f /etc/yum.repos.d/mongodb-org* /etc/yum.repos.d/StackStorm*"
sudo sh -c "rm -f /etc/yum.repos.d/nginx* /etc/yum.repos.d/nodesource*"
sudo sh -c "rm -f /etc/yum.repos.d/rabbitmq_erlang* /etc/yum.repos.d/*rabbitmq-server*"

echo "All content"
sudo sh -c "rm -rf /etc/st2 /etc/mongod* /etc/rabbitmq /etc/nginx /opt/stackstorm"
sudo sh -c "rm -rf /var/log/st2 /var/log/mongodb /var/log/rabbitmq /var/log/nginx /var/log/redis"
sudo sh -c "rm -rf /var/lib/rabbitmq /var/lib/mongo"
sudo sh -c "rm -rf /etc/redis/redis.conf /var/lib/redis /root/.st2 /root/.dbshell"

echo "Finished Uninstalling Stackstorm and its components"
