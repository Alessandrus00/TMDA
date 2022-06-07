FROM python:3.10

WORKDIR /usr/src/app/zips

COPY requirements.txt .

RUN apt-get update && apt-get -y install bash python3 python3-pip

RUN pip3 --no-cache-dir install -r requirements.txt

CMD [ "python3", "zip_extractor.py" ]