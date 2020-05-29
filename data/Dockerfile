FROM python:3.7-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
		unzip \
        libfreetype6 \
	&& rm -rf /var/lib/apt/lists/*

RUN mkdir /utils

ADD https://github.com/protocolbuffers/protobuf/releases/download/v3.12.2/protoc-3.12.2-linux-x86_64.zip /utils/
RUN unzip /utils/protoc-3.12.2-linux-x86_64.zip -d /utils/protoc \
    && rm /utils/protoc-3.12.2-linux-x86_64.zip \
    && chmod +x /utils/protoc/bin/protoc

RUN mkdir -p /utils/fontbm/bin
ADD https://github.com/vladimirgamalyan/fontbm/releases/download/v0.2.4/fontbm /utils/fontbm/bin
RUN chmod +x /utils/fontbm/bin/fontbm

RUN pip install --no-cache-dir pipenv

WORKDIR /majsoul-plus-korean/data
RUN mkdir -p /majsoul-plus-korean/data
RUN cd /majsoul-plus-korean/data

COPY Pipfile* /majsoul-plus-korean/data/

RUN pipenv lock --requirements > requirements.txt
RUN pip install -r requirements.txt

CMD [ "python", "src/interface.py", "--protoc-path=/utils/protoc/bin/protoc", "--fontbm-path=/utils/fontbm/bin/fontbm"]