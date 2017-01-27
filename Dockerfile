FROM python:3.6-slim
MAINTAINER https://github.com/grahame/

ENV VIRTUAL_ENV /env
ENV PYTHON_PIP_VERSION 8.1.2

# create a virtual env in $VIRTUAL_ENV and ensure it respects pip version
RUN pyvenv $VIRTUAL_ENV \
    && $VIRTUAL_ENV/bin/pip install --upgrade --no-cache-dir pip==$PYTHON_PIP_VERSION

ENV PATH $VIRTUAL_ENV/bin:$PATH

RUN addgroup --gid 1000 wrfy \
    && adduser --disabled-password --home /app --no-create-home --system -q --uid 1000 --ingroup wrfy wrfy \
    && mkdir /app \
    && chown wrfy:wrfy /app

COPY . /app

WORKDIR /app
RUN pip install -e .

ENTRYPOINT ["wrfy"]
CMD ["-h"]
