FROM python:3.12-alpine
WORKDIR /app
COPY . /app
RUN python3 design/polish.py --file /app/index.html
EXPOSE 80
CMD ["python3","-m","http.server","80","--directory","/app"]
