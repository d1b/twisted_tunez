#!/usr/bin/env python
import os
import mutagen

def get_song_info(path, as_dict=True):
	songs = []
	for dirpath, dirnames, filenames in os.walk(path):
		for filename in filenames:
			full_path = os.path.join(dirpath, filename)
			yy = mutagen.File(full_path, easy=True)
			if yy is not None:
				if as_dict:
					yy = dict(yy)
					yy.update({'location' : full_path} )
				songs.append(yy)
	return songs

def main():
	path = "/MUSIC/"
	print get_song_info(path)

if __name__=="__main__":
	main()
