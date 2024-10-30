# distinct

So there's this magazine's Mastodon account that you like, but it rebogs stories over and over again? 
This Mastodon bot will reblog someone's toot only if that person hasn't tooted something with the same 
URL in the past. The name "distinct" was chosen for the SQL [SELECT DISTINCT](https://www.w3schools.com/Sql/sql_distinct.asp) statement.

Follow distinct bots instead of the original Mastodon accounts and enjoy duplicate-free toots!

## Setup

1. Copy `distinct.init.example` to `distinct.ini`. This is the configuration file.

2. [Setup a Mastodon account](SETUP.md) with API keys.

3. Run "sudo -H pip3 install Mastodon" to install [Mastodon.py]([http://www.tweepy.org/](https://pypi.org/project/Mastodon.py/)) 1.8.1 (the currently recommended version). This should also install the "requests" python module, if not install it as a package (e.g. "apt install python-requests") or via "pip3 install requests"

4. Run `fill_cache.py` if you want to fill a URL cache with the URLs from past toots.

5. Run `distinct.py`. It will keep running until its interrupted.

To run multiple instances of the bot, give an extra parameter to both scripts to specify a different configuration file.

## Example

The Mastodon account [@heise_distinct](https://botsin.space/heise_distinct) is running this software, deduplicating
toots from the [@heise]((https://mastodon.social/@heiseonline) Mastodon account.

The obsolete and unmaintained Twitter version is in the twitter branch for now.

* * *

github icon image credit: Nick Royer "Space Marines: Into the Future" CC-by-SA 2.0 https://flic.kr/p/gVo63P

