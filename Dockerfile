FROM python:3
RUN apt-get update
RUN apt-get install -y build-essential libpcre3 libpcre3-dev wget

RUN wget -O /tmp/cppcheck-2.2.tar.gz https://github.com/danmar/cppcheck/archive/2.2.tar.gz
RUN cd /tmp/ && tar xvzf cppcheck-2.2.tar.gz

RUN cd /tmp/cppcheck-2.2 && make install SRCDIR=build CFGDIR=/cfg HAVE_RULES=yes


ADD ./src/entrypoint.py /entrypoint.py
ENTRYPOINT ["python", "/entrypoint.py"]
