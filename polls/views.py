from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Choice, Question, Vote

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(LoginRequiredMixin,generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter()
    
    def get(self, request, *args, **kwargs):
        """
        Check if Question is pending using self.object.can_vote().
        If voting is not allowed, we set an error.
        Then, we redirect the user to the polls index page.
        """
        self.object = self.get_object()
        if not self.object.can_vote():
            messages.error(request, "Voting is not allowed for this question.")
            return redirect('polls:index')
        return super().get(request, *args, **kwargs)

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    user = request.user

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
        
    except (KeyError, not question.can_vote):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "The Question is not pending currently.",
        })
        
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    
    try:
        vote = Vote.objects.get(user=user, choice=selected_choice)

    except Vote.DoesNotExist:
        vote = Vote.objects.create(user=user, choice=selected_choice)
        messages.success(request, f"Your vote '{selected_choice.choice_text}' was recorded")

    else:
        vote.choice = selected_choice
        messages.success(request, f"Your vote was changed to '{selected_choice.choice_text}'")
    
    vote.save()
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    
    
    # try:
    #     selected_choice = question.choice_set.get(pk=request.POST['choice'])
        
    # except (KeyError, not question.can_vote):
    #     return render(request, 'polls/detail.html', {
    #         'question': question,
    #         'error_message': "The Question is not pending currently.",
    #     })
        
    # except (KeyError, Choice.DoesNotExist):
    #     # Redisplay the question voting form.
    #     return render(request, 'polls/detail.html', {
    #         'question': question,
    #         'error_message': "You didn't select a choice.",
    #     })
    # else:
    #     selected_choice.votes += 1
    #     selected_choice.save()
    #     # Always return an HttpResponseRedirect after successfully dealing
    #     # with POST data. This prevents data from being posted twice if a
    #     # user hits the Back button.
    #     return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))