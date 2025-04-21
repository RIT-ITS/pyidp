#!/usr/bin/env bash

# Build and test the docker image, not used in CI. All references to usernames and passwords
# are local.

set -euo pipefail

HERE=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE="$(realpath "${HERE}/../../")"

PEM_KEY=$(cat <<EOF
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDglC0LJs8lRLLb
HL524Fa4uaQexHriLvYXy9RVWEWLFjiXhleUkCLjk0Mav/LvVrf6WLNggi2JzoUR
V1qrWIKMFRmSPDu17F/RXjGNggBkTBfQlXVBAWPUa4ZcbKP70IR6ADmkPeDl5m8M
mmd8wVoCiURkar9KsYV6lbii0yx+CRdREbpMTahA8UDx382ARCx+iTe04oGBFp39
IqtfihPPbEl9O6aKqR1PFT2/faORkQLrfXBw9IB3kyjqTgd4PAFGs03q1FSuh1q/
J5gbeSUX+faQ/f5vRqCW5JLC+k0xJHqzB+NGDS0tP11u5Tl3OlKiAYxr1a3ipJhJ
45xKFPN1AgMBAAECggEAETOQSqsfkSt0pp9KQGk5Az+m4Dts7R+rNlHkst/GvdtH
HOYLlcO/hF5edLFQnn/uKhT6slDuQ4CnxRcDiR3HrAqesYp/CVVwVmVIVt4nAQeq
CE42U7MTTi0pNrGUkuBbEUwsnhWmQP24MkcuV4ooxop0jFt3yPUVc/j9Ui1qGkIb
wksOC17VAsVCmmsYzpWqL0ZSipxIzDTDeGjQDP2LoNivy8OaNpdOedffvSWO4GbF
NBATjvsErixWBP5Y2cOvswud5tep8NXJ+uMKvHMWLoHMatW9UE0kfRjLJqadSA/L
58u1fY8gPcI8nNqIR4El47O/xW1ZuiyP9y3QDuZ+uQKBgQD2PsiibFq4+8hdZ/jR
Z49hs4BezyUW3cYG6BsvLwYe1QKg2vCLslFWR28VN2elvFKj+aL/YlzDntq/gHqc
3FDoWx5D/nlBWtoJ0+RaLlk63ljATIEgadod4Yybj7+OuDDie8eVepZtMTwdODmY
NaEZ7SnoTfaLgJOznTQQyXha3QKBgQDpeatJWOK13bVEzy+1v1uyWunzlflryTDc
LSZd5McXKlxdyIjkCYrwN2DscQT4NmNtwW27ZbHAYZY+46fLjTdUS9atNcCJEeCN
toqyhaueaTZftbWVNLbqWclsvetUecn+g6Qk+3XXlwLctfSW3Qh3rzz6AIQHv3E8
M4ZDIyd1eQKBgQCoO0CLZwecNbgvyGa/eccFcsMTAuZN9vnhohVgaPn/enuvNaT9
a7gR//+uOQoAuuaizFxFqgfCRfcgukAKhqJn/EhzH5nrwowQBsmNqvifNWThC+N0
J50yqPONG+o9MS2Erhgu0W+P7gEp3U3L5WfI9LSa1xjHOfKu1YnKpjopqQKBgBz4
X+yl/tuaOxfirYTbzcD/zu/OuDhLqqhnYc9cx+dz9ioc6/9/v6G2/WvZSkiSVxwT
WE5cfAXnFgGPtg5n42muT2EGvnFDqp1q/SLRu03YuEp//ZwaAmhp47h+iGjfA9V0
+DUujpzFvDEu0r61hotzTxmmXrunYaGasxo5jnfhAoGBAJdgBhVVUezRfBEn2GUL
PEkEpox51kiQNwaov/ngAUHfeFVKnpCE+Z4foHBUIklM+FJ6aQzsDTG1z6vqpsX+
fP1nK+MGzoEmeaIRM8LIV7dv7EFp8YXA8w2+kd7F2v9ypVHJLmpyv98ypdNMl+ZS
m5XUeSI0KUEc/DTYVZpU5C0f
-----END PRIVATE KEY-----
EOF
)

PEM_CRT=$(cat <<EOF
-----BEGIN CERTIFICATE-----
MIIDCzCCAfOgAwIBAgIUGGzOZiUM1dj/185zDVg9dOlSIIQwDQYJKoZIhvcNAQEL
BQAwFTETMBEGA1UEAwwKcHlpZHAudGVzdDAeFw0yNTA0MTkxNDEzMTVaFw0yNjA0
MTkxNDEzMTVaMBUxEzARBgNVBAMMCnB5aWRwLnRlc3QwggEiMA0GCSqGSIb3DQEB
AQUAA4IBDwAwggEKAoIBAQDglC0LJs8lRLLbHL524Fa4uaQexHriLvYXy9RVWEWL
FjiXhleUkCLjk0Mav/LvVrf6WLNggi2JzoURV1qrWIKMFRmSPDu17F/RXjGNggBk
TBfQlXVBAWPUa4ZcbKP70IR6ADmkPeDl5m8Mmmd8wVoCiURkar9KsYV6lbii0yx+
CRdREbpMTahA8UDx382ARCx+iTe04oGBFp39IqtfihPPbEl9O6aKqR1PFT2/faOR
kQLrfXBw9IB3kyjqTgd4PAFGs03q1FSuh1q/J5gbeSUX+faQ/f5vRqCW5JLC+k0x
JHqzB+NGDS0tP11u5Tl3OlKiAYxr1a3ipJhJ45xKFPN1AgMBAAGjUzBRMB0GA1Ud
DgQWBBTlx0USwJiwK0oiAeHyCt2dy0d1GzAfBgNVHSMEGDAWgBTlx0USwJiwK0oi
AeHyCt2dy0d1GzAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQAz
dcFTOi6bDvTYVlZ+TPgYDzcRQjociuUPnd9eJ0ePt8J0KvkxVsUqU9d5apo11ZF/
Dwk7tkUn7DKabqFqFRCqTWH2lgTk7KU0zAU3qwTqJtJs7aCFVBpMr2HgRug4fIC9
1RpQ1zaWxL4KW8lq+ik4UXHA3urduvtDVICDueyrF21JP6874RUba9/0II36R5em
Ix1a5xYUpt45ZByEqvOBp3y4430gu/dwFsRLi6oAuUrKac2ik6+7vGzOqGivmlZG
VYA5qmd0bf657HF19NxAVqJA0PnWvAuWJy960S0vKH1OtjINPtnXVPEJ4CKGxETV
tt2Ynob2hp6hdmLL0JAN
-----END CERTIFICATE-----
EOF
)

SP_METADATA=$(cat <<EOF
<?xml version="1.0"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
    entityID="https://dummy-sp.localhost/saml2">
    <md:SPSSODescriptor AuthnRequestsSigned="false" WantAssertionsSigned="false"
        protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:KeyDescriptor use="signing">
            <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
                <ds:X509Data>
                    <ds:X509Certificate>
                        MIIDBTCCAe2gAwIBAgIUZ5FClPZ+lln+GZGfZyraIJ+sx1owDQYJKoZIhvcNAQELBQAwEjEQMA4GA1UEAwwHdGVzdHJlcTAeFw0yNTA0MTQyMjExNTdaFw0yNjA0MTQyMjExNTdaMBIxEDAOBgNVBAMMB3Rlc3RyZXEwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCVa8uK85SxJjyIJyK+XN4j/fBTF3c4EsmSCB12ZgSjVJj43ABRKYqbWUUpXMotHBJj0TjdPSlRHrYFx75VIbAH/6PJZw0OeexcgxqZ2XlC0sV0A9Q8EmpluNInaGdTej3/vlRi8jEyLO65btS4bHGeXzLWejCkS3wRi/vM0+fm4ObmE/ZC+pdLwcj6o8mfalE3OITIgexmVx+a/+ixafKTcrGKG4pCd5UhDhDApJTFBGRi0Es5RU09m+Yv8NM91ltrv1urMUg/l7ziW8VAOlOTJpTty6zOVfBynxvrdfqI90RMii85KcwSv9+nbbZ/T5rm/q5cyyISe8uzJ+6QJMYjAgMBAAGjUzBRMB0GA1UdDgQWBBRTsqpyhK/sZuZFbTPdhc+Gt5FYBjAfBgNVHSMEGDAWgBRTsqpyhK/sZuZFbTPdhc+Gt5FYBjAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQBoSJmBA1S4zm1L8aJ1D5Devi+DZXVmjx+9HNetm8Kfn9FYBbBNBkuL9faEhgiiGZyNK61DciLhhyNZoc0g7fleoQMsaTI28qsbqAy3UCALwhBbhGnHzLdPGzDWvrldT/IGTRSazHc//zCFc2Mtml5KkobHbqO3mm78j4h1NAJoKYxp0qHjVmdBAWZfe85gLNf0HaJxaDgmZhQvL9cMpKJNHuUcMSbA0ZAaMcW+psa3qi2tmuU4iC7z5ACpUleNyuMB6OkGTmjxk5HwalNWcSRuF/EeOhO9RttZNTWWzrYNdcRubFf9fh7ynxOrh76M18/aRCnZ/pNfxh1QYfMdWhgO</ds:X509Certificate>
                </ds:X509Data>
            </ds:KeyInfo>
        </md:KeyDescriptor>
        <md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            Location="https://dummy-sp.localhost/saml2/acs"
            index="1" />
    </md:SPSSODescriptor>
</md:EntityDescriptor>
EOF
)

docker buildx build \
    --build-context "src=${WORKSPACE}/src/" \
    --build-context "dockerfiles=${WORKSPACE}/docker/pyidp" \
    -f "${WORKSPACE}/docker/pyidp.Dockerfile" "${WORKSPACE}" 

LAST_IMAGE="$(docker images --format "{{.ID}} {{.CreatedAt}}" | sort -rk 2 | awk 'NR==1{print $1}')"
echo "Last image: ${LAST_IMAGE}"

docker network create --driver bridge pyidp_test || true

docker run \
        --network pyidp_test \
        -eSECRET_KEY="secret-password" \
        -eBASE_URL="http://localhost:8000" \
        -eIDP_KEY="${PEM_KEY}" \
        -eIDP_CRT="${PEM_CRT}" \
        -eSP_METADATA="${SP_METADATA}" \
        -v"${WORKSPACE}/docker/pyidp/srv/www/entrypoint.sh:/srv/www/entrypoint.sh" \
        -p8000:80 \
        -it $LAST_IMAGE \
        "$@"
