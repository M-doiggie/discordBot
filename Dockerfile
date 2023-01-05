FROM ubuntu:latest
ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt update; apt-get update
RUN apt install -y tzdata

#install python stuff

RUN apt-get -y install python3.10; \
	apt-get -y install python3-pip; \
	apt -y install ffmpeg

RUN pip install discord.py; \
	pip install mcstatus; \
	pip install youtube_dl; \
	pip install python-dotenv; \ 
	pip install PyNaCl; \
	pip install spotipy; \
	pip install pytube

#enviroment
ENV SONG_CHECK_TIMER=1
ENV AUTO_LEAVE_TIMER=10
ENV mc_server_token = "gallafent.duckdns.org"
#ENV discord_token = "OTE3MDU3NDQ5MTk2OTQxNDc1.YazKTQ.vyTD_6i4qSjuhkOPvB4vMB08hsM"
ENV LOG_LEVEL "WARNING"
CMD mkdir /musicbot
WORKDIR /musicbot
COPY main.py Downloader.py MiscCommands.py MusicCommands.py TestTimeKeeperCommands.py TimeKeeperCommands.py Strings.py ./

CMD [ "python3", "main.py" ]