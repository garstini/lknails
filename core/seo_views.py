from django.http import HttpResponse, JsonResponse
from django.urls import reverse

from core.models import SiteSettings


def robots_txt(_request):
    site_settings = SiteSettings.objects.first()
    domain = site_settings.domain if site_settings else "lknailslashes.de"
    content = f"User-agent: *\nAllow: /\nSitemap: https://{domain}/sitemap.xml\n"
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml(request):
    pages = [
        request.build_absolute_uri(reverse("home")),
        request.build_absolute_uri(reverse("service_list")),
        request.build_absolute_uri(reverse("booking_create")),
    ]
    xml = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"]
    xml.extend(f"<url><loc>{page}</loc></url>" for page in pages)
    xml.append("</urlset>")
    return HttpResponse("".join(xml), content_type="application/xml")


def health_check(_request):
    return JsonResponse({"status": "ok"})
