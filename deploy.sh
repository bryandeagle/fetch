docker rm -f fetch
docker build -q -t deagle/fetch:stable .
docker run --init --name="fetch" --network="fetch-net"  --ip 172.18.0.2 --env NER=stanford-ner --env IP=172.18.0.2 --restart always -d -p 127.0.0.1:5200:5000 deagle/fetch:stable
