FROM nginx:latest as development_build

RUN rm /etc/nginx/conf.d/default.conf
COPY ./nginx/conf.d/nginx.conf /etc/nginx/conf.d