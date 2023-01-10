FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3-pip  tesseract-ocr 

COPY ./requirements.txt .
RUN  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple 
