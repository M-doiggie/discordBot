FROM ubuntu:latest
ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt update
RUN apt install -y tzdata
RUN apt-get -y install python3.8
RUN apt-get -y install python3-pip
RUN apt -y install ffmpeg
RUN pip3 install discord.py 
RUN pip3 install mcstatus 
RUN pip3 install requests
RUN pip3 install animals.py
RUN pip3 install youtube_dl
RUN pip3 install python-dotenv 
RUN pip3 install PyNaCl
RUN pip3 install bs4
ENV SONG_CHECK_TIMER=1
ENV AUTO_LEAVE_TIMER=10
ENV LOG_LEVEL = "WARNING"
CMD [ "python3", "/main.py" ]