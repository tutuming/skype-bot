#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

class Feed(models.Model):
    name = models.CharField(max_length = 30)

    url = models.URLField()

    last_feed_id = models.CharField(max_length  = 1024, null = True, blank = True)
    created_at = models.DateTimeField(u'登録日時', auto_now_add = True)
    last_fetched_at = models.DateTimeField(u'最終更新日時', auto_now_add = True)
    
    def __unicode__(self):
        return unicode(self.name);
