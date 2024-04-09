# Use the official MongoDB image

FROM mongo:latest

# Set the MongoDB environment variables

# This is where you can set the MongoDB root username and password
ENV MONGO_INITDB_ROOT_USERNAME=admin
ENV MONGO_INITDB_ROOT_PASSWORD=password

# Optionally, you can set a custom database name and user
# ENV MONGO_INITDB_DATABASE=mydatabase
# ENV MONGO_USERNAME=myuser
# ENV MONGO_PASSWORD=mypassword

# Copy any initialization scripts if you have them
# This is useful for setting up initial data or schemas
COPY ./init-db.d/ /docker-entrypoint-initdb.d/

# Expose the default MongoDB port
EXPOSE 27017

# The CMD instruction is already defined in the base image
# It starts MongoDB with the default settings or those modified by ENV variables
