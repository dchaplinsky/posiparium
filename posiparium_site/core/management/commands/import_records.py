import os
import fnmatch
import re
from openpyxl import load_workbook
from dateutil.parser import parse as dt_parse
from django.core.management.base import BaseCommand, CommandError

from core.models import (
    County, PublicOffice, Convocation,
    MemberOfParliament, MP2Convocation,
    Minion2MP2Convocation, Minion)


def cleanup(s):
    if hasattr(s, "value"):
        s = s.value

    s = s or ""
    if isinstance(s, str):
        return re.sub("\s+", " ", s.strip().strip("\xa0"))
    else:
        return s


class Command(BaseCommand):
    regions_mapping = {
        "Волинська область": "lt",
        "Вінницька область": "vn",
        "Дніпропетровська область": "dp",
        "Житомирська область": "zt",
        "Закарпатська область": "uz",
        "Запорізька область": "zp",
        "Кіровоградська область": "kr",
        "Львівська область": "lviv",
        "Миколаївська область": "mk",
        "Одеська область": "od",
        "Полтавська область": "pl",
        "Рівненська область": "rv",
        "Сумська область": "sumy",
        "Тернопільска область": "te",
        "Харківська область": "kh",
        "Херсонська область": "ks",
        "Черкаська область": "ck",
        "Чернівецька область": "cv",
        "Чернігівська область": "cn",
        "Івано-Франківська область": "if",
        "Київська область": "kyiv",
        "Донецька область": "dn",
        "Луганська область": "lg",
    }

    def add_arguments(self, parser):
        parser.add_argument('input_path')

    def handle(self, *args, **options):
        data_dir = options["input_path"]

        for file in os.listdir(data_dir):
            if fnmatch.fnmatch(file, '*.xlsx'):
                wb = load_workbook(os.path.join(data_dir, file))

                for name in wb.get_sheet_names():
                    ws = wb[name]

                    for i, row in enumerate(ws.rows):
                        if i == 0:
                            continue

                        if not any(map(lambda r: r.value, row)):
                            continue

                        (region, office, convocation, period, photo, mp_name,
                            link, party, fraction, comission, minion,
                            confirmation_date) = map(cleanup, row[:12])

                        body_type = " ".join(office.split()[-2:]).lower()
                        inflected_region = " ".join(office.split()[:-2])
                        if body_type in ("обласна рада", "обласна влада", "обласна раада"):
                            kind = 0
                            # Fixing shitty typos
                            office = inflected_region + " обласна рада"
                        elif body_type == "міська рада":
                            kind = 1
                            office = inflected_region + " міська рада"
                        else:
                            self.stderr.write(
                                "Cannot classify public body type {}".format(body_type)
                            )
                            continue

                        region_model, _ = County.objects.get_or_create(
                            name=region,
                            defaults={
                                "slug": self.regions_mapping[region]
                            }
                        )

                        office_model, _ = PublicOffice.objects.get_or_create(
                            name=office,
                            region=region_model,
                            defaults={
                                "kind": kind
                            }
                        )

                        try:
                            year_from, year_to = period.split("-")
                        except ValueError:
                            self.stderr.write(
                                "Cannot parse convocation period {}".format(period)
                            )

                        convocation_model, _ = Convocation.objects.get_or_create(
                            number=convocation,
                            office=office_model,
                            defaults={
                                "year_from": year_from,
                                "year_to": year_to,
                            }
                        )

                        mp_model, mp_created = MemberOfParliament.objects.get_or_create(
                            name__iexact=mp_name,
                            convocations__office__region=region_model,
                            defaults={
                                "name": mp_name
                            }
                        )
                        if not mp_created:
                            self.stdout.write(
                                "Reused one mp {}, {}, {}".format(
                                    file, mp_name, office))

                        mp2conv_model, _ = MP2Convocation.objects.get_or_create(
                            mp=mp_model,
                            convocation=convocation_model,
                            defaults={
                                "party": party,
                                "fraction": fraction,
                                "comission": comission,
                                "link": link
                            }
                        )

                        if minion:
                            try:
                                minion_model, minion_created = Minion.objects.get_or_create(
                                    name__iexact=minion,
                                    mp__convocation__office__region__pk=region_model.pk,
                                    defaults={
                                        "name": minion
                                    }
                                )

                                if not minion_created:
                                    self.stdout.write(
                                        "Reused one minion {}, {}, {}".format(
                                            file, minion, office))

                            except Minion.MultipleObjectsReturned:
                                self.stderr.write("Shite, too much minions {}, {}, {}".format(file, minion, office))
                                break

                            minion2mp2conv_model, _ = Minion2MP2Convocation.objects.get_or_create(
                                mp2convocation=mp2conv_model,
                                minion=minion_model,
                                defaults={
                                    "confirmed": confirmation_date
                                }
                            )
                        else:
                            self.stdout.write(
                                "MP {} from {} doesn't have little helpers".format(mp_name, office)
                            )
