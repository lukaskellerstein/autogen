FROM nats:alpine

EXPOSE 4222
EXPOSE 6222
EXPOSE 8222
EXPOSE 8089

COPY ./nats.conf /server.conf

# RUN pwd
# RUN ls -l

CMD ["nats-server", "--config", "/server.conf"]
