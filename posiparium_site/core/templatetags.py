from functools import reduce

from django_jinja import library
from dateutil.parser import parse


@library.global_function
def updated_querystring(request, params):
    """Updates current querystring with a given dict of params, removing
    existing occurrences of such params. Returns a urlencoded querystring."""
    original_params = request.GET.copy()
    for key in params:
        if key in original_params:
            original_params.pop(key)
    original_params.update(params)
    return original_params.urlencode()


@library.filter
def format_date(s):
    try:
        dt = parse(s, yearfirst=True)
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        return s


def ukr_plural(value, *args):
    value = int(value) % 100
    rem = value % 10
    if value > 4 and value < 20:
        return args[2]
    elif rem == 1:
        return args[0]
    elif rem > 1 and rem < 5:
        return args[1]
    else:
        return args[2]


@library.filter
def uk_plural(value, args):
    args = args.split(',')
    return ukr_plural(value, *args)


def deepgetattr(obj, attr):
    """Recurses through an attribute chain to get the ultimate value."""

    try:
        return reduce(getattr, attr.split('.'), obj)
    except AttributeError:
        return None


@library.filter
def highlight(obj, field_name):
    if hasattr(obj.meta, "highlight") and hasattr(obj.meta.highlight, field_name):
        return " ".join(getattr(obj.meta.highlight, field_name))
    else:
        return deepgetattr(obj, field_name)
