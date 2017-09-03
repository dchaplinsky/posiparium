from operator import itemgetter
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.db.models import Count

from core.elastic_models import Minion as ElasticMinion
from core.models import (
    County, Convocation, MemberOfParliament, Minion2MP2Convocation,
    Minion
)
from core.paginator import paginated


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


def home_stats(request):
    regions = County.objects.order_by("name").annotate(
        num_mps=Count('publicoffice__convocation__mp2convocation', distinct=True),
        num_minions=Count('publicoffice__convocation__mp2convocation__minion'))

    return JsonResponse(
        [
            {
                "name": r.name,
                "slug": r.slug,
                "url": r.get_absolute_url(),
                "num_mps": r.num_mps,
                "num_minions": r.num_minions
            }

            for r in regions
        ],
        safe=False
    )


def county(request, county_slug):
    region = get_object_or_404(County, slug=county_slug)

    results = ElasticMinion.search().query(
        "term", region_slug=region.slug)

    return render(request, "county.jinja", {
        "region": region,
        "convocations": Convocation.objects.select_related(
            "office", "office__region").filter(office__region=region).order_by(
            "office").annotate(
                num_mps=Count('mp2convocation', distinct=True),
                num_minions=Count('mp2convocation__minion')
        ),

        "search_results": paginated(
            request, results.sort(
                'body', 'region', 'mp.grouper', 'name.raw')),
    })


def convocation(request, county_slug, convocation_id):
    region = get_object_or_404(County, slug=county_slug)
    try:
        convocation = get_object_or_404(
            Convocation,
            pk=int(convocation_id),
            office__region=region
        )
    except ValueError:
        return HttpResponseBadRequest()

    results = ElasticMinion.search().query(
        "term", convocation_id=convocation.pk)

    return render(request, "convocation.jinja", {
        "region": region,
        "convocation": convocation,
        "convocations": Convocation.objects.select_related(
            "office", "office__region").filter(pk=convocation.pk).annotate(
                num_mps=Count('mp2convocation', distinct=True),
                num_minions=Count('mp2convocation__minion')
        ),


        "search_results": paginated(
            request, results.sort(
                'body', 'region', 'mp.grouper', 'name.raw')),
    })


def search(request):
    query = request.GET.get("q", "")

    if query:
        results = ElasticMinion.search() \
            .query(
                "multi_match", query=query,
                operator="and",
                fields=["mp.name", "name"]) \
            .highlight_options(
                order='score',
                fragment_size=500,
                number_of_fragments=100,
                pre_tags=['<u class="match">'], post_tags=["</u>"]) \
            .highlight("mp.name", "name")

    else:
        results = ElasticMinion.search().query('match_all')

    return render(request, "search.jinja", {
        "search_results": paginated(
            request, results.sort(
                'body', 'region', 'mp.grouper', 'name.raw'), cnt=30),
    })


def mp(request, mp_id):
    mp = get_object_or_404(MemberOfParliament, pk=mp_id)

    return render(request, "mp.jinja", {
        "mp": mp
    })


def minion(request, minion_id):
    minion = get_object_or_404(Minion, pk=minion_id)

    return render(request, "minion.jinja", {
        "minion": minion
    })
