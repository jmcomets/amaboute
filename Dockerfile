FROM python:3
WORKDIR /usr/src
ADD . /usr/src
RUN ["python", "setup.py", "install"]
ENTRYPOINT ["amaboute"]
