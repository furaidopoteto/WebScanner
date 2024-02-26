FROM php:7.2-apache
RUN apt-get update
RUN apt-get install -y vim wget zip graphviz gcc
RUN docker-php-ext-install pdo_mysql
# Chromeに必要なドライバーのインストール
RUN apt-get install -y libvulkan1
# Chromeが文字化けしないように日本語フォントをインストール
RUN apt-get install -y fonts-ipaexfont-gothic fonts-ipaexfont-mincho

RUN apt-get install -y python3 python3-pip default-libmysqlclient-dev python3-selenium libxml2-dev libxslt-dev
RUN apt-get install python3-dev
# Chromeのダウンロード
COPY ./google-chrome-stable_current_amd64.deb /tmp/
RUN dpkg -i /tmp/google-chrome-stable_current_amd64.deb
COPY ./chromedriver_linux64.zip /tmp/
RUN unzip -o /tmp/chromedriver_linux64.zip -d ~/bin/

# Pythonの各種ライブラリのインストール
RUN python3 -m pip install -U pip
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# Apacheのポート番号を80から8080にする
COPY ./ports.conf /etc/apache2/ports.conf