import json

from django.core.management.base import BaseCommand

import requests

from ciadata.models import *

class Command(BaseCommand):
    help = "Pulls down the info from GYC web site"

    def handle(self, *args, **options):

        # Fake Chrome as the browser
        headers = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36"
        }

        GYC_CONTROLLER_URL = "http://gycweb.org/sm-controller.php"
        params = {"vo-action" : "init"}

        # Make the initial request
        print "Loading presenter listing"
        r = requests.get(GYC_CONTROLLER_URL, headers=headers, params=params)

        result = r.json()

        presenters_created = 0
        sermons_created = 0

        presenter_list_dict = result.get("panel").get("presenter").get("array")
        for presenter_id, presenter_dict in presenter_list_dict.iteritems():
            name = presenter_dict.get("name", "Presenter")
            #print "Processing presenter 1: %s" % name
            presenter, created = Presenter.objects.get_or_create(name=name,
                web_id=presenter_id)

            if created:
                print " Presenter created: %s" % presenter.name
                presenters_created += 1


        # Now we make another request for the sermon listing
        print "Loading sermon listing"
        params = {"vo-action" : "null", "filter_conditions" : "{\"limit\":1000}"}
        r = requests.get(GYC_CONTROLLER_URL, headers=headers, params=params)

        result = r.json()

        sermons = result.get("content") # an array of sermons
        for sermon_json in sermons:
            try:
                web_id = sermon_json.get("id")
                title = sermon_json.get("name")
                slug = sermon_json.get("slug")
                date = sermon_json.get("date")
                duration = sermon_json.get("duration")

                if "presenter_id" not in sermon_json:
                    print "Skipping sermon: %s, no presenter_id" % title
                    continue

                try:
                    presenter_id = int(sermon_json.get("presenter_id"))
                except TypeError:
                    print "Skipping sermon: %s, presenter_id not an int" % title
                    continue

                sermon, sermon_created = Sermon.objects.get_or_create(web_id=web_id, title=title)
                if sermon_created:
                    print " Created sermon: %s" % sermon.title
                    sermons_created += 1

                if "presenters" in sermon_json:
                    # make sure all the presenters are created
                    presenter_list_dict = sermon_json.get("presenters")
                    for presenter_id, presenter_dict in presenter_list_dict.iteritems():
                        name = presenter_dict.get("name", "Presenter")
                        #print "Processing presenter 2: %s" % name
                        slug = presenter_dict.get("slug")
                        presenter, created = Presenter.objects.get_or_create(name=name,
                            web_id=presenter_id)
                        if created:
                            presenters_created += 1
                        presenter.slug = slug
                        presenter.site_url = "http://gycweb.org/presenters/%s" % slug
                        presenter.save()
                else:
                    presenter_id = sermon_json.get("presenter_id")
                    name = sermon_json.get("presenter", "Presenter")
                    if not name:
                        name = "Presenter"
                    #print "Processing presenter 3: %s" % name
                    slug = presenter_dict.get("slug")
                    presenter, created = Presenter.objects.get_or_create(name=name,
                        web_id=presenter_id)
                    if created:
                        presenters_created += 1
                    presenter.slug = slug
                    presenter.save()

                if "presenter_id" in sermon_json:
                    presenter = Presenter.objects.get(web_id=int(sermon_json.get("presenter_id")))
                    sermon.presenter = presenter
                    sermon.save()
            except UnicodeEncodeError as e:
                continue

        print "Created %s sermons and %s presenters" % (sermons_created, presenters_created)

