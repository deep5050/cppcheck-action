FROM neszt/cppcheck-docker
RUN apt-get update
RUN apt-get install -y python wget


ADD ./src/entrypoint.py /entrypoint.py
ENTRYPOINT ["python", "/entrypoint.py"]
