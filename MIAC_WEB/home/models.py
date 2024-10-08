from django.db import models

# Create your models here.


class Team(models.Model):
    team_name = models.CharField(max_length=50)
    wins = models.IntegerField(default=0)
    loses = models.IntegerField(default=0)

    def __str__(self):
        text = self.team_name + ", " + str(self.wins) + "-" + str(self.loses)
        return text

class Game(models.Model):
    team1 = models.ForeignKey("Team", related_name="team1", on_delete=models.CASCADE)
    team2 = models.ForeignKey("Team", related_name = "team2", on_delete=models.CASCADE)
    game_date = models.DateTimeField()

    def __str__(self):
        text = "Team 1: " + self.team1.__str__() + "\n" + "Team 2: " + self.team2.__str__() + "\n" + "Date: " + str(self.game_date)
        return text