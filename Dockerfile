FROM r-base:3.4.2

ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8
RUN apt-get update && apt-get install -y \
		python3-pip

RUN Rscript -e 'source("https://bioconductor.org/biocLite.R"); biocLite("HIBAG")'

## Prevent cache invalidation of requirements.txt every time another file is updated.
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip3 install -r requirements.txt


## Copy everything else
COPY . /app


ENTRYPOINT ["python3"]
CMD ["webapp.py"]
