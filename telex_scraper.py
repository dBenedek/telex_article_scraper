#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 19:52:41 2022

@author: dbenedek
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import exceptions  
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from nltk.corpus import stopwords
import time
import simplemma
import re
from collections import Counter
import os
import logging
from bs4 import BeautifulSoup
import requests
from wordcloud import WordCloud
import matplotlib.pyplot as plt


class TelexScraper:
    def __init__(self, delay=5):
        if not os.path.exists("telex_data"):
            os.makedirs("telex_data")
        log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_fmt)
        self.delay=delay
        logging.info("Starting driver")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_options)

    def open_url(self, url):
        """Go to telex, click on Elfogadom"""
        # Go to telex:
        logging.info("Opening telex.hu")
        self.driver.maximize_window()
        self.driver.get(url)
        time.sleep(self.delay)
        button = self.driver.find_element(By.XPATH,
                                      "//*[contains(text(), 'ELFOGADOM')]")
        button.click()
        time.sleep(self.delay)
        
    def find_articles(self):
        """Find articles on main page
        """
        logging.info("Looking for articles on main page")
        titles = self.driver.find_elements(By.CLASS_NAME, "cl-title")
        titles_text = [title.text for title in titles]
        time.sleep(self.delay)
        return [titles, titles_text]
    
    def wait(self, t_delay=None):
        """
        Parameters
        ----------
        t_delay [optional] : int
            seconds to wait.
        """
        delay = self.delay if t_delay == None else t_delay
        time.sleep(delay)
        
    def scrape_article(self):
        """
        Scrapes the selected article.
        ----------
        Returns 
        author: selenium obejct, date_posted: selenium object
        fb_shared_text: string, article_content_text: string
        [author, date_posted, fb_shared_text, article_content_text]

        """
        try:
            date_posted = self.driver.find_element(By.CLASS_NAME, 'history--original')
        except exceptions.NoSuchElementException:
            logging.info('No date found.')
            pass
        try:
            fb_shared = self.driver.find_element(By.CLASS_NAME, 'share-network-facebook')
            fb_shared_text = fb_shared.text
        except exceptions.NoSuchElementException:
            logging.info('No facebook share info.')
            pass
        try:
            article_content = self.driver.find_element(By.CLASS_NAME, 'article-html-content')
            article_content_text = [re.sub('[„,";.\-!?”]', '', w).lower() for w in re.split('\s|\n', article_content.text)]
            # Lemmatize:
            langdata = simplemma.load_data('hu', 'en')
            article_content_text = [simplemma.lemmatize(w, langdata) for w in article_content_text if str.isalpha(w) is True]
        except exceptions.NoSuchElementException:
            logging.info('No identifiable content.')
            pass
        if fb_shared_text in ['', ' ']:
            fb_shared_text = 0
        try:
            author = self.driver.find_element(By.CLASS_NAME, 'author__name')
        except exceptions.StaleElementReferenceException:
            author = self.driver.find_element(By.CLASS_NAME, 'author__name')
            self.driver.execute_script("arguments[0].scrollIntoView();", author)
            author = self.driver.find_element(By.CLASS_NAME, 'author__name')
            pass
        except exceptions.NoSuchElementException:
            logging.info('No author found.')
            pass
        return [author, date_posted, fb_shared_text, article_content_text]
    
    def wait_for_element_ready(self, by, text):
        try:
            WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((by, text)))
        except exceptions.TimeoutException:
            logging.debug("wait_for_element_ready TimeoutException")
            pass
        
    def close_session(self):
        """This function closes the actual session"""
        logging.info("Closing session.")
        self.driver.close()
        
    def run(self):
        """
        Runs the webpage scraping, stores the words of all articles.
        Returns
        -------
        text_words : list
            All the words of all articles on the main page.
        """
        # Get linking and other non important words (we don't need them):
        r = requests.get('https://hu.wiktionary.org/wiki/Kateg%C3%B3ria:magyar_k%C3%B6t%C5%91sz%C3%B3k')
        soup = BeautifulSoup(r.text, 'html')
        ksz = soup.find_all("div", {"class": "mw-category-group"})
        ksz = [k.findAll('li') for k in ksz]
        ksz = [i.text for k in  ksz for i in k]
        ksz.extend(['a', 'az', 'be', 'ki', 'le', 'fel', 'össze', 'vissza',
                    'egy', 'már', 'még', 'el', 'meg', 'ami', 'aki', 'ez'])
        hun_stopwords = [re.sub('õ', 'ő', w) for w in stopwords.words('hungarian')]
        ksz.extend(hun_stopwords)
        # Create daat folder:
        if not os.path.exists("telex_data"):
            os.mkdir('telex_data')
        self.wait_for_element_ready(By.XPATH,
                                    "//*[contains(text(), 'ELFOGADOM')]")
        self.open_url('https://www.telex.hu/')
        logging.info("Begin Telex article scraping.")
        self.wait(2)
        titles, titles_text = self.find_articles()
        text_words = []
        for i in range(len(titles)):
            title = self.driver.find_elements(By.CLASS_NAME, "cl-title")[i]
            title_text = title.text
            webdriver.ActionChains(self.driver).move_to_element(title).click(title).perform()
            self.wait(2)
            current_url = self.driver.current_url
            author, date_posted, fb_shared_text, article_content_text = self.scrape_article()
            text_words.extend([w for w in article_content_text if w not in ksz])
            print(author.text, title_text)
            self.wait(2)
            if current_url != 'https://www.telex.hu/':
                self.driver.back()
                self.wait(2)
            elif self.driver.current_url == 'data:,':
                self.driver.get('https://www.telex.hu/')
                self.wait(2)
            else:
                pass
        logging.info("Done scraping.")
        logging.info("Closing DB connection.")
        bot.close_session()
        return text_words
        
    
if __name__ == "__main__":
    bot = TelexScraper()
    words = bot.run()
    word_counts = Counter(words)
    word_counts_ordered = dict(sorted(word_counts.items(), key=lambda item: item[1]))
    # Create and generate a word cloud image:
    wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(' '.join(words))
    # Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    print([*word_counts_ordered.keys()][-10:])
    print([*word_counts_ordered.values()][-10:])