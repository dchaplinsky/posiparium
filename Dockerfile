FROM python:3.7.2-alpine3.8

ARG root=/app
ARG version

LABEL kind=app

WORKDIR ${root}

ENV VERSION=${version} \
		PYTHONPATH=${root} PREFIX=${root} \
		STATIC_ROOT=/static MEDIA_ROOT=/media \
		STATIC_ROOT_SOURCE=/static-source \
		APP_NAME="posiparium_site.wsgi:application" APP_WORKERS="2"

RUN [ "x${VERSION}" = "x" ] && echo -e '=== build-arg "version" is required for building an image ===' && exit 1 || exit 0

RUN /usr/sbin/adduser -D -h ${root} app

COPY ./requirements.txt ${root}/requirements.txt

RUN apk add --no-cache su-exec postgresql-libs libjpeg \
		&& apk add --no-cache --virtual .build-deps jpeg-dev zlib-dev postgresql-dev build-base \
		&& pip install -r  ${root}/requirements.txt \
		&& runDeps="$( \
			scanelf --needed --nobanner --format '%n#p' --recursive /usr/local \
				| tr ',' '\n' \
				| sort -u \
				| awk 'system("[ -e /usr/local/lib" $1 " ]") == 0 { next } { print "so:" $1 }' \
		)" \
			apk add --no-cache --virtual .app-rundeps $runDeps \
		&& apk del .build-deps

COPY docker-entrypoint.sh /usr/local/bin/

COPY ./posiparium_site/ ${root}/

RUN apk add --no-cache --virtual .build-deps nodejs npm \
		&& npm install -g sass uglify-js \
		&& python -m compileall ${root} \
		&& mkdir -p ${STATIC_ROOT} ${STATIC_ROOT_SOURCE} ${MEDIA_ROOT} \
		&& PATH=${PATH}:${root}/bin STATIC_ROOT=${STATIC_ROOT_SOURCE} python manage.py collectstatic \
		&& apk del .build-deps \
		&& rm -rf ${PREFIX}/bin ${PREFIX}/lib

ENTRYPOINT [ "docker-entrypoint.sh" ]

VOLUME [ "/static", "/media" ]

EXPOSE 8000

CMD [ "gunicorn" ]
