FROM python:3
RUN apt-get update
RUN apt-get -y install cppcheck=1.88-1

ADD ./src/entrypoint.py /entrypoint.py
ENTRYPOINT ["python", "/entrypoint.py"]
