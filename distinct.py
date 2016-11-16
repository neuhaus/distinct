#!/usr/bin/env python3

'''
	twitter deduplication bot.
	Copyright (C) 2016 Sven Neuhaus

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU Affero General Public License as published
	by the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

import configparser
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import json
import shelve
import re
import time
import requests
import random

class StdOutListener(StreamListener):

	def on_data(self, data):
		tweet = json.loads(data)
		if tweet.get('text'):
			handle_tweet(tweet)
		return True

	def on_error(self, status):
		print(status)


user = None
api = None
default = None
session = None
seen_urls = None

def main():
	config = configparser.ConfigParser()
	config.read('distinct.ini')
	global default
	default = config['DEFAULT']
	l = StdOutListener()
	auth = OAuthHandler(default['consumer_key'], default['consumer_secret'])
	auth.set_access_token(default['access_token'], default['access_token_secret'])
	global api
	api = tweepy.API(auth)
	stream = Stream(auth, l)

	global user
	user = api.get_user(default['follow_user'])
	if not user:
		print("Unknown user %s" % default['follow_user'])
		exit(1)
	print("user %s id %d" % ( default['follow_user'], user.id))
	global seen_urls
	seen_urls = default['url_cache']
	global session
	session = requests.Session()  # so connections are recycled
	stream.filter(follow=[user.id_str])


def handle_tweet(tweet):
	print("%s tweet = %s " % ( tweet.get('created_at', 'unknown'), tweet['text'] ))
	global seen_urls
	global default
	# make sure it's not a retweet
	if tweet['user']['id_str'] == user.id_str:
		#if tweet['entities']['urls'][0]['expanded_url']:
		urlmatch = re.search("(?P<url>https?://[^\s]+)", tweet['text'])
		if urlmatch:
			if default.getboolean('unshorten_url'):
				# unshortening URLs has privacy implications
				shorturl = urlmatch.group("url")
				#shorturl = tweet['entities']['urls'][0]['expanded_url']
				resp = session.head(shorturl, allow_redirects=True)
				url = resp.url
				print("short URL = %s URL = %s" % (shorturl, url))
			else:
				url = urlmatch.group("url")
			purge_old_urls()
			cache = seen_urls.get(url)
			if not cache:
				# remember
				seen_urls[url] = int(time.time())
				if default.getboolean('unshorten_url'):
					seen_urls[shorturl] = int(time.time())
				seen_urls.sync()
				# retweet
				#api.retweet(tweet['id'])
				print("tweet with new URL")
		else:
			print("tweet without URL")
			#api.retweet(tweet['id'])
	else:
		print("ignoring retweet/response")

def purge_old_urls():
	# only every nth tweet, purge old URLs in the cache
	global default
	if random.random() >= (1 / int(default['url_purge_check'])):
		return;
	time_now = int(time.time())
	delcount = 0
	global seen_urls
	for url in seen_urls.keys():
		if (time_now - seen_urls[url] > default['url_expiration']):
			del seen_urls[url]
			delcount += 1
	print("deleted %d URLs from cache" % delcount)

main()

# eof
