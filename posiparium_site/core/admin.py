from django.contrib import admin
from django.template.loader import render_to_string
from core.models import County, PublicOffice, Convocation, MemberOfParliament


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

    list_display = ["name", "convocations_str"]


admin.site.register(County, CountyAdmin)
admin.site.register(PublicOffice, PublicOfficeAdmin)
admin.site.register(Convocation, ConvocationAdmin)
admin.site.register(MemberOfParliament, MemberOfParliamentAdmin)
