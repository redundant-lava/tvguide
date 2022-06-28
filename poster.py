#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 16:00:01 2022

script to create posts for daily schedules 

@author: wfa2
"""
import pytumblr
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime
from babel.dates import format_date, format_datetime, format_time
import argparse


load_dotenv()
BLOG = 'miraculous-guide-tv-belgique'
schedule_dir = 'schedules'

#login to tumblr
def get_client() -> pytumblr.TumblrRestClient:
    client = pytumblr.TumblrRestClient(
        os.environ['consumer_key'],
        os.environ['consumer_secret'],
        os.environ['oauth_token'],
        os.environ['oauth_secret'])
    return client


def post_schedule(client, date, schedule_path=None, blog=BLOG):
    if schedule_path is None:
        schedule_path = f'{schedule_dir}/schedule-{date}.csv'
    
    schedule=pd.read_csv(schedule_path, sep=';')

    show = schedule[schedule['show'].str.contains('Miraculous')]
    table = show[['time', 'episode']]
    body = "*Heures de séances en Disney Channel Belgique*  \n\n  "
    #html tables do not display on dash!
    #body = table.to_html(index=False, header=False)
    
    for index, row in table.iterrows():
        t = row['time']
        ep = row['episode']
        body += f'- {t} ~~ **{ep}**\n'
    
    d = datetime.strptime(date, '%Y%m%d')
    date_fr = format_date(d, locale='fr')
    title = f'Miraculous Guide TV -- {date_fr}'
    slug = date_fr.replace(' ', '-')
    
    client.create_text(blog, state="published", slug=slug, title=title, body=body, format='markdown')
    url = f'https://{blog}.tumblr.com/post/{slug}'
    print(f'post published at {url}')
    
def reblog_schedule(client, slug, blog=BLOG):
    posts = client.posts(blog)['posts'] #list of posts, each post is a dict
    reblog_post = None
    for p in posts:
        if p['slug'] == slug:
            reblog_post = p
            break
    
    if reblog_post is not None:
        client.reblog(blog, id=reblog_post['id'], reblog_key=reblog_post["reblog_key"])
        print(f'post for {reblog_post["slug"]} reblogged')
    else:
        print("could not find post to reblog")
    
    
if __name__ == "__main__":
    today = datetime.today().strftime('%Y%m%d')
    
    parser = argparse.ArgumentParser(description='post information')
    parser.add_argument('--date', dest='date', type=str, default=today, help='<YYYYMMDD> date of schedule, must be <=3 days after today')
    parser.add_argument('--file', dest='file', type=str, help='input file (will be overwritten)')
    parser.add_argument('--reblog', dest='reblog', action="store_true", help='use when rebloging existing post')
    args = parser.parse_args()
    
    args = parser.parse_args()
    if args.file is None:
        args.file = f'{schedule_dir}/schedule-{args.date}.csv'
    
    client = get_client()
    
    if args.reblog:
        d = datetime.strptime(args.date, '%Y%m%d')
        date_fr = format_date(d, locale='fr')
        slug = date_fr.replace(' ', '-')
        reblog_schedule(client, slug)
    else:
        post_schedule(client,args.date)
    
    
    
    