"""
Poll's Question and Choice model.
Question has a question and a publication date.
A Choice has two fields: the text of the choice and a vote tally.
Each Choice is associated with a Question.
"""
import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('ending date',null=True)
    

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
    def is_published(self): 
        now = timezone.now()
        return self.pub_date <= now
    
    def can_vote(self):
        now = timezone.now()
        if self.end_date == None:
            return self.pub_date<= now 
        return self.pub_date<= now <=self.end_date

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    @property
    def votes(self):
        """Return the number of votes for this choice."""
        return len(Vote.objects.filter(choice=self))

    def __str__(self):
        return self.choice_text
    
class Vote(models.Model):
    """Record a choice for a question made by a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user.username} voted for {self.choice.choice_text}"