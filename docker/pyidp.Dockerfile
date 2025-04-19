FROM python:3.13.3-alpine AS base

FROM base AS builder

RUN apk update && \
    apk add --no-cache \
    curl \
    libstdc++ \
    gcc \        
    musl-dev \
    libffi-dev \
    make \
    mariadb-dev \
    py3-virtualenv 

COPY --from=src ./ /code/

WORKDIR /code/

RUN pip3 install uv && \
    uv build && \
    uv export --no-emit-workspace --no-hashes -o requirements-frozen.txt

FROM base AS prod

ARG GUNICORN_VERSION=21.2.0

WORKDIR /srv/www

RUN apk update && \
     apk add --no-cache \
     bash \
     xmlsec \
     pkgconf 

# flask runs as the pyidp user and it needs to own
# the directory where gunicorn creates its socket
RUN adduser -S pyidp && \
     mkdir /run/pyidp && \
     chown pyidp /run/pyidp && \
     chmod 0750 /run/pyidp

COPY --from=builder --chown=pyidp /code/requirements-frozen.txt /opt/pyidp/requirements-frozen.txt
COPY --from=builder --chown=pyidp /code/dist/pyidp-*.whl /opt/pyidp/
    
RUN chown pyidp /srv/www
USER pyidp

RUN python3 -m venv /srv/www/.venv && \
     /srv/www/.venv/bin/pip install \
         --no-cache-dir \
         -c /opt/pyidp/requirements-frozen.txt \
         /opt/pyidp/pyidp-*.whl gunicorn==$GUNICORN_VERSION
 

# Overlay static configuration and runtime files
COPY --from=dockerfiles --chown=pyidp /srv /srv/
COPY --from=dockerfiles --chown=pyidp /etc /etc/

#FROM scratch AS prod_flattened

#COPY --from=prod / /



ENTRYPOINT [ "/srv/www/entrypoint.sh" ]
EXPOSE 80