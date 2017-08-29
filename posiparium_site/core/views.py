from operator import itemgetter
from collections import Counter
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Count

from core.elastic_models import Minion as ElasticMinion
from core.models import (
    County, Convocation, Minion, MemberOfParliament, MP2Convocation,
    Minion2MP2Convocation)
# from core.paginator import paginated, DjangoPageRangePaginator


def unique(source):
    """
    Returns unique values from the list preserving order of initial list.
    :param source: An iterable.
    :type source: list
    :returns: List with unique values.
    :rtype: list
    """
    seen = set()
    return [seen.add(x) or x for x in source if x not in seen]


def suggest(request):
    def assume(q, fuzziness):
        results = []

        search = ElasticMinion.search()\
            .source(['name_suggest', 'name'])\
            .params(size=0)\
            .suggest(
                'name',
                q,
                completion={
                    'field': "name_suggest",
                    'size': 10,
                    'fuzzy': {
                        'fuzziness': fuzziness,
                        'unicode_aware': True
                    }
                }
        )

        res = search.execute()
        if res.success:
            results += res.suggest['name'][0]['options']

        search = ElasticMinion.search()\
            .source(['mp_name_suggest', 'mp.name'])\
            .params(size=0)\
            .suggest(
                'name',
                q,
                completion={
                    'field': "mp_name_suggest",
                    'size': 10,
                    'fuzzy': {
                        'fuzziness': fuzziness,
                        'unicode_aware': True
                    }
                }
        )

        res = search.execute()
        if res.success:
            results += res.suggest['name'][0]['options']

        results = sorted(results, key=itemgetter("_score"), reverse=True)

        if results:
            return unique(
                val._source.name
                if "name" in val._source else val._source.mp.name
                for val in results
            )
        else:
            return []

    q = request.GET.get('q', '').strip()

    # It seems, that for some reason 'AUTO' setting doesn't work properly
    # for unicode strings
    fuzziness = 0

    if len(q) > 2:
        fuzziness = 1

    suggestions = assume(q, fuzziness)

    if not suggestions:
        suggestions = assume(q, fuzziness + 1)

    return JsonResponse(suggestions, safe=False)


def home(request):
    return render(request, "home.jinja", {
        "count_of_minions": Minion2MP2Convocation.objects.count(),
        "count_of_mps": MemberOfParliament.objects.count(),

        "regions": County.objects.order_by("name").annotate(
            num_mps=Count('publicoffice__convocation__mp2convocation', distinct=True),
            num_minions=Count('publicoffice__convocation__mp2convocation__minion'))
    })


def county(request, county_slug):
    region = get_object_or_404(County, slug=county_slug)

    return render(request, "county.jinja", {
        "region": region
    })
