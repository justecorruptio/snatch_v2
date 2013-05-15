#!/usr/bin/env bash

#  This script must be idempotent.

# on first boot:
#    expand_rootfs
#    change_pass

A='\e[1;32m'
Z='\e[0m'

echo -e "${A}Initializing Raspberry Pi${Z}"

echo -e "${A}Installing packages from apt${Z}"
if [ ! -e /tmp/.apt_is_updated ] ; then apt-get update; fi
touch /tmp/.apt_is_updated
apt-get -y install git python-pip supervisor

echo -e "${A}Installing packages from pip${Z}"
pip install tornado sockjs-tornado

echo -e "${A}Stopping services${Z}"
supervisorctl stop tornado
/etc/init.d/supervisor stop

echo -e "${A}Installing server from git${Z}"
cd /usr/local
rm -rf snatch
git clone http://github.com/justecorruptio/snatch_v2.git snatch

echo -e "${A}Updating supervisor settings${Z}"
echo '
[unix_http_server]
file=/var/run//supervisor.sock
chmod=0700
[supervisord]
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid
childlogdir=/var/log/supervisor

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///var/run//supervisor.sock ; use a unix:// URL  for a unix socket

[program:tornado]
command=/usr/local/snatch/run_tornado.py
' > /etc/supervisor/supervisord.conf

echo -e "${A}Starting services${Z}"
/etc/init.d/supervisor start
supervisorctl start tornado

echo -e "${A}Done initializing Raspberry pi.${Z}"
