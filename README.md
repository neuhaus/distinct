# distinct
So there's this twitter bot by a magazine you like but it posts stories over and over again? 
This twitter bot will retweet someone's tweet only if that person hasn't tweeted 
something with the same URL in the past. The name "distinct" was chosen for the SQL [SELECT DISTINCT](https://www.w3schools.com/Sql/sql_distinct.asp) statement.

Follow distinct bots instead of the original twitter accounts and enjoy duplicate-free tweets!

## Setup

1. Copy `distinct.init.example` to `distinct.ini`. This is the configuration file.

2. [Setup a twitter account](https://github.com/neuhaus/distinct/wiki/Setup-twitter-account) with API keys.

3. Run "sudo -H pip3 install tweepy" to install [tweepy](http://www.tweepy.org/) 3.6.0 (the currently recommended version). You also need the "requests" python module, install it as a pacakge (e.g. "apt install python-requests") or via "pip3 install requests"

4. Run `fill_cache.py` if you want to fill a URL cache with the URLs from past tweets.

5. Run `distinct.py`. It will keep running until its interrupted.

To run multiple instances of the bot, give an extra parameter to both scripts to specify a different configuration file.

## Example

The twitter account [@wired_distinct](https://twitter.com/wired_distinct) is running this software, deduplicating
tweets from the [@wired](https://twitter.com/wired) twitter account.

* * *

github icon image credit: Nick Royer "Space Marines: Into the Future" CC-by-SA 2.0 https://flic.kr/p/gVo63P

