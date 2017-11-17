# distinct
This twitter bot will retweet someone's tweet only if that person hasn't tweeted 
something with the same URL in the past. The name "distinct" was chosen for the SQL [SELECT DISTINCT](https://www.w3schools.com/Sql/sql_distinct.asp) statement.

Follow distinct bots instead of the original twitter accounts and enjoy duplicate-free tweets!

## Setup

1. Copy `distinct.init.example` to `distinct.ini`. This is the configuration file.

2. [Setup a twitter account](https://github.com/neuhaus/distinct/wiki/Setup-twitter-account) with API keys

3. Run `fill_cache.py` if you want to fill a URL cache with the URLs from past tweets

4. Run `distinct.py`. It will keep running until its interrupted.

To run multiple instances of the bot, give an extra parameter to both scripts to specify a different configuration file.

* * *

github icon image credit: Nick Royer CC-by-SA 2.0 https://flic.kr/p/gVo63P

