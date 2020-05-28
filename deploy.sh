declare -a minify=("fetch/static/index.html" 
                   "fetch/static/style.css"
                   "fetch/app/templates/results.html"
                   "fetch/app/templates/error.html"
                   "fetch/app/templates/empty.html")

for i in "${minify[@]}"
do
    html-minifier --collapse-whitespace --remove-optional-tags --remove-redundant-attributes --remove-script-type-attributes --use-short-doctype --minify-css true --minify-js true $i -o $i.min
    mv $i.min $i
done

docker rm -f fetch
docker rm -f stanford-ner

#docker build -t deagle/fetch:stable .
#docker pull lawinsider/stanford-ner-docker

#docker run --init --name="fetch" --network="fetch-net"  --env NER=stanford-ner --restart always -d -p 5200:5000 deagle/fetch:stable
docker-compose up