from django.db import models

class WebSiteModel(models.Model):

    web_id = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True

class Presenter(WebSiteModel):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, null=True)
    site_url = models.TextField(blank=True, null=True)

    @property 
    def num_sermons():
        return self.sermons.count()


class Sermon(WebSiteModel):
    title = models.CharField(max_length=255)
    conference = models.CharField(max_length=255, blank=True, null=True)
    series = models.ForeignKey("Series", blank=True, null=True)
    duration = models.CharField(max_length=10)
    presenter = models.ForeignKey("Presenter", blank=True, null=True)

class Series(WebSiteModel):

    title = models.CharField(max_length=255)
