FROM python:3.9.6
WORKDIR /flask
ADD . /flask/data_init
RUN apt update
#RUN apt install nano
RUN pip install --upgrade pip
RUN pip3 install -r ./data_init/requirements_data.txt
CMD bash -c "python data_init/data_init_tw_v0.py && python data_init/data_init_us_v0.py ; python data_init/update_data_daily_le.py"

