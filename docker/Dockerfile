FROM ubuntu:22.04

# Var for labels
ARG GITHUB_ACTOR
ARG GITHUB_REPOSITORY
ARG GITHUB_REF

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Paris

ENV PROJECT_NAME="Module_benevole"

LABEL org.opencontainers.image.title="${PROJECT_NAME}" \
      org.opencontainers.image.authors=${GITHUB_ACTOR} \
      org.opencontainers.image.vendor=${GITHUB_REPOSITORY} \
      org.opencontainers.image.source="https://github.com/${GITHUB_ACTOR}/web_mb" \
      org.opencontainers.image.url="https://github.com/${GITHUB_ACTOR}/web_mb/tags" \
      org.opencontainers.image.description="Module benevole" \
      org.opencontainers.image.os="Ubuntu" \
      org.opencontainers.image.version=${GITHUB_REF}

RUN apt-get update -yq \
&& apt-get install python3-pip -y

COPY controllers/ /opt/mb/controllers
COPY helpers/ /opt/mb/helpers
COPY pages/ /opt/mb/pages
COPY resources/ /opt/mb/resources
COPY styles/ /opt/mb/styles
COPY system/ /opt/mb/system
COPY Home.py /opt/mb/
COPY requirements.txt /opt/mb/

COPY start.sh .

RUN pip3 install --upgrade pip setuptools
RUN pip3 install -r /opt/mb/requirements.txt

RUN mkdir /opt/mb/conf && mkdir /opt/mb/.streamlit

VOLUME /opt/mb/conf
VOLUME /opt/mb/.streamlit

EXPOSE 8501

CMD ./start.sh
