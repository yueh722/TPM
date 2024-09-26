FROM python:3.9.6
WORKDIR /flask
ADD . /flask
#RUN apt update
#RUN apt install nano
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 8000
