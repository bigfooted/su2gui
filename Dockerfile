FROM kitware/trame

COPY --chown=trame-user:trame-user . /deploy

RUN /opt/trame/entrypoint.sh build
