from core.models import County


def get_regions(request):
    return {
        "all_regions": County.objects.all().order_by("name")
    }
