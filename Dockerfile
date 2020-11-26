FROM facthunder/cppcheck

RUN rm /var/lib/apt/lists/* -vf
RUN apt-get clean
RUN mkdir -p /var/lib/apt/lists/partial
RUN apt-get update

RUN apt-get install -y git --no-install-recommends

ADD ./src/entrypoint.py /entrypoint.py
ENTRYPOINT ["python", "/entrypoint.py"]
