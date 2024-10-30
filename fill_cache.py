#!/usr/bin/env python3

'''
    fill cache of known urls from previous toots for Mastodon deduplication bot
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
import shelve
import requests
import sys
import datetime
from mastodon import Mastodon

session = None
api = None
user = None

def cache_toot_urls(cache_filename, tootcount):
    toots = 0
    toot_duplicate_url = 0
    toot_nourl = 0
    """ Stores URLs found in past toots in the cache """
    seen_urls = shelve.open(filename=cache_filename, writeback=True)
    statuses = api.timeline_user(user.id, limit=tootcount)  # Fetch user timeline

    for toot in statuses:
        print("\n\ntoot = %s" % toot)
        toots += 1
        print("created at %s" % toot['created_at'])
        
        if not toot.get('media_attachments'):
            toot_nourl += 1
            continue
        
        for media in toot['media_attachments']:
            if media['type'] == 'image' and 'url' in media:
                url = media['url']
                
                if seen_urls.get(url):
                    print("URL already seen %s" % url)
                    toot_duplicate_url += 1
                    continue
                
                seen_urls[url] = int(toot['created_at'].timestamp())
                redirected_url = session.head(url, allow_redirects=True).url
                
                if seen_urls.get(redirected_url):
                    print("Redirected URL already seen %s" % url)
                    toot_duplicate_url += 1
                    continue
                
                seen_urls[redirected_url] = int(toot['created_at'].timestamp())
                print("Expanded URL %s and redirected URL %s" % (url, redirected_url))
    
    seen_urls.sync()
    seen_urls.close()
    print("%d toots, %d duplicate URLs, %d without URL" % (toots, toot_duplicate_url, toot_nourl))


def main():
    config = configparser.ConfigParser()
    if len(sys.argv) == 2:  # Alternate config file
        config.read(sys.argv[1], encoding='utf8')
    else:
        config.read('distinct.ini', encoding='utf8')
    
    default = config['DEFAULT']
    global api
    api = Mastodon(
        access_token=default['access_token'],
        api_base_url=default['api_base_url']
    )
    
    global user
    user = api.account_verify_credentials()
    print("User '%s' id %d" % (user['username'], user['id']))
    
    global session
    session = requests.Session()  # Recycle connections
    
    cache_toot_urls("urlcache.{}.db".format(user['username']), 1500)

main()
