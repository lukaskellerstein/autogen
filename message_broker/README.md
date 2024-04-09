Build

`docker build --no-cache --tag autogen-broker:0.0.1 .`

Run

`docker run --name broker -d -p 4222:4222 -p 6222:6222 -p 8222:8222 -p 8089:8089 autogen-broker:0.0.1`
