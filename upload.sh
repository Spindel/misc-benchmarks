#! /bin/sh
CA_CERT=caramel.modio.se.cacert
POST_URL=https://caramel.modio.se
MY_CSR=$1
CSRSUM=$(sha256sum $MY_CSR |cut -f1 -d" ")
CURL_OPTS="--silent --show-error --remote-time --connect-timeout 300 --max-time 600 --cacert $CA_CERT"
curl ${CURL_OPTS} --data-binary @$MY_CSR ${POST_URL}/${CSRSUM} -o /dev/null
