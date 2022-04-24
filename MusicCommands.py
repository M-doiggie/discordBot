import asyncio
import json
import os
import re
import urllib
from queue import Queue
from urllib import parse

import discord
import spotipy
import youtube_dl
from discord.ext import commands, tasks
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify Variables
client_id = "384291e4cdab4faea3f4517b61a89eb5"
client_secret = "0457b50cefe449998af10aa8707be247"
redirect_uri = 'http://127.0.0.1:9090'
scope = "user-top-read"
sp = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

toDownloadList = Queue(maxsize=0)
toPlayList = Queue(maxsize=0)


class MusicCommands(commands.Cog):
    # Local Music Variables
    currentSong = None

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
            self.check_music.start(ctx)
            self.check_downloads.start(ctx)
            print("Successfully joined: ", channel, flush=True)
        except Exception as e:
            await ctx.send("Bot unable to connect to " + str(channel))
            print("Channel: " + str(channel) + " Self: " + str(self), flush=True)
            print(e, flush=True)

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
            print(url, flush=True)
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
        else:
            toDownloadList.put(url)
        print("Current size of download list: ", toDownloadList.qsize(), flush=True)

    # Skips the current song, will throw a little error
    @commands.command(name='skip', help='Skips the current song')
    async def skip(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client
        filename = toPlayList.get(0)
        try:
            if not os.path.exists(filename):
                voice_channel.stop()
                voice_channel.play(discord.FFmpegPCMAudio(source=filename), after=lambda e: self.deleteSong(filename))
                await ctx.send("Not yet implemented.")
                return
        except Exception as ex:
            print("Deleted Exception caught", flush=True)

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
                print(videoId, flush=True)
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

                print("VideoID: ", videoId, flush=True)
                print("URL: ", url, flush=True)

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
        # disabled due to filling up logs
        # print("Checking if to play a song", flush=True)
        try:
            server = ctx.message.guild
            voice_channel = server.voice_client
            # disabled due to filling up logs
            # print("Check if playing: " + str(voice_client.is_playing()) + " is toplayingList size: " + str(toPlayList.qsize()), flush=True)
            if not voice_client.is_playing() and toPlayList.qsize() > 0:
                filename = toPlayList.get(0)
                if not os.path.exists(filename):
                    return print("checking_playing: File does not exist")
                currentSong = filename
                voice_channel.play(discord.FFmpegPCMAudio(source=filename), after=lambda e: self.deleteSong(filename))
                print("Playing song: ", filename, flush=True)
                await ctx.send('**Now playing:** {}'.format(filename))
        except Exception as ex:
            print(ex, flush=True)
        except:
            await ctx.send("The bot is not connected to a voice channel.")

    # A method which is called every 3 seconds. To check if a song needs to be played from the toPlayQueue
    @tasks.loop(seconds=3)
    async def check_music(self, ctx):
        if ctx is not None:
            voice_client = ctx.message.guild.voice_client
            if voice_client.is_connected():
                if not voice_client.is_playing():
                    await self.check_playing(ctx)

    # A method which is called every 3 seconds, to check if a song needs to be downloaded
    @tasks.loop(seconds=3)
    async def check_downloads(self, ctx):
        if not toDownloadList.empty():
            url = toDownloadList.get()
            print("Trying to download url: " + url, flush=True)
            if not await Downloader.download_music(url):
                if ctx is not None:
                    failedDownloadEmbed = discord.Embed(title="Failed Song")
                    failedDownloadEmbed.url = url
                    failedDownloadEmbed.description = "Failed to download due to Youtube"
                    await ctx.send(embed=failedDownloadEmbed)
                print("File not able to be downloaded: " + url, flush=True)
                self.check_downloads(ctx)
            else:
                print("File downloaded: " + url, flush=True)
        else:
            pass
        # disabled as this fills the logs
        # print("No file to download", flush=True)

    # Deletes song files
    @staticmethod
    def deleteSong(filename):
        print("Trying to delete song: " + str(filename), flush=True)
        try:
            os.remove(filename)
        except OSError as OSE:
            print("File deleted: ", filename, flush=True)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename


# Used to download music. Url not required, just a String of a song name.
class Downloader:
    async def download_music(url):
        try:
            filename = await YTDLSource.from_url(url)
            toPlayList.put(filename)
            return True
        except:
            return False
