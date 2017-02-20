# YTCrawl Manual-Fork README

This sub directory was cloned from: https://github.com/yuhonglin/YTCrawl

You should see the file OLD-README.md for details.

`ytids.txt` was the original source file used to crawl YouTube.

A Python REPL session was used to batch_crawl YouTube: the old README.md file
for details on using batch_crawl. The original output directory was compressed into ytcrawl.tar.gz in our
parent directory.

The session used to `batch_crawl` looked something like:

```
cnkelly@PSYCIISPROGWS:~/george/ted/ytscrape/YTCrawl$ python2
Python 2.7.12 (default, Nov 19 2016, 06:48:10)
[GCC 5.4.0 20160609] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from crawler import Crawler
>>> c = Crawler()
>>> c._crawl_delay_time = 1
>>> c._cookie_update_delay_time = 1
>>> c.batch_crawl('./ytids.txt', './output')
>>> quit()
```
