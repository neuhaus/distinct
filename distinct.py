#!/usr/bin/env python3

'''
    Mastodon deduplication bot.
    Copyright (C) 2024 Sven Neuhaus

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
import json
import shelve
import time
import requests
import random
import sys
from mastodon import Mastodon

class MastodonListener:

    def __init__(self, mastodon_instance, user_id):
        self.mastodon_instance = mastodon_instance
        self.user_id = user_id

    def on_toot(self, toot):
        if toot['account']['id'] != self.user_id:
            return
        handle_toot(toot)

user = None
api = None
seen_urls = None

def main():
    config = configparser.ConfigParser()
    if len(sys.argv) == 2:  # alternate config file
        config.read(sys.argv[1], encoding='utf8')
    else:
        config.read('distinct.ini', encoding='utf8')

    global api
    api = Mastodon(
        access_token=config['DEFAULT']['access_token'],
        api_base_url=config['DEFAULT']['api_base_url']
    )

    global user
    user = api.account_verify_credentials()
    print("user '%s' id %d" % (user['username'], user['id']))

    global seen_urls
    seen_urls = shelve.open(filename='urlcache.' + user['username'] + '.db', writeback=True)

    while True:
        try:
            # Fetch the user's timeline and check for new toots
            timeline = api.timeline_home()
            for toot in timeline:
                handle_toot(toot)
            time.sleep(60)  # Delay between checks
        except Exception as e:
            print("Unexpected error:", e)
            time.sleep(5)

    seen_urls.close()

def handle_toot(toot):
    global seen_urls
    # Check if it’s not a reblog
    if toot['account']['id'] != user['id']:
        return

    print("%s toot = %s " % (toot.get('created_at', 'unknown'), toot['content']))

    urls = toot['media_attachments'] if 'media_attachments' in toot else []
    if not urls:  # no URLs in the toot
        api.status_reblog(toot['id'])
        print("toot without URL reblogged")
        return

    purge_old_urls()
    url = urls[0]['url']
    cache = seen_urls.get(url)
    if not cache:
        # remember
        seen_urls[url] = int(time.time())
        print("new URL %s" % url)
        seen_urls.sync()
        # reblog
        api.status_reblog(toot['id'])
        print("toot with new URL reblogged")
    else:
        print("skipping toot with old URL")

def purge_old_urls():
    global default
    if random.random() >= (1 / int(default['url_purge_check'])):
        return
    time_now = int(time.time())
    delcount = 0
    global seen_urls
    for url in list(seen_urls.keys()):
        if (time_now - seen_urls[url] > int(default['url_expiration'])):
            del seen_urls[url]
            delcount += 1
    print("deleted %d URLs from cache" % delcount)

main()

# eof
