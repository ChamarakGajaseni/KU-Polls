import datetime
from django.test import TestCase
from django.utils import timezone
from .models import Question, User
from django.urls import reverse

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(
            list(response.context['latest_question_list']),
            [question],
            )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)
        
    def is_published_with_future_pub_date(self):
        """
        is_published should be false,
        if question is set to be published in the future.
        """
        future_pub_date = timezone.now() +timezone.timedelta(days=1)
        question = Question(pubdate=future_pub_date)
        self.assertIs(question.is_published(),False)
        
    def is_published_with_past_pub_date(self):
        """
        is_published should be True,
        if question was published in the past.
        """
        past_pub_date = timezone.now() - timezone.timedelta(days=1)
        question = Question(pubdate=past_pub_date)
        self.assertIs(question.is_published(),True)
        
    def is_published_now(self):
        """
        is_published should be True,
        if question is published now.
        """
        question = Question(pubdate=timezone.now())
        self.assertIs(question.is_published(),True)
    
    def test_cannot_vote_after_end_date(self):
        """
        Cannot vote if current time is passed end_date.
        """
        past_pub_date = timezone.now() - timezone.timedelta(days=1)
        question = Question(pub_date=timezone.now(), end_date=past_pub_date)
        self.assertIs(question.can_vote(), False)

    def test_cannot_vote_before_pub_date(self):
        """
        Cannot vote if current time is passed end_date.
        """
        future_pub_date = timezone.now() + timezone.timedelta(days=1)
        question = Question(pub_date=future_pub_date, end_date= future_pub_date + timezone.timedelta(days=10))
        self.assertIs(question.can_vote(), False)
        
    def test_can_vote_published_now(self):
        """
        Can vote if question pub_date is equals to the time now
        """
        question = Question(pub_date=timezone.now(), end_date=timezone.now() + timezone.timedelta(days=1) )
        self.assertIs(question.can_vote(), True)

    def test_can_vote_during_pending_time(self):
        """
        Can vote if current time is between pub_date and end_date.
        """
        past_pub_date = timezone.now() - timezone.timedelta(days=1)
        future_end_date = timezone.now() + timezone.timedelta(days=1)
        question = Question(pub_date=past_pub_date,end_date=future_end_date)
        self.assertIs(question.can_vote(), True)
        
class QuestionDetailViewTests(TestCase):

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
    
    def test_future_question(self):
        """
        Cannot see question's detail if it isn't published yet. 
        """
        future_question = create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertRedirects(response, reverse('polls:index'))
