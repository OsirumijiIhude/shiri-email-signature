FROM python:3.12-slim-bookworm AS build
RUN apt-get update \
 && apt-get install -y --no-install-recommends chromium fonts-liberation ca-certificates \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir playwright==1.55.0 Pillow==12.3.0
WORKDIR /app
COPY . /app
RUN python3 redesign/motion_v5.py --assets-source /app/index.html --output-dir /out
RUN python3 redesign/test_browser.py /out --chromium /usr/bin/chromium \
 && python3 redesign/test_motion_v5.py /out --chromium /usr/bin/chromium

FROM nginx:alpine
COPY --from=build /out/ /usr/share/nginx/html/
COPY default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
