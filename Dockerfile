FROM r-base:3.4.2

ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8
RUN apt-get update && apt-get install -y \
		python3-pip

RUN apt-get install --no-install-recommends -y supervisor redis-server plink1.9 nginx

RUN Rscript -e 'source("https://bioconductor.org/biocLite.R"); biocLite("HIBAG")'

## Prevent cache invalidation of requirements.txt every time another file is updated.
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt


## Copy everything else
COPY . /app
COPY nginx.conf /etc/nginx/nginx.conf
RUN chown -R docker:docker /app
CMD ["/usr/bin/supervisord", "-c", "/app/supervisord.conf"]
