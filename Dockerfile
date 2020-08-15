FROM jfloff/alpine-python:latest
RUN apk upgrade
COPY fetch /app
WORKDIR /app
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["fetch.py"]
