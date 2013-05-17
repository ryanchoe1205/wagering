from django.views.generic.base import View
from django.utils import simplejson as json
from django.db.models import Q
from django import http
from models import Game
from forms import ScheduleForm
from forms import GameForm
import datetime
import operator

class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
        return json.dumps(context, default=dthandler, indent=4)


class Schedule(View, JSONResponseMixin):
    def get(self, request):
        form = ScheduleForm(request.GET)
        if form.is_valid():
            game_types = form.get_game_type()
            _from = form.cleaned_data["start_time"]
            to = form.cleaned_data["end_time"]
            combined_query = reduce(operator.or_, [Q(game_type=game_type) for game_type in game_types], Q(game_type=""))
            games = list(Game.objects.filter(combined_query).filter(start_time__range=(_from, to)).values())
            return self.render_to_response({"games": games})
        else:
            return self.render_to_response({"request_error": form.errors, "games": []})

class GetGameByID(View, JSONResponseMixin):
    def get(self, request):
        form = GameForm(request.GET)
        if form.is_valid():
            game = form.get_game()
            return self.render_to_response({"game": [game]})
        else:
            return self.render_to_response({"request_error": form.errors, "game": []})