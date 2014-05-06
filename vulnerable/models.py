from django.db import models


class CVE_2014_0474_Blacklist(models.Model):
    ip = models.IPAddressField()

    class Meta:
        db_table = 'blacklist'

    def __unicode__(self):
        return self.ip


class Upload(models.Model):
    a_file = models.FileField(upload_to='.')
