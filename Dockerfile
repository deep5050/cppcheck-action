FROM facthunder/cppcheck

RUN sudo apt-get install -y git
ADD ./src/entrypoint.py /entrypoint.py
ENTRYPOINT ["python", "/entrypoint.py"]
