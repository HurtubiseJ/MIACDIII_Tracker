from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.http import Http404

from .models import Game, Team

def index(request):
    Game_List = Game.objects.order_by("-game_date")[:5]
    # template = loader.get_template("Home/index.html")
    context = {"Game_List": Game_List}
    return HttpResponse(render(request, "Home/index.html", context))

def detail(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    return render(request, "Home\index.html", {"Game": game})

# Create your views here.
