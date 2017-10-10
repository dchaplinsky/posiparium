import re
from string import capwords

from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from django.db import models

from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.exceptions import EasyThumbnailsError


def title(s):
    chunks = s.split()
    chunks = map(lambda x: capwords(x, u"-"), chunks)
    return u" ".join(chunks)


def parse_fullname(person_name):
    # Extra care for initials (especialy those without space)
    person_name = re.sub("\s+", " ",
                         person_name.replace(".", ". ").replace('\xa0', " "))

    chunks = person_name.strip().split(" ")

    last_name = ""
    first_name = ""
    patronymic = ""

    if len(chunks) == 2:
        last_name = title(chunks[0])
        first_name = title(chunks[1])
    elif len(chunks) > 2:
        last_name = title(" ".join(chunks[:-2]))
        first_name = title(chunks[-2])
        patronymic = title(chunks[-1])

    return last_name, first_name, patronymic


def generate_suggestions(last_name, first_name, patronymic):
    if not last_name:
        return []

    return [
        " ".join([last_name, first_name, patronymic]),
        " ".join([first_name, patronymic, last_name]),
        " ".join([first_name, last_name])
    ]


class County(models.Model):
    name = models.CharField("Регіон", max_length=100, primary_key=True)
    slug = models.CharField("slug", max_length=20)
    koatuu = models.CharField("КОАТУУ", max_length=20, blank=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    def get_absolute_url(self):
        return reverse("county", kwargs={"county_slug": self.slug})

    class Meta:
        verbose_name = "Регіон"
        verbose_name_plural = "Регіони"


class PublicOffice(models.Model):
    name = models.CharField("Рада", max_length=100, primary_key=True)
    region = models.ForeignKey("County")
    kind = models.IntegerField(
        "Тип органу",
        choices=(
            (0, "Обласна рада"),
            (1, "Міська рада"),
            (2, "Районна рада"),
        ),
        default=0
    )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    class Meta:
        verbose_name = "Орган влади"
        verbose_name_plural = "Органи влади"


class Convocation(models.Model):
    number = models.IntegerField("Скликання")
    year_from = models.IntegerField("З", blank=True, null=True)
    year_to = models.IntegerField("По", blank=True, null=True)
    office = models.ForeignKey("PublicOffice")

    def __unicode__(self):
        return "{} скликання {}".format(self.number, self.office.name)

    def __str__(self):
        return self.__unicode__()

    def get_absolute_url(self):
        return reverse("convocation", kwargs={
            "county_slug": self.office.region.slug, "convocation_id": self.pk
        })

    class Meta:
        verbose_name = "Скликання"
        verbose_name_plural = "Скликання"


class MemberOfParliament(models.Model):
    convocations = models.ManyToManyField(
        "Convocation", verbose_name="Скликання", through="MP2Convocation")
    name = models.CharField("ПІБ", max_length=200, db_index=True)
    img = models.ImageField(blank=True)

    def __unicode__(self):
        return "Депутат %s" % (self.name)

    def __str__(self):
        return self.__unicode__()

    def get_absolute_url(self):
        return reverse("mp_details", kwargs={"mp_id": self.pk})

    class Meta:
        verbose_name = "Депутат"
        verbose_name_plural = "Депутати"


class MP2Convocation(models.Model):
    party = models.CharField("Партія", max_length=512, blank=True)
    fraction = models.CharField("Фракція", max_length=512, blank=True)
    comission = models.CharField("Комісія", max_length=512, blank=True)

    link = models.URLField("Посилання", max_length=512, blank=True)

    mp = models.ForeignKey("MemberOfParliament")
    convocation = models.ForeignKey("Convocation")

    def __unicode__(self):
        return "%s, депутат %s скликання" % (self.mp.name, self.convocation)

    def __str__(self):
        return self.__unicode__()

    def to_dict(self):
        m = model_to_dict(self, fields=[
            "party", "fraction", "comission"])

        m["convocation"] = self.convocation_id
        m["name"] = self.mp.name
        m["link"] = self.link
        m["id"] = self.mp.id
        if self.mp.img:
            try:
                m["img_thumbnail"] = get_thumbnailer(self.mp.img)['avatar'].url
            except EasyThumbnailsError:
                pass

        m["grouper"] = "%s %s" % (self.convocation_id, self.mp.name)

        base_d = {
            "mp": m,
            "convocation": self.convocation.number,
            "convocation_id": self.convocation.pk,
            "body": self.convocation.office.name,
            "body_id": self.convocation.office.pk,
            "region": self.convocation.office.region.name,
            "region_slug": self.convocation.office.region.slug,
            "mp_name_suggest": {
                "input": generate_suggestions(*parse_fullname(self.mp.name))
            }
        }

        minions = self.minion2mp2convocation_set.select_related("minion").all()
        if minions:
            for minion in minions:
                d = base_d.copy()
                d.update(minion.to_dict())
                yield d
        else:
            yield base_d

    class Meta:
        verbose_name = "Належність до скликання"
        verbose_name_plural = "Належності до скликання"


class Minion2MP2Convocation(models.Model):
    mp2convocation = models.ForeignKey("MP2Convocation")
    minion = models.ForeignKey("Minion")
    confirmed = models.CharField("Підтверджено", max_length=200)

    def to_dict(self):
        """
        Convert Minion model to an indexable presentation for ES.
        """
        d = model_to_dict(self, fields=["confirmed"])

        d["minion_id"] = self.minion_id

        d["name_suggest"] = {
            "input": generate_suggestions(
                *parse_fullname(self.minion.name))
        }

        d["_id"] = self.id
        d["id"] = self.minion.id
        d["name"] = self.minion.name

        return d

    class Meta:
        verbose_name = "Належність помічника до депутата"
        verbose_name_plural = "Належності помічників до депутатов"


class Minion(models.Model):
    mp = models.ManyToManyField(
        "MP2Convocation", verbose_name="Депутат",
        through=Minion2MP2Convocation)
    name = models.CharField("ПІБ", max_length=200, db_index=True)

    class Meta:
        verbose_name = "Помічник"
        verbose_name_plural = "Помічники"

    def __unicode__(self):
        return "Помічник %s (%s)" % (self.name, self.mp)

    def __str__(self):
        return self.__unicode__()

    def get_absolute_url(self):
        return reverse("minion_details", kwargs={"minion_id": self.pk})
