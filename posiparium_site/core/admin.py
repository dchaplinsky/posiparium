from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.html import format_html
from core.models import County, PublicOffice, Convocation, MemberOfParliament, Minion


class CountyAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "koatuu"]


class PublicOfficeAdmin(admin.ModelAdmin):
    list_display = ["name", "region", "kind"]


class ConvocationAdmin(admin.ModelAdmin):
    list_display = ["number", "year_from", "year_to", "office"]


class MemberOfParliamentAdmin(admin.ModelAdmin):
    def convocations_str(self, obj):
        return render_to_string(
            "admin/convocations.jinja",
            {"convocations": obj.convocations.all()}
        )

    convocations_str.short_description = 'Скликання'
    convocations_str.allow_tags = True
    search_fields = ["name"]
    list_display = ["name", "convocations_str"]


class MinionAdmin(admin.ModelAdmin):
    search_fields = ["name", "mp__mp__name"]
    list_display = ["name", "mp_name"]

    def mp_name(self, obj):
        return format_html(
            "<br/>".join(mp.mp.name for mp in obj.mp.select_related("mp"))
        )


admin.site.register(County, CountyAdmin)
admin.site.register(PublicOffice, PublicOfficeAdmin)
admin.site.register(Convocation, ConvocationAdmin)
admin.site.register(MemberOfParliament, MemberOfParliamentAdmin)
admin.site.register(Minion, MinionAdmin)
