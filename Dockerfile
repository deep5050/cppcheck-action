FROM neszt/cppcheck-docker

ADD ./src/entrypoint.py /entrypoint.py
ENTRYPOINT ["python", "/entrypoint.py"]
