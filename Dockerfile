FROM facthunder/cppcheck
RUN apt-get install git -y
ADD ./src/entrypoint.py /entrypoint.py
ENTRYPOINT ["python", "/entrypoint.py"]
