FROM facthunder/cppcheck

RUN apt-get install -y git
ADD ./src/entrypoint.py /entrypoint.py
ENTRYPOINT ["python", "/entrypoint.py"]
