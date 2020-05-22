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

### Apache Reverse Proxy
```
<VirtualHost *:80>
        ServerName fetch.home

        # Proxy requests
        ProxyPass / http://localhost:5200/
        ProxyPassReverse / http://localhost:5200/

        # Custom log locations
        ErrorLog ${APACHE_LOG_DIR}/fetch-error.log
        CustomLog ${APACHE_LOG_DIR}/fetch-access.log combined
</VirtualHost>

<VirtualHost *:80>
        ServerName fetch.dea.gl

        # Rewrite HTTP to HTTPS
        RewriteEngine on
        RewriteCond %{SERVER_NAME} ^fetch.dea.gl$
        RewriteRule ^ https://fetch.dea.gl%{REQUEST_UTI} [L,NE,R=302]

        # Custom log locations
        ErrorLog ${APACHE_LOG_DIR}/fetch-error.log
        CustomLog ${APACHE_LOG_DIR}/fetch-access.log combined
</VirtualHost>

<VirtualHost *:443>
        ServerName fetch.dea.gl

        # Proxy requests
        ProxyPass / http://localhost:5200
        ProxyPassReverse / http://localhost:5200

        # Custom log locations
        ErrorLog ${APACHE_LOG_DIR}/fetch-error.log
        CustomLog ${APACHE_LOG_DIR}/fetch-access.log combined
</VirtualHost>
```