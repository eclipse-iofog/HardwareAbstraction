FROM frolvlad/alpine-python3

# for rpi
#FROM armhf/alpine

#RUN apk add --no-cache python && \
#    python -m ensurepip && \
#    rm -r /usr/lib/python*/ensurepip && \
#    pip install --upgrade pip setuptools && \
#    rm -r /root/.cache
RUN apk add --update util-linux pciutils lshw
RUN pip install --upgrade pip
RUN pip install pyserial
#RUN pip install asyncio
RUN pip install autobahn

COPY . /src/
RUN cd /src;

CMD ["python3", "/src/hal_main.py"]