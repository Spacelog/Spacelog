# Deploying Spacelog

Most of this could be turned into chef, but hasn't been because it doesn't happen often. Start with Ubuntu 16.04, and then as root. The very first command requires you to select the UTC timezone before continuing (it's under "None of the above").

```sh
dpkg-reconfigure tzdata # None of the above > UTC
apt-get update && apt-get upgrade
apt-get purge -y postfix samba samba-libs samba-common samba-common-bin python-samba
a2dismod -f auth_basic authn_core authn_file authz_host authz_user autoindex dir filter status
a2disconf other-vhosts-access-log serve-cgi-bin
a2enmod proxy proxy_http
a2dissite 000-default
sed -i -e 's/Listen 80/Listen 8080/'  /etc/apache2/ports.conf
mkdir /var/log/apache2/spacelog.org
apt-get install -y libffi-dev libssl-dev python-setuptools python-pip redis-server python-redis python-virtualenv imagemagick optipng procps python-xapian varnish
service varnish stop
mkdir /etc/systemd/system/varnish.service.d
echo -e "[Service]\nExecStart=\nExecStart=/usr/sbin/varnishd -a :80 -F -T localhost:6082 -f /etc/varnish/default.vcl -S /etc/varnish/secret -s malloc,256m" > /etc/systemd/system/varnish.server.d/customexec.conf
systemctl daemon-reload
service varnish start
```

This will leave varnish running on port 80 (with admin on 6082, bound to localhost), redis running (bound to localhost only) on port 6379, and apache2 (with most things disabled) on port 8080. The only other listening service should be sshd on port 22.

Then we need to set up a user to run the app servers. Set a password in the first step.

```sh
adduser spacelog
adduser spacelog sudo
mkdir ~spacelog/{archives,releases} && chown spacelog:spacelog ~spacelog/{archives,releases}
echo '@reboot cd /home/spacelog/releases/current && make gunicornucopia' | crontab
```

Now add a suitable ssh authorized key into the new spacelog account.

Finally we have to get the Spacelog code onto the instance. From a development machine (with access to the private part of the ssh key you set up for the spacelog account, and with `host` being whatever the ip address or hostname of the live machine):

```sh
fab -H host deploy:bootstrap=true
fab -H host update_vhosts
```

The latter uses sudo, so it will prompt you for the password. The vhost configuration files don't change often, so it's unlikely you'll need to do this more than once.

## Remaining

 * is varnish actually doing anything for the HTML pages?
 * we should use a ManifestStaticFilesStorage variant that puts the manifest (staticfiles.json) in the project root (~spacelog/releases/current/website or ~spacelog/releases/current/global)
 * template caching
 * should `make dirty` also do `make collectstatic`? There's no point doing `make productioncss` otherwise, surely? Maybe this was lying around from pre-Manifest / staticfiles days, and should be dropped entirely.
 * fail2ban sshd rules, munin + firewall
