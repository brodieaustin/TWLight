import datetime
from faker import Faker
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from TWLight.applications.factories import ApplicationFactory
from TWLight.applications.models import Application
from TWLight.resources.models import Partner, Stream

class Command(BaseCommand):
    help = "Adds a number of example applications."

    def add_arguments(self, parser):
        parser.add_argument('num', nargs='+', type=int)

    def handle(self, *args, **options):
        num_applications = options['num'][0]
        fake = Faker()

        available_partners = Partner.objects.all()
        # Don't fire any applications from the superuser.
        all_users = User.objects.exclude(is_superuser=True)

        for _ in range(num_applications):
            random_user = random.choice(all_users)
            random_partner = random.choice(available_partners)

            app = ApplicationFactory(
                editor = random_user.editor,
                partner = random_partner,
                hidden = self.chance(True, False, 10)
                )

            # Make sure partner-specific information is filled.
            if random_partner.specific_stream:
                app.specific_stream = random.choice(
                    Stream.objects.filter(partner=random_partner))

            if random_partner.specific_title:
                app.specific_title = fake.sentence(nb_words= 3)

            if random_partner.agreement_with_terms_of_use:
                app.agreement_with_terms_of_use = True

            if random_partner.account_email:
                app.account_email = fake.email()

            # Imported applications have very specific information, and were
            # all imported on the same date.
            imported = self.chance(True, False, 50)
            import_date = datetime.datetime(2017, 7, 17, 0, 0, 0)

            if imported:
                app.status = Application.SENT
                app.date_created = import_date
                app.date_closed = import_date
                app.rationale = "Imported on 2017-07-17"
                app.comments = "Imported on 2017-07-17"
            else:
                app.status = random.choice(Application.STATUS_CHOICES)[0]
                app.date_created = fake.date_time_between(
                    start_date = random_user.editor.wp_registered,
                    end_date = "now",
                    tzinfo=None)
                app.rationale = fake.paragraph(nb_sentences=3)
                app.comments = fake.paragraph(nb_sentences=2)

            # Assign sent_by if this is a non-imported sent applications
            if app.status == Application.SENT:
                if not imported:
                    app.sent_by = random_partner.coordinator
                    app.date_closed = fake.date_time_between(
                        start_date = app.date_created,
                        end_date = "now",
                        tzinfo=None)
                else:
                    app.date_closed = import_date

            app.save()

        # Renew a selection of apps.
        all_apps = Application.objects.all()
        num_to_renew = int(num_applications*0.3)
        for app_to_renew in random.sample(all_apps, num_to_renew):
            app_to_renew.renew()

    def chance(self, selected, default, chance):
        # A percentage chance to select something, otherwise selects
        # the default option. Used to generate data that's more
        # in line with the live site distribution.

        roll = random.randint(0,100)
        if roll < chance:
            selection = selected
        else:
            selection = default

        return selection