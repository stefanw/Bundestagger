from django.db import models

# Create your models here.

NORMAL_LEVEL = 0
EDIT_LEVEL = 1
SUPER_LEVEL = 2

class User(models.Model):
    openid = models.CharField(blank=True, max_length=255)
    ipaddress = models.IPAddressField(blank=True, null=True)
    username = models.CharField(null=True, blank=True, max_length=30)
    level = models.IntegerField(default=0)
    last_seen = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.level >= EDIT_LEVEL

    @property
    def is_admin(self):
        return self.level >= SUPER_LEVEL
