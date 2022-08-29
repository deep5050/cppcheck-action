FROM neszt/cppcheck-docker:2.9
RUN apk add --no-cache python3
ADD ./src/entrypoint.py /entrypoint.py
ENTRYPOINT ["python3", "/entrypoint.py"]
