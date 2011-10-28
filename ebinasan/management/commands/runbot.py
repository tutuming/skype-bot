#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import feedparser
import sgmllib
from django.core.management.base import BaseCommand
from django.conf import settings
from ebinasan import models

import re

SPACES = re.compile(ur'[\s　]+')

class Stripper(sgmllib.SGMLParser):
    def __init__(self):
        sgmllib.SGMLParser.__init__(self)

    def strip(self, some_html):
        self.theString = ""
        self.feed(some_html)
        self.close()

        self.theString = SPACES.sub(' ', self.theString)
        
        return self.theString

    def handle_data(self, data):
        self.theString += data

stripper = Stripper()

def stripHTML(t):
    return HTMLPT.sub(t , "")

class Command(BaseCommand):
    def init_chat(self):
        if settings.DEBUG:
            self.chat = self.skype.CreateChatWith("echo123")
        else:
            for bookmarkedChat in self.skype.BookmarkedChats:
                if bookmarkedChat.Topic == settings.EBINASAN_BOOKMARKED_CHAT_NAME:
                    self.chat = bookmarkedChat
                    return
                raise RuntimeError(u'no bookmaedked chat named "{0}"'.format(settings.EBINASAN_BOOKMARKED_CHAT_NAME))

    def say(self, msg):
        self.chat.SendMessage(msg)
        
    def handle(self, *args, **options):
        import Skype4Py
        self.skype = Skype4Py.Skype()
        self.skype.Attach()

        self.skype.OnMessageStatus = self.onMessageStatus
        
        self.init_chat()
        self.say(u'(dance) 海老名なう(ninja)')

        self.run_feed_loop(30)

    def onMessageStatus(self, msg, event):
        if event == u'RECEIVED':
            if msg.Body.find(u'海老名さん') != -1:
                self.say(u'へいへい、いますよいますよ(ninja)(ninja)(ninja)');

    def run_feed_loop(self, interval = 30):
        while True:
            feeds = self.get_feeds()
            plural = len(feeds) > 1
            if feeds and plural:
                self.say(u'★{0}件 更新のお知らせがございます'. format(len(feeds)))
            for i, feed in enumerate(feeds):
                msg = u'{0} - \n{1}\n詳しくはコチラ : {2}'.format(feed['title'],  feed['desc'], feed['url'])
                if plural:
                    self.say(u'--- {0} 件目 : {1}'.format(i + 1, feed['feed_title']))
                self.say(msg)

            time.sleep(interval) 

    def get_feeds(self):
        feeds = models.Feed.objects.all()

        ret = []
        for feed in feeds:
            d = feedparser.parse(feed.url)
            pre_last_feed_id = feed.last_feed_id
            for i, entry in enumerate(d.entries):
                if not i :
                    feed.last_feed_id = entry.id

                if entry.id == pre_last_feed_id:
                    break

                entry_dict = {}
                entry_dict['title'] = entry.title
                entry_dict['url'] = entry.link
                if entry.has_key('content'):
                    entry_dict['desc'] = stripper.strip(entry.content[0].value)
                elif entry.has_key('summary_detail'):
                    entry_dict['desc'] = stripper.strip(entry.summary_detail.value)
                else:
                    entry_dict['desc'] = ''
                entry_dict['feed_title'] = d.feed.title
                
                ret.append(entry_dict)
            feed.save()
        ret.reverse()
        
        return ret
