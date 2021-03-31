docker rm -f fetch
docker build -q -t deagle/fetch:stable .
docker run -d \
    --init
    --name fetch \
    --network fetch-net \
    --ip 172.18.0.2 \
    --env NER=stanford-ner \
    --env IP=172.18.0.2 \
    --restart always \
    --publish 127.0.0.1:5200:5000 \
    deagle/fetch:stable

docker rm -f stanford-ner
docker pull -q lawinsider/stanford-ner-docker
docker run -d \
    --init \
    --publish 127.0.0.1:5201:80 \
    --name stanford-ner \
    --restart always \
    --network fetch-net \
    lawinsider/stanford-ner-docker
