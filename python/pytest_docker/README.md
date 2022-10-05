# Docker python test framework(s) environment.

![Project page](https://github.com/wpdulyea)

Nice idea to remove the need to one collosal set of environemental dependencies
and or libraries installed on your Linux platform. Instead remove those dependencies
and build them into Docker with the assumption that tests exists locally. You 
then need only cd to the appropriate directory and run the docker image with -v
to run your pytest or Tavern tests or Robot framework tests.
 
Also includes a Docker image ready to be used with

## How to use this Docker image to run tests for your project

You can run this Docker image to test your project with:

```bash
$ docker run -v $(pwd):/home --rm <image_location:tag_name) bash
```

Where:
- `-v $(pwd):/home` flag mounts your PC current working directory as a volume
  inside the docker container `/home` path, which is also the container default
  working directory
- `--rm` flag will clean up the container created

### Example: pytest

To run pytests

```bash
# Clone the repository
$ git clone https://github.com/lancaster-university/microbit-samples
$ cd microbit-samples
# Run pytest using this docker image
$ docker run -v $(pwd):/home it --rm pytest-tools:latest -- bash
# cd to the location of the tests to run and exec
$ pytest ...
```

### Example: Tavern

an example run of tavern

### Example: Robot Framework


## Other General Docker Instructions

### Build docker image

Build the docker image:

```bash
$ docker build -t "python-test-tools" .
```

### Run a bash session

Run a bash session (launches a new container) from an existing docker image:

```
docker run --name python-test-tools -it python-test-tools:latest -- bash
```

### Copy files from docker to host

```
docker cp python-test-tools:/home/tests/results .
```
