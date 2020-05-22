docker rm -f fetch
docker build -t deagle/fetch:stable .
docker run --init --name="fetch" --network="fetch-net" -d -p 5000:5000 deagle/fetch:stable

