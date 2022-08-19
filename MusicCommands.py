import json
import os
import re
import urllib
from queue import Queue
from urllib import parse
import logging

import discord
import spotipy
from discord.ext import commands, tasks
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import Playlist, Stream
import threading

# Spotify Variables
from Downloader import Downloader

client_id = "384291e4cdab4faea3f4517b61a89eb5"
client_secret = "0457b50cefe449998af10aa8707be247"
redirect_uri = 'http://127.0.0.1:9090'
scope = "user-top-read"
sp = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

currentSong = None
toDownloadList = Queue(maxsize=0)
toPlayList = Queue(maxsize=0)
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "WARNING"))
LOGGER = logging.getLogger(__name__)

SONG_TIMER = float(os.getenv("SONG_CHECK_TIMER", 3))
AUTO_LEAVE_TIMER = float(os.getenv("AUTO_LEAVE_TIMER", 10))


class MusicCommands(commands.Cog):

    # Gets the bot to join the same voice channel as the author of the message
    @commands.command(name='join', help='Tells the bot to join the voice channel')
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
            return
        else:
            channel = ctx.message.author.voice.channel
        try:
            await channel.connect()
            if not self.check_downloads.is_running():
                self.check_music.start(ctx)
            if not self.check_downloads.is_running():
                self.check_downloads.start(ctx)
            if not self.auto_leave.is_running():
                self.auto_leave.start(ctx)
            LOGGER.warning("Successfully joined: '{0}'".format(channel))
        except Exception as e:
            await ctx.send("Bot unable to connect to " + str(channel))
            LOGGER.error("Trying to join Channel: '{0}' caused the following exception: '{1}'".format(channel, e))

    # Gets the bot to leave the voice channel that it is currently in.
    @commands.command(name='leave', help='To make the bot leave the voice channel', aliases=['stop'])
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
            toDownloadList.empty()

    # Adds a song to the download list
    # Accepts youtube urls, song names, spotify platlist/album urls.
    @commands.command(name='play', help='To play song', aliases=['p', 'play_song'])
    async def add_to_queue(self, ctx, *, url):
        voice_client = ctx.message.guild.voice_client
        if voice_client is None:
            await self.join(ctx)
        if "spotify" in url:
            await self.parseSpotify(url)
        elif "youtube" in url and "playlist" in url:
            th = threading.Thread(target=self.parseYoutubePlaylists, args=(url,))
            th.start()
        else:
            toDownloadList.put(url)
        LOGGER.warning("Current size of Download List: '{0}'".format(toDownloadList.qsize()))

    def parseSpotify(self, url):
        LOGGER.warning("Spotify Url being deciphered.")
        if "album" in url:
            album_response = sp.album_tracks(url, limit=50, market=None)
            results = album_response["items"]
            for result in results:
                toDownloadList.put(result['name'] + " by " + result['artists'][0]['name'])
        if "playlist" in url:
            response = sp.playlist_tracks(url, fields=None, limit=100, market=None)
            results = response["items"]
            for result in results:
                toDownloadList.put(result['track']['name'] + " by " + result['track']['artists'][0]['name'])
        if "track" in url:
            track_response = sp.track(url, market=None)
            toDownloadList.put(track_response['name'] + " by " + track_response['artists'][0]['name'])

    def parseYoutubePlaylists(self, url):
        playlist = Playlist(url)
        playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")

        for url in playlist.video_urls:
            print(url)

        for video in playlist.videos:
            audioStream = video.streams.get_by_itag(140)
            toDownloadList.put(audioStream)


    # Skips the current song, will throw a little error
    @commands.command(name='skip', help='Skips the current song')
    async def skip(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client
        if toPlayList.qsize() == 0:
            filename = None
            voice_channel.stop()
            return
        else:
            filename = toPlayList.get()
            try:
                if os.path.exists(filename):
                    voice_channel.stop()
                    voice_channel.play(discord.FFmpegPCMAudio(source=filename), after=lambda e: self.deleteSong(filename))
                    return
            except Exception as e:
                LOGGER.error("An Exception was caught trying to play a song: '{0}'".format(e))

    # Tells the user the current song playing.
    @commands.command(name='song', help='Get the name of the current song')
    async def get_song(self, ctx):
        global currentSong
        if currentSong is not None:
            await ctx.send("Currently playing: " + currentSong)
        else:
            await ctx.send("No Song currently playing")

    # Tells the user the list of songs queued up to play.
    @commands.command(name='queue', help='Prints the current queued songs.')
    async def get_queue(self, ctx):
        global currentSong
        totalSongsList = [currentSong]
        if toPlayList.qsize() != 0:
            toPlay = list(toPlayList.queue)
            totalSongsList += toPlay
        if toDownloadList.qsize() != 0:
            toDownload = list(toDownloadList.queue)
            totalSongsList += toDownload
        embedMessage = discord.Embed(title="Queue of Songs")
        counter = 0

        for item in totalSongsList:
            # Try to get the video id
            skip = False
            try:
                url_data = parse.urlparse(item)
                query = parse.parse_qs(url_data.query)
                videoId = query["v"][0]
            except:
                try:
                    pattern = r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})'
                    videoId = re.findall(pattern, item)[0]
                except:
                    skip = True

            if not skip:
                # Tries to get the title of the video
                params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % videoId}
                url = "https://www.youtube.com/oembed"
                query_string = urllib.parse.urlencode(params)
                url = url + "?" + query_string
                LOGGER.info("Adding VideoID: {0} to the display queue".format(videoId))

                with urllib.request.urlopen(url) as response:
                    response_text = response.read()
                    data = json.loads(response_text.decode())

                # Put it into the embedded message
                embedMessage.add_field(name=counter, value=data['title'], inline=False)
            else:
                embedMessage.add_field(name=counter, value=str(item), inline=False)
            counter += 1

        await ctx.send(embed=embedMessage)

    # Checks if there are any songs in the toPlayQueue, then plays them if no song is currently playing
    # Called after Play is called.
    @add_to_queue.after_invoke
    async def check_playing(self, ctx):
        global currentSong
        voice_client = ctx.message.guild.voice_client
        try:
            server = ctx.message.guild
            voice_channel = server.voice_client
            if not voice_client.is_playing() and toPlayList.qsize() > 0:
                filename = toPlayList.get(0)
                if not os.path.exists(filename):
                    LOGGER.error("The song: {0} does not exist locally.".format(filename))
                    return None
                currentSong = filename
                voice_channel.play(discord.FFmpegPCMAudio(source=filename), after=lambda e: self.deleteSong(filename))
                LOGGER.warning("Playing Song: {0}".format(filename))
                await ctx.send('**Now playing:** {}'.format(filename))
        except Exception as e:
            LOGGER.error("An Exception occurred when trying to play music, Exception: {0}".format(e))

    # A method which is called every 3 seconds. To check if a song needs to be played from the toPlayQueue
    @tasks.loop(seconds=SONG_TIMER)
    async def check_music(self, ctx):
        if ctx is not None:
            voice_client = ctx.message.guild.voice_client
            if voice_client is not None and voice_client.is_connected():
                if not voice_client.is_playing():
                    await self.check_playing(ctx)

    # A method which is called every 3 seconds, to check if a song needs to be downloaded
    @tasks.loop(seconds=SONG_TIMER)
    async def check_downloads(self, ctx):
        if not toDownloadList.empty():
            url = toDownloadList.get()
            LOGGER.warning("Trying to download url: {0}".format(url))
            if isinstance(url, Stream):
                filename = url.download(output_path='C:\Productive\Projects\Python\discordBot\\').split("\\")[-1]
                toPlayList.put(filename)
                return
            else:
                filename = await Downloader.download_music(None, url)
                if filename is None:
                    if ctx is not None:
                        failedDownloadEmbed = discord.Embed(title="Failed Song")
                        LOGGER.error("Url of failed song: {0}".format(url))
                        if 'http' in url or 'https' in url:
                            failedDownloadEmbed.url = url
                        else:
                            failedDownloadEmbed.add_field(name="File: ", value=url)
                        failedDownloadEmbed.description = "Failed to download due to Youtube"
                        await ctx.send(embed=failedDownloadEmbed)
                    LOGGER.error("File was not able to be downloaded: {0}".format(url))
                    await self.check_downloads(ctx)
                else:
                    toPlayList.put(filename)
                    LOGGER.warning("File: {0} was downloaded".format(filename))

    @tasks.loop(seconds=10)
    async def auto_leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client is not None and len(voice_client.channel.members) == 1 and voice_client.is_connected:
            await voice_client.disconnect()
            LOGGER.warning("Bot left voice call due to being alone")

    # Deletes song files
    @staticmethod
    def deleteSong(filename):
        try:
            os.remove(filename)
            LOGGER.warning("A Song was deleted: {0}".format(filename))
        except OSError as OSE:
            pass
