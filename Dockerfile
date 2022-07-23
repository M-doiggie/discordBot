FROM ubuntu:latest
ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt update
RUN apt install -y tzdata
RUN apt-get update

#install python stuff
RUN apt-get -y install python3.9
RUN apt-get -y install python3-pip
RUN apt -y install ffmpeg
RUN pip install discord.py 
RUN pip install mcstatus
RUN pip install youtube_dl
RUN pip install python-dotenv 
RUN pip install PyNaCl

RUN pip install spotipy

RUN pip install async-timeout==3.0.1
#enviroment
ENV SONG_CHECK_TIMER=1
ENV AUTO_LEAVE_TIMER=10
ENV mc_server_token = "gallafent.duckdns.org"
#ENV discord_token = "OTE3MDU3NDQ5MTk2OTQxNDc1.YazKTQ.vyTD_6i4qSjuhkOPvB4vMB08hsM"
ENV LOG_LEVEL "WARNING"
CMD mkdir /musicbot
WORKDIR /musicbot
COPY main.py ./
COPY Downloader.py ./
COPY MiscCommands.py ./
COPY MusicCommands.py ./
COPY TestTimeKeeperCommands.py ./
COPY TimeKeeperCommands.py ./
CMD [ "python3", "main.py" ]
