#!/usr/bin/env python
import os
import mimetypes
import string
import sys
import json
import tornado.ioloop
import tornado.web
from random import SystemRandom
import get_song_info

try:
	import music_settings
except ImportError:
	print return_red("Please create a music_settings.py file as stated in the readme!")
	sys.exit(1)

random = SystemRandom()

def return_red(input):
	return "\033[1;31m" + input  + "\033[m"

def get_random_string(length=10):
	choices = [x for x in (string.digits + string.letters) ]
	return ''.join([random.choice(choices) for x in range(0, length) ])

def append_song_id_to_songs(songs):
	count = 0
	for song in songs:
		song['_id'] = count
		count = count + 1

def get_song_from_songs(song_id, songs):
	song_id = int(song_id)
	if 0 <= song_id < len(songs):
		return [songs[song_id]]
	return None

class MainHandler(tornado.web.RequestHandler):
	def initialize(self, songs):
		self.songs = songs

	def set_default_headers(self):
		self.set_header("Server", "Unicorn powered!")

	def get(self):
		self.render("web/songs.html", songs=self.songs)

class SongApiHandler(MainHandler):
	def get(self, song_id=None):
		if len(self.songs) == 0:
			ret = {"error" : "NO SONGS"}
		if song_id is not None:
			""" as the song id is simply the number where the song
			    sits in the list, we can just access it directly! """
			ret = get_song_from_songs(song_id, self.songs)
			if ret is None:
				ret = {"error" : "Invalid song_id"}
		else:
			ret = self.songs
		self.set_header("Content-Type", "application/json")
		self.write(json.dumps(ret) )

class SongFileRetrievalHandler(MainHandler):
	def get(self, song_id):
		song = get_song_from_songs(song_id, self.songs)
		if song is None or len(song) == 0:
			self.write(json.dumps({"error" : "Invalid song_id"}) )
			return
		song = song[0]
		mime_type, encoding = mimetypes.guess_type(song['location'])
		if mime_type:
			self.set_header("Content-Type", mime_type)

		f = open(song['location'], 'rb' )
		data = f.read()
		self.write(data)
		f.close()

def main():
	songs = get_song_info.get_song_info(music_settings.MUSIC_PATH)
	append_song_id_to_songs(songs)

	settings = {
		"cookie_secret" : get_random_string(),
		"xsrf_cookies" : True,
		"login_url" : "/login/",
		"static_path" : os.path.join(os.path.dirname(__file__), "static" ),
	}
	application = tornado.web.Application([ \
		(r"/", MainHandler, {'songs' : songs}), \
		(r"/api/songs/(?P<song_id>[^\/]+)?/", SongApiHandler, {'songs' : songs}), \
		(r"/api/songs/", SongApiHandler, {'songs' : songs}), \
		(r"/api/files/songs/(?P<song_id>[^\/]+)?/", SongFileRetrievalHandler, {'songs' : songs}), \
		(r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path']))
	], **settings)
	application.listen(8000)
	tornado.ioloop.IOLoop.instance().start()

if __name__=="__main__":
	main()

