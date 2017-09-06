from django.contrib.sitemaps import GenericSitemap

from core.models import Minion, County, Convocation, MemberOfParliament

sitemaps = {
    "regions": GenericSitemap({'queryset': County.objects.all()}),
    "convocations": GenericSitemap({'queryset': Convocation.objects.all()}),
    "minions": GenericSitemap({'queryset': Minion.objects.all()}),
    "mps": GenericSitemap({'queryset': MemberOfParliament.objects.all()}),
}
