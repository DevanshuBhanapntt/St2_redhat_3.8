[StackStorm_stable]
name=StackStorm_stable
baseurl=https://packagecloud.io/StackStorm/stable/el/8/$basearch
repo_gpgcheck=1
gpgcheck=0
enabled=1
gpgkey=https://packagecloud.io/StackStorm/stable/gpgkey
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
metadata_expire=300

[StackStorm_stable-source]
name=StackStorm_stable-source
baseurl=https://packagecloud.io/StackStorm/stable/el/8/SRPMS
repo_gpgcheck=1
gpgcheck=0
enabled=1
gpgkey=https://packagecloud.io/StackStorm/stable/gpgkey
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
metadata_expire=300