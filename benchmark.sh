#! /bin/sh
CA_CERT=ca.example.com.crt
MY_KEY=benchmark.key

if [ ! -f $MY_KEY ];
then
    openssl genrsa -out $MY_KEY 2048
fi

POST_URL=https://caramel.modio.se/


for x in $(seq 100000);
do
    CLIENTID=$(cat /proc/sys/kernel/random/uuid)
    SUBJECT="/C=SE/O=Modio Caramel Public/OU=Caramel/CN=$CLIENTID"
    MY_CSR="$CLIENTID".csr
    openssl req -new -key $MY_KEY -out  $MY_CSR -utf8 -sha256 -subj  "$SUBJECT"
done
