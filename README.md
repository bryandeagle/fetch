Fetch
=====
Flask App to Scrape Contact Information from Given Website

## Installing
```
python -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Testing
```
python -m pytest tests/
```

## Deploying

### Build & Run Flask Docker Container
```
docker rm -f fetch
docker build -t deagle/fetch:stable .
docker run --init --name="fetch" --network="fetch-net" --env NER=stanford-ner --restart always -d -p 5200:5000 deagle/fetch:stable
```

### Pull & Run Stanford NER Docker Container
```
docker rm -f stanford-ner
docker pull lawinsider/stanford-ner-docker
docker run --init -d -p 5201:80 --name="stanford-ner" --restart always --network="fetch-net" lawinsider/stanford-ner-docker
```

### Private Reverse Proxy
```
<VirtualHost *:80>
	ServerName fetch.home

	# Proxy others normally
	ProxyPass / http://localhost:5200/
	ProxyPassReverse / http://localhost:5200/

	# Create site-specific logs
	ErrorLog ${APACHE_LOG_DIR}/fetch-error.log
	CustomLog ${APACHE_LOG_DIR}/fetch-access.log combined
</VirtualHost>
```

### Public Reverse Proxy
> TBD