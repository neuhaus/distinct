#!/usr/bin/env python3

'''
    twitter deduplication bot.
    Copyright (C) 2016-2017 Sven Neuhaus

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
import urllib.parse
import random
import sys
import codecs


class StdOutListener(StreamListener):

    def on_data(self, data):
        tweet = json.loads(data)
        if tweet.get('text'):
            handle_tweet(tweet)
        return True

    def on_error(self, status):
        # tipp: 401 errors can be caused by a wrong system clock
        print("on_error: %s" % status)


user = None
api = None
default = None
session = None
seen_urls = None


def main():
    # sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    config = configparser.ConfigParser()
    if len(sys.argv) == 2:  # alternate config file
        config.read(sys.argv[1], encoding='utf8')
    else:
        config.read('distinct.ini', encoding='utf8')
    global default
    default = config['DEFAULT']
    listener = StdOutListener()
    auth = OAuthHandler(default['consumer_key'],
                        default['consumer_secret'])
    auth.set_access_token(default['access_token'],
                          default['access_token_secret'])
    global api
    api = tweepy.API(auth)
    stream = Stream(auth, listener)

    # print("follow_user = >%s<" % default['follow_user'])
    global user
    user = api.get_user(default['follow_user'])
    if not user:
        print("Unknown user %s" % default['follow_user'])
        exit(1)
    print("user '%s' id %d" % (default['follow_user'], user.id))
    global seen_urls
    seen_urls = shelve.open(
        filename='urlcache.' + default['follow_user'] + '.db',
        writeback=True)
    global session
    session = requests.Session()  # so connections are recycled
    while(True):
        try:
            stream.filter(follow=[user.id_str])
        except (ConnectionError, ConnectionResetError,
                AttributeError, UnicodeError, IndexError):
            print("error during stream.filter")
        except:   # keep running
            print("Unexpected error:", sys.exc_info()[0])
        time.sleep(5)
    # not reached
    print("stream is done")
    seen_urls.close()


def handle_tweet(tweet):
    global seen_urls
    global default
    # make sure it's not a retweet
    if tweet['user']['id_str'] != user.id_str:
        # print("ignoring retweet/response at %s" %
        #       tweet.get('created_at', 'unknown'))
        return
    print("%s tweet = %s " %
          (tweet.get('created_at', 'unknown'), tweet['text']))
    if not tweet['entities']['urls']:  # empty list
        api.retweet(tweet['id'])
        print("tweet without URL retweeted")
        return

    purge_old_urls()
    url = tweet['entities']['urls'][0]['url']
    shorturl = None
    if default.getboolean('unshorten_url'):
        shorturl = url
        try:
            url = unshorten_url(shorturl)
        except (UnicodeError, IndexError,
                ConnectionError, ConnectionResetError):
            print("error during unshorten url")
            shorturl = None
        except:   # keep running
            print("Unexpected error:", sys.exc_info()[0])
            shorturl = None
    cache = seen_urls.get(url)
    if not cache:
        # remember
        seen_urls[url] = int(time.time())
        print("new url %s" % url)
        if shorturl is not None:
            seen_urls[shorturl] = int(time.time())
            print("new short url %s" % shorturl)
        seen_urls.sync()
        # retweet
        api.retweet(tweet['id'])
        print("tweet with new URL")
    else:
        print("skipping tweet with old URL")


def purge_old_urls():
    # only every nth tweet, purge old URLs in the cache
    global default
    if random.random() >= (1 / int(default['url_purge_check'])):
        return
    time_now = int(time.time())
    delcount = 0
    global seen_urls
    for url in seen_urls.keys():
        if (time_now - seen_urls[url] > int(default['url_expiration'])):
            del seen_urls[url]
            delcount += 1
    print("deleted %d URLs from cache" % delcount)


def unshorten_url(shorturl):
    # unshortening URLs has privacy implications
    # ignoring the Google UTM stuff when matching
    try:
        session.cookies.clear()
        long_url   = session.head(shorturl, allow_redirects=True).url
        parsed_url = urllib.parse.urlparse(long_url)
        qs_dict    = urllib.parse.parse(qs_(parsed_url.query))
        if "utm_source" in qs_dict:
            del qs_dict["utm_source"]
        if "utm_medium" in qs_dict:
            del qs_dict["utm_medium"]
        if "utm_campaign" in qs_dict:
            del qs_dict["utm_campaign"]
        if "utm_term" in qs_dict:
            del qs_dict["utm_term"]
        if "utm_content" in qs_dict:
            del qs_dict["utm_content"]
        long_url = urllib.parse.urlunparse((parsed_url.scheme,
            parsed_url.netloc, parsed_url.path, parsed_url.params,
            urllib.parse.urlencode(a, True), parsed_url.fragment))

        return long_url
    except (ConnectionError, ConnectionResetError):
        return None
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return None

main()

# eof
