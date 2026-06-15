from django.urls import path

from .views import (
    CompassView,
    ContactView,
    CookiesView,
    HomeView,
    IsItForMeView,
    LegalNoticeView,
    PrivacyView,
    ProcessView,
    ProgramView,
    RootsView,
    ServicesView,
    TeamView,
    WhatWeDoView,
)


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("nuestras-raices/", RootsView.as_view(), name="roots"),
    path("programa/", ProgramView.as_view(), name="program"),
    path("programa/que-hacemos/", WhatWeDoView.as_view(), name="what_we_do"),
    path("programa/nuestra-brujula/", CompassView.as_view(), name="compass"),
    path(
        "programa/acompanamiento-como-proceso/",
        ProcessView.as_view(),
        name="process",
    ),
    path("programa/pasos-y-servicios/", ServicesView.as_view(), name="services"),
    path("sendaoroi-es-para-mi/", IsItForMeView.as_view(), name="is_it_for_me"),
    path("equipo/", TeamView.as_view(), name="team"),
    path("contactar/", ContactView.as_view(), name="contact"),
    path("aviso-legal/", LegalNoticeView.as_view(), name="legal_notice"),
    path("privacidad/", PrivacyView.as_view(), name="privacy"),
    path("cookies/", CookiesView.as_view(), name="cookies"),
]
