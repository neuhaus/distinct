#!/usr/bin/env python3

'''
	fill cache of known urls from previous tweets for twitter deduplication bot
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
from tweepy import OAuthHandler
import tweepy
import shelve
import requests

user = None
api = None
session = None


def cache_tweet_urls(cache_filename):
	""" Stores URLs found in past tweets in the cache """
	seen_urls = shelve.open(filename=cache_filename, writeback=True)
	statuses = api.user_timeline(id=user.id_str, count=10, include_rts=False)
	for tweet in statuses:
		print("created at epoch %d" % int(tweet.created_at.timestamp()))
		if not tweet.entities.get("urls"):
			continue
		for urldata in tweet.entities['urls']:
			if seen_urls.get(urldata['expanded_url']):
				print("url already seen %s" % urldata['expanded_url'])
				continue
			seen_urls[urldata['expanded_url']] = int(tweet.created_at.timestamp())
			redirected_url = session.head(
				urldata['expanded_url'], allow_redirects=True).url
			if seen_urls.get(redirected_url):
				print("redirected_url already seen %s" % urldata['expanded_url'])
				continue
			seen_urls[redirected_url] = int(tweet.created_at.timestamp())
			print("expanded url %s and\nredirected url %s" %
				(urldata['expanded_url'], redirected_url))
	seen_urls.sync()
	seen_urls.close()


def main():
	config = configparser.ConfigParser()
	config.read('distinct.ini')
	default = config['DEFAULT']
	auth = OAuthHandler(default['consumer_key'], default['consumer_secret'])
	auth.set_access_token(default['access_token'], default['access_token_secret'])
	global api
	api = tweepy.API(auth)
	global user
	user = api.get_user(default['follow_user'])
	print("user " + default['follow_user'] + " id_str " + user.id_str)
	global session
	session = requests.Session()  # so connections are recycled
	cache_tweet_urls(default['url_cache'])


main()
