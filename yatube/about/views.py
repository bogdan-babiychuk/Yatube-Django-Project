from django.views.generic.base import TemplateView

# Create your views here.


class AboutAuthorView(TemplateView):
    template_name: str = 'about/author.html'


class AboutTechView(TemplateView):
    template_name: str = 'about/tech.html'
