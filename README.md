# ansible-snakeoil

build a simple snakeoil certificate for a test environment.

we use as base dn *cm.local*

## manuel creation

```
cat > csr_details.txt <<-EOF
[req]
default_bits = 4096
prompt = no
default_md = sha512
req_extensions = req_ext
distinguished_name = dn

[ dn ]
C=DE
ST=Hamburg
L=Hamburg
O=Acme, Inc
OU=Testing Domain
emailAddress=cert@cm.local
CN = *.cm.local

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1  = cm.local
DNS.2  = database.cm.local
DNS.3  = backend.cm.local
DNS.4  = frontend.cm.local
DNS.5  = delivery.cm.local
DNS.6  = monitoring.cm.local
DNS.7  = mysql.cm.local
DNS.8  = mongo.cm.local
DNS.9  = *.delivery.cm.local
DNS.10 = *.backend.cm.local
DNS.11 = overview.cm.local
DNS.12 = corporate.cm.local
DNS.13 = studio.cm.local
DNS.14 = preview.cm.local
DNS.15 = *.be.cm.local
DNS.16 = *.fe.cm.local
IP.1   = 192.168.124.10
IP.2   = 192.168.124.20
IP.3   = 192.168.124.30
IP.4   = 192.168.124.35
IP.5   = 192.168.124.50
EOF

# Let’s call openssl now by piping the newly created file in
openssl req -new -sha512 -nodes -out cm.local.csr -newkey rsa:4096 -keyout cm.local.key -config <( cat csr_details.txt )
openssl dhparam -out dh.pem 2048

#
openssl req -noout -verify -in cm.local.csr
openssl req -text -noout -in cm.local.csr

#
openssl x509 -in cm.local.csr -out cm.local.pem -req -signkey cm.local.key -days 29

cat cm.local.key >> cm.local.pem
```

