#! usr/bin/python3

from bs4 import BeautifulSoup
import time
from csv import DictWriter
import pprint
import datetime
import math
import traceback
import sys
from datetime import date, datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

reload(sys)
sys.setdefaultencoding('utf8')

total_tweets = 0
total_followers = 0
total_followings = 0
total_favorites = 0
total_lists = 0


def init_driver(driver_type):
    if driver_type == 1:
        driver = webdriver.Firefox()
    elif driver_type == 2:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=chrome_options)
    elif driver_type == 3:
        driver = webdriver.Ie()
    elif driver_type == 4:
        driver = webdriver.Opera()
    elif driver_type == 5:
        driver = webdriver.PhantomJS()
    driver.wait = WebDriverWait(driver, 5)
    return driver


def scroll(driver, username):
    url = "https://twitter.com/" + username
    print(url)
    driver.get(url)
    # get beautifulsoup from page
    pageHTML = driver.page_source
    page_object = BeautifulSoup(pageHTML, 'html.parser')
    try:
        global total_followers, total_followings, total_favorites, total_lists, total_tweets
        total_followers = page_object.find('li', attrs={'class': 'ProfileNav-item--followers'})
        if total_followers:
            total_followers = total_followers.find('span', attrs={'class': 'ProfileNav-value'}).text
            total_followers = int(total_followers.replace(',', ''))

        total_followings = page_object.find('li', attrs={'class': 'ProfileNav-item--following'})
        if total_followings:
            total_followings = total_followings.find('span', attrs={'class': 'ProfileNav-value'}).text
            total_followings = int(total_followings.replace(',', ''))

        total_favorites = page_object.find('li', attrs={'class': 'ProfileNav-item--favorites'})
        if total_favorites:
            total_favorites = total_favorites.find('span', attrs={'class': 'ProfileNav-value'}).text
            total_favorites = int(total_favorites.replace(',', ''))

        total_lists = page_object.find('li', attrs={'class': 'ProfileNav-item--lists'})
        if total_lists:
            total_lists = total_lists.find('span', attrs={'class': 'ProfileNav-value'}).text
            total_lists = int(total_lists.replace(',', ''))

        total_tweets = page_object.find('li', attrs={'class': 'ProfileNav-item--tweets'})
        total_tweets = total_tweets.find('span', attrs={'class': 'ProfileNav-value'}).text
        total_tweets = int(total_tweets.replace(',', ''))
    except Exception as e:
        # print(str(e))
        # Get current system exception
        ex_type, ex_value, ex_traceback = sys.exc_info()

        # Extract unformatter stack traces as tuples
        trace_back = traceback.extract_tb(ex_traceback)

        # Format stacktrace
        stack_trace = list()

        for trace in trace_back:
            stack_trace.append(
                "File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

        print("Exception type : %s " % ex_type.__name__)
        print("Exception message : %s" % ex_value)
        print("Stack trace : %s" % stack_trace)

        total_tweets = 200
    pages = math.ceil(total_tweets / 20)
    start_time = time.time()  # remember when we started
    i = 1
    while i < pages:
        print('loading more')
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        i += 1


def fetch_hashtags(tweet):
    newTags = tweet.split(' ')
    hashtags = ''
    for newTag in newTags:
        if newTag.startswith('#'):
            hashtags += ' ' + str(newTag)
    return hashtags


def fetch_mentions(tweet):
    mentions = ''
    new_mentions = tweet.split(' ')
    if new_mentions:
        for new_mention in new_mentions:
            if new_mention.startswith("@"):
                mentions += ' ' + new_mention
    return mentions


def scrape_tweets(driver, handle):
    try:
        print('Scraping tweets')
        tweet_divs = driver.page_source
        obj = BeautifulSoup(tweet_divs, "html.parser")
        tweets = obj.find_all('div', attrs={'class': 'js-stream-tweet'})
        names = []
        tweet_texts = []
        hashtags = []
        retweeteds = []
        mentions = []
        tweet_ids = []
        tweet_urls = []
        timestamps = []
        comments = []
        likes = []
        shares = []
        for tweet in tweets:
            tweet_likes = tweet.find("button", attrs={"class": "js-actionFavorite"})
            tweet_likes = tweet_likes.find("span", attrs={"class": "ProfileTweet-actionCount"}).text
            tweet_shares = tweet.find("button", attrs={"class": "js-actionRetweet"})
            tweet_shares = tweet_shares.find("span", attrs={"class": "ProfileTweet-actionCount"}).text
            tweet_comments = tweet.find("button", attrs={"class": "js-actionReply"})
            tweet_comments = tweet_comments.find("span", attrs={"class": "ProfileTweet-actionCount"}).text
            message = tweet.find("p", attrs={"class": "TweetTextSize"}).text

            name = tweet.find('strong', attrs={"class": "fullname"}).text
            tweet_id = str(tweet["data-tweet-id"])
            tweet_url = 'https://twitter.com' + tweet["data-permalink-path"]
            timestamp = tweet.find('span', attrs={"class": "_timestamp"})
            timestamp = int(timestamp['data-time'])
            value = datetime.fromtimestamp(timestamp)
            timestamp = value.strftime('%d %B %Y %H:%M:%S')
            retweeted = tweet.find('span', attrs={"class": "js-retweet-text"})
            if retweeted:
                retweeted = "Retweeted " + name
            names.append(name)
            tweet_texts.append(message)
            hashtags.append(fetch_hashtags(message))
            mentions.append(fetch_mentions(message))
            retweeteds.append(retweeted)
            tweet_ids.append(tweet_id)
            tweet_urls.append(tweet_url)
            timestamps.append(timestamp)
            comments.append(tweet_comments)
            likes.append(tweet_likes)
            shares.append(tweet_shares)

        data = {
            "name": names,
            "tweet": tweet_texts,
            "hashtags": hashtags,
            "mentions": mentions,
            "tweet_ids": tweet_ids,
            "tweet_urls": tweet_urls,
            "timestamps": timestamps,
            "retweeted": retweeteds,
            "comments": comments,
            "likes": likes,
            "shares": shares
        }

        make_csv(data, handle)

    except Exception as e:
        # print(str(e))
        # Get current system exception
        ex_type, ex_value, ex_traceback = sys.exc_info()

        # Extract unformatter stack traces as tuples
        trace_back = traceback.extract_tb(ex_traceback)

        # Format stacktrace
        stack_trace = list()

        for trace in trace_back:
            stack_trace.append(
                "File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

        print("Exception type : %s " % ex_type.__name__)
        print("Exception message : %s" % ex_value)
        print("Stack trace : %s" % stack_trace)
        driver.quit()


def make_csv(data, handle):
    l = len(data['name'])
    print("count: %d" % l)
    with open(handle + "_" + str(time.time()) + ".csv", "a+") as file:
        fieldnames = ['Name', 'Total Tweets', 'Total Followers', 'Total Followings', 'Total Lists', 'Text',
                      'Retweeted', 'Comments on this tweet', 'Likes on this tweet', 'Shares on this tweet',
                      'Hashtags', 'Mentioned', 'Tweet Id', 'Tweet Urls', 'Tweet Time']
        writer = DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(l):
            writer.writerow({'Name': data['name'][i],
                             'Total Tweets': total_tweets,
                             'Total Followers': total_followers,
                             'Total Followings': total_followings,
                             'Total Lists': total_lists,
                             'Text': data['tweet'][i],
                             'Retweeted': data['retweeted'][i],
                             'Comments on this tweet': data['comments'][i],
                             'Likes on this tweet': data['likes'][i],
                             'Shares on this tweet': data['shares'][i],
                             'Hashtags': data['hashtags'][i],
                             'Mentioned': data['mentions'][i],
                             'Tweet Id': data['tweet_ids'][i],
                             'Tweet Urls': data['tweet_urls'][i],
                             'Tweet Time': data['timestamps'][i]
                             })


def get_all_dates(start_date, end_date):
    dates = []
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    step = timedelta(days=1)
    while start_date <= end_date:
        dates.append(str(start_date.date()))
        start_date += step

    return dates


driver_type = int(
    input("1) Firefox | 2) Chrome | 3) IE | 4) Opera | 5) PhantomJS\nEnter the driver you want to use: "))
username = raw_input("Enter twitter handles to search: ")
if ',' in username:
    usernames = username.split(',')
    for user in usernames:
        driver = init_driver(driver_type)
        scroll(driver, user)
        scrape_tweets(driver, user)
        time.sleep(5)
        print("The tweets for {} are ready!".format(user))
        driver.quit()
else:
    driver = init_driver(driver_type)
    scroll(driver, username)
    scrape_tweets(driver, username)
    time.sleep(5)
    print("The tweets for {} are ready!".format(username))
    driver.quit()
