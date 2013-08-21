from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.views.generic.edit import FormView
from django.views.generic.base import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
import settings
from wagers.models import EditableHTML
from wagers.models import Tournament
admin.autodiscover()

class UserCreateForm(UserCreationForm):
    next = forms.CharField()

class RegisterView(FormView):
    template_name = "registration/register.html"
    form_class = UserCreateForm

    def form_valid(self, form):
        form.save()
        user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password1"])
        login(self.request, user) 
        self.success_url = form.cleaned_data["next"]
        return super(RegisterView, self).form_valid(form)

class HomePageView(View):
    template_name = "wagers/home.html"
    landing_template = "wagers/admin_landing.html"
    def get(self, request):
        if request.user.is_authenticated():
            html, created = EditableHTML.objects.get_or_create(id=1)
            admin_tournaments = Tournament.objects.filter(created_by=request.user, is_open=True)[:5]
            ran_tournaments = Tournament.objects.filter(created_by=request.user, is_open=False)[:5]
            playing_tournaments = Tournament.objects.filter(player__user=request.user, is_open=True)[:5]
            played_tournaments = Tournament.objects.filter(player__user=request.user, is_open=False)[:5]
            return render(request,
                self.template_name,
                {"html": html,
                 "admin_tourneys": admin_tournaments,
                 "ran_tourneys": ran_tournaments,
                 "played_tourneys": played_tournaments,
                 "playing_tourneys": playing_tournaments})
        else:
            return render(request, self.landing_template, {})
        
    def post(self, request):
        if self.request.POST["html"]:      
            editable_html, created = EditableHTML.objects.get_or_create(id=1)
            editable_html.html = self.request.POST["html"]
            editable_html.save()
        return HttpResponseRedirect("/")

class About(View):
    template_name = "wagers/about.html"
    def get(self, request):
        if request.user.is_authenticated():
            html, created = EditableHTML.objects.get_or_create(id=2)
            return render(request, self.template_name, {"html": html})
        
    def post(self, request):
        if self.request.POST["html"]:      
            editable_html, created = EditableHTML.objects.get_or_create(id=2)
            editable_html.html = self.request.POST["html"]
            editable_html.save()
        return HttpResponseRedirect("/about")

urlpatterns = patterns('',
    # Include Examples:
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^logout', 'django.contrib.auth.views.logout'),
    url(r'^register', RegisterView.as_view(), name='register'),
    url(r'^wagers/', include('wagers.urls')),
    url(r'^gdapi/', include('game_database.urls')),
    url(r'^about$', About.as_view(), name='about'),
    url(r'', include('social_auth.urls')),
    url(r'^login', 'django.contrib.auth.views.login', name='login'),

    # url(r'^wagering/', include('wagering.foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/r/', include('django.conf.urls.shortcut')),
    url(r'^admin/', include(admin.site.urls)))


if settings.DEBUG:
    urlpatterns += patterns('',
      (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': "C:/Users/joshua/Programming/wagering/site_media"}))
