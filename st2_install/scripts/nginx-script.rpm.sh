cat <<EOT > /etc/yum.repos.d/nginx.repo
[nginx]
name=nginx repo
baseurl=http://nginx.org/packages/rhel/8/x86_64/
gpgcheck=1
enabled=1
EOT
