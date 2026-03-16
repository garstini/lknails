from core.models import SiteSettings


def site_context(_request):
    settings = SiteSettings.objects.first()
    domain = settings.domain if settings and settings.domain else "lknailslashes.de"
    return {
        "global_site_settings": settings,
        "currency_symbol": "€",
        "currency_code": settings.currency_code if settings else "EUR",
        "site_url": f"https://{domain}",
    }
