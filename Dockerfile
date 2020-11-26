FROM facthunder/cppcheck

RUN apt-get update -y
RUN apt-get install -y git --no-install-recommends

ADD ./src/entrypoint.py /entrypoint.py
ENTRYPOINT ["python", "/entrypoint.py"]
