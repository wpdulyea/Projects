FROM ubuntu:focal

LABEL org.opencontainers.image.title="Python pytest, Tavern and Robot test environment"
LABEL org.opencontainers.image.description="Docker image running different python tests."
LABEL org.opencontainers.image.authors="William P Dulyea <wpdulyea@yahoo.com>"
LABEL org.opencontainers.image.source="https://github.com/wpdulyea/"

# Installing various packages python3 and setting it as the default python
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends wget build-essential && \
    apt-get install -y --no-install-recommends python3 python3-pip && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    apt-get autoremove -y && apt-get autoclean -y && rm -rf /var/lib/apt/lists/*

# pip install required packages
RUN pip freeze > requirements.txt && pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt
# This is the tests dir in the repo where all tests that are to run should be copied.
#COPY . tests
#WORKDIR /tests
RUN python3 -m pip --no-cache-dir install --upgrade pip && \
    python3 -m pip --no-cache-dir install pytest && \
    python3 -m pip --no-cache-dir install tavern && \
    python3 -m pip --no-cache-dir install robot
# Use "docker run -v $(pwd):/home ... to start in the appropriate dir to run tests
WORKDIR /home/
