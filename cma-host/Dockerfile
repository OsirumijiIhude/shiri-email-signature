FROM python:3.12-alpine AS build
WORKDIR /app
COPY . /app
RUN python3 design/polish.py --file /app/index.html

FROM nginx:alpine
COPY --from=build /app/index.html /usr/share/nginx/html/index.html
COPY default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
