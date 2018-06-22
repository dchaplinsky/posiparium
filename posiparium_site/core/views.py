from operator import itemgetter
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.db.models import Count
from django.views import View

from elasticsearch_dsl.query import Q
from core.elastic_models import Minion as ElasticMinion
from core.models import (
    County, Convocation, MemberOfParliament, Minion2MP2Convocation,
    Minion
)
from core.paginator import paginated


class SuggestView(View):
    def get(self, request):
        q = request.GET.get('q', '').strip()

        suggestions = []
        seen = set()

        s = ElasticMinion.search().source(
            ['names_autocomplete']
        ).highlight('names_autocomplete').highlight_options(
            order='score', fragment_size=100,
            number_of_fragments=10,
            pre_tags=['<strong>'],
            post_tags=["</strong>"]
        )

        s = s.query(
            "bool",
            must=[
                Q(
                    "match",
                    names_autocomplete={
                        "query": q,
                        "operator": "and"
                    }
                )
            ],
            should=[
                Q(
                    "match_phrase",
                    names_autocomplete__raw={
                        "query": q,
                        "boost": 2
                    },
                ),
                Q(
                    "match_phrase_prefix",
                    names_autocomplete__raw={
                        "query": q,
                        "boost": 2
                    },
                )
            ]
        )[:200]

        res = s.execute()

        for r in res:
            if "names_autocomplete" in r.meta.highlight:
                for candidate in r.meta.highlight["names_autocomplete"]:
                    if candidate.lower() not in seen:
                        suggestions.append(candidate)
                        seen.add(candidate.lower())


        rendered_result = [
            render_to_string("autocomplete.jinja", {
                "result": {
                    "hl": k
                }
            })
            for k in suggestions[:20]
        ]

        return JsonResponse(rendered_result, safe=False)


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
            "office", "number").annotate(
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
                fields=["mp.name", "name", "persons"]) \
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
