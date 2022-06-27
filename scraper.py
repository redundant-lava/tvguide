#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 19:18:32 2022

Webscraper for disney channel tv guide

@author: wfa2
"""

url = "https://tv.fr.disney.be/guide-tv"

import argparse
from playwright.sync_api import Playwright, sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def run(playwright: Playwright) -> None:
    # won't work with slow_mo < 30 ??? not sure why
    browser = playwright.chromium.launch(headless=False, slow_mo=30)
    
    #browser = playwright.chromium.launch(headless=True)
    # does not work in headless - site might be blocking playwright
    
    context = browser.new_context()
    # Open new page
    page = context.new_page()
    
    # Go to https://tv.fr.disney.be/guide-tv
    page.goto("https://tv.fr.disney.be/guide-tv")
    
    # Click text=Tout refuser --> refuse cookies
    page.locator("text=Tout refuser").click()
    
    # Click on date
    select='a[data-date="'+args.date+'"]'
    page.locator(select).click()
    
    # wait for schedule to load
    page.wait_for_load_state("networkidle")
   #page.wait_for_selector('id=schedule')
    
    # get all episode elements
    episodes = page.locator('div[class="inner-entry"]')
    count = episodes.count()
    
    f = open(args.file, 'w')
    f.write('date, time, show, episode, synopsis\n')
    
    for i in range(count):
        ep = episodes.nth(i).inner_html()
        soup = BeautifulSoup(ep, "html.parser")
        
        # select first p element with 'time' class
        time = soup.find("p", class_="time")
        
        # select other elements
        show = soup.find("h2", class_="show-title")
        ep_title = soup.find("h2", class_="episode-title")
        synopsis = soup.find("p", class_="episode-description")
        
        # create & write csv row
        row = [args.date, time.text, show.text, ep_title.text, synopsis.text]
        row = [r.replace("\n", " ") for r in row]
        f.write(', '.join(row))
        f.write('\n')
    f.close()
    
    #text = episodes.all_text_contents()
    print(str(episodes.count())+' showtimes found for '+args.date)
    print('scheudle saved to '+args.file)
    # ---------------------
    context.close()
    browser.close()



if __name__ == "__main__":
    
    today = datetime.today().strftime('%Y%m%d')
    max_date = datetime.today()+timedelta(days=3)
    min_date = datetime.combine(datetime.today(), datetime.min.time())
    
    parser = argparse.ArgumentParser(description='schedule information')
    parser.add_argument('--date', dest='date', type=str, default=today, help='<YYYYMMDD> date of schedule, must be <=3 days after today')
    parser.add_argument('--file', dest='file', type=str, help='output file (will be overwritten)')
    
    args = parser.parse_args()
    if args.file is None:
        args.file = 'schedules/schedule-'+args.date+'.csv'
        
    try:
        d = datetime.strptime(args.date, '%Y%m%d')
    except ValueError:
        print('Error - invalid date format: '+args.date)
        exit(1)
   
    if d>max_date or d<min_date:
        print('Error - date out of range')
        exit(1)
    
    with sync_playwright() as playwright:
       run(playwright)
   
    exit(0)
