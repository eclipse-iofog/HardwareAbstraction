FROM frolvlad/alpine-python3

# for rpi
#FROM armhf/alpine

#RUN apk add --no-cache python3 && \
#    python3 -m ensurepip && \
#    rm -r /usr/lib/python*/ensurepip && \
#    pip3 install --upgrade pip setuptools && \
#    rm -r /root/.cache
RUN apk add --update util-linux pciutils lshw # basic linux utils for HWC
RUN apk add --update build-base python3-dev # lastest python dev utils
RUN pip install --upgrade pip
RUN pip install pyserial
RUN pip install autobahn
#RUN pip install RPi.GPIO # RaspberryPi GPIO module

COPY . /src/
RUN cd /src;

CMD ["python3", "/src/hal_main.py"]