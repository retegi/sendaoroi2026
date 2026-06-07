from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "pages/home.html"


class RootsView(TemplateView):
    template_name = "pages/roots.html"


class ProgramView(TemplateView):
    template_name = "pages/program.html"


class WhatWeDoView(TemplateView):
    template_name = "pages/what_we_do.html"


class CompassView(TemplateView):
    template_name = "pages/compass.html"


class ProcessView(TemplateView):
    template_name = "pages/process.html"


class ServicesView(TemplateView):
    template_name = "pages/services.html"


class IsItForMeView(TemplateView):
    template_name = "pages/is_it_for_me.html"


class TeamView(TemplateView):
    template_name = "pages/team.html"


class ContactView(TemplateView):
    template_name = "pages/contact.html"
