FROM python:3.12

RUN curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash

RUN apt-get update && apt-get install -y speedtest

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /.

RUN mkdir -p ~/.config/ookla

RUN cp ./static/speedtest-cli.json ~/.config/ookla/

ENTRYPOINT ["/entrypoint.sh"]


