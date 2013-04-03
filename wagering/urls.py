from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import FormView
from django.views.generic.base import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login


from wagers.models import EditableHTML

admin.autodiscover()

class RegisterView(FormView):
    template_name = "registration/register.html"
    form_class = UserCreationForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password1"])
        login(self.request, user) 
        return super(RegisterView, self).form_valid(form)

class HomePageView(View):
    template_name = "wagers/home.html"
    def get(self, request):
        html, created = EditableHTML.objects.get_or_create(id=1)
        return render(request, self.template_name, {"html": html})

    def post(self, request):
        if self.request.POST["html"]:      
            editable_html, created = EditableHTML.objects.get_or_create(id=1)
            editable_html.html = self.request.POST["html"]
            editable_html.save()
        return HttpResponseRedirect("/")


urlpatterns = patterns('',
    # Include Examples:
    url(r'^$', HomePageView.as_view()),
    url(r'^login', 'django.contrib.auth.views.login'),
    url(r'^logout', 'django.contrib.auth.views.logout'),
    url(r'^register', RegisterView.as_view()),
    url(r'^wagers/', include('wagers.urls')),
    # url(r'^wagering/', include('wagering.foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': "C:\Users\joshua\Programming\wagering\site_media"})
)
