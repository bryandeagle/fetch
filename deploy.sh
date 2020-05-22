docker rm -f fetch
docker build -t deagle/fetch:stable .
docker run --init --name="fetch" --network="fetch-net" --restart always -d -p 5200:5000 deagle/fetch:stable
