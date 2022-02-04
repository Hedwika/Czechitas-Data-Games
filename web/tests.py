import datetime
from typing import Tuple

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from . import forms, models


class LoginAndGameTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="test")
        self.user.set_password("1X<ISRUkw+tuK")
        self.user.save()
        self.new_user = models.NewUser.objects.filter(user=self.user).first()

        self.user_2 = get_user_model().objects.create(username="test_2")
        self.user_2.set_password("5DdfgdgER*tuK")
        self.user_2.save()
        self.new_user_2 = models.NewUser.objects.filter(user=self.user_2).first()
        LoginAndGameTest.create_events((self.new_user, self.new_user_2))

    @classmethod
    def create_events(cls, new_users):
        # Create a current event
        start = datetime.datetime.now() - datetime.timedelta(hours=1)
        end = datetime.datetime.now() + datetime.timedelta(hours=1)

        current_event = models.Event(title="Test current event", start=start, end=end, description="Test", id=1)
        current_event.save()

        # Create a past event
        start = datetime.datetime.now() - datetime.timedelta(days=1)
        end = start + datetime.timedelta(hours=1)

        event = models.Event(title="Test past event", start=start, end=end, description="Test", id=2)
        event.save()

        # Create a future event
        start = datetime.datetime.now() + datetime.timedelta(days=1)
        end = start + datetime.timedelta(hours=1)

        event = models.Event(title="Test future event", start=start, end=end, description="Test", id=3)
        event.save()

        cls.create_tasks(current_event)
        cls.create_teams(event, new_users)

    @classmethod
    def create_tasks(cls, event: models.Event):
        assignment1 = models.Assignment(description="Assignment 1",
                                        answer_type="TEXT", right_answer="Test right answer", order=1, event=event,
                                        id=1)
        assignment1.save()

        assignment2 = models.Assignment(description="Assignment 2",
                                        answer_type="TEXT", right_answer="Test right answer", order=2, event=event,
                                        id=2)
        assignment2.save()

        assignment3 = models.Assignment(description="Assignment 3",
                                        answer_type="SEZNAM", right_answer="alpha,beta,gama", order=3, event=event,
                                        id=3)
        assignment3.save()

        assignment4 = models.Assignment(description="Assignment 4",
                                        answer_type="ČÍSLO", right_answer="3.1415", order=4, event=event,
                                        id=4)
        assignment4.save()

    @classmethod
    def create_teams(cls, event: models.Event, new_users: Tuple):
        team = models.Team(name="T1", event=event)
        team.save()
        for user in new_users:
            user.team = team
            user.save()

    def test_create_team(self):
        # User can create a new team
        login = self.client.login(username='test', password='1X<ISRUkw+tuK')
        response = self.client.post(reverse('tymy'), {"name": "T2", "new_team": ""}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Team.objects.filter(name="T2").count(), 1)
        team = models.Team.objects.filter(name="T2").first()
        self.new_user.refresh_from_db()
        self.assertEqual(self.new_user.team.pk, team.pk)

        # Second user can join the new team
        login = self.client.login(username="test_2", password='5DdfgdgER*tuK')
        response = self.client.post(reverse('tymy'), {"join_team": team.pk}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.new_user_2.refresh_from_db()
        self.assertEqual(self.new_user_2.team.pk, team.pk)

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='test', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('title_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/title_page.html")
        self.assertEqual(str(response.context['user']), 'test')

        # Two events should be visible - past and future
        self.assertEqual(len(response.context['object_list']), 2)

        self.assertEqual(response.context['object_list'][0].id, 1)
        self.assertEqual(response.context['object_list'][1].id, 3)
        self.assertContains(response, "První úkol")

    def test_text_assignment(self):
        login = self.client.login(username='test', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('title_page'))
        self.assertEqual(str(response.context['user']), 'test')

        # I should start with a assigment 1
        response = self.client.get(reverse('ukoly', kwargs={'event': 1}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["assignment"].id, 1)
        self.assertEqual(models.TeamProgress.objects.filter(team=self.new_user.team).count(), 0)

        # I am trying a wrong answer so the assigment should stay the same
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "Wrong text answer"},
                                    follow=True)
        self.assertContains(response, forms.WRONG_ANSWER_TEXT)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["assignment"].id, 1)

        # I am trying the right answer so the assigment should be the second one
        # The space in the beginning and end should be stripped
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "   Test right answer   "},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["assignment"].id, 2)
        self.assertEqual(models.TeamProgress.objects.filter(team=self.new_user.team).count(), 1)

        # I am trying the right answer so I should see the congratulations page
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "Test right answer"},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.TeamProgress.objects.filter(team=self.new_user.team).count(), 2)

        # LIST question type
        # I am delivering incomplete the answer
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "alpha"},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, forms.NOT_A_LIST_TEXT)
        self.assertEqual(models.TeamProgress.objects.filter(team=self.new_user.team).count(), 2)

        # I am delivering incomplete the answer
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "alpha, beta"},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, forms.WRONG_ANSWER_TEXT)
        self.assertEqual(models.TeamProgress.objects.filter(team=self.new_user.team).count(), 2)

        # I am delivering superfluous content in the answer
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "alpha, beta, gama, delta"},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, forms.WRONG_ANSWER_TEXT)
        self.assertEqual(models.TeamProgress.objects.filter(team=self.new_user.team).count(), 2)
        
        # I am delivering the correct elements in a different order, this should be accepted
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "gama, beta, alpha"},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.TeamProgress.objects.filter(team=self.new_user.team).count(), 3)

        # NUMBER question type
        # I am using a comma instead of a dot
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "3,1415"},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, forms.COMMA_TEXT)
        self.assertEqual(models.TeamProgress.objects.filter(team=self.new_user.team).count(), 3)

        # I am delivering text instead of number
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "abc"},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, forms.NOT_A_NUMBER_TEXT)
        self.assertEqual(models.TeamProgress.objects.filter(team=self.new_user.team).count(), 3)

        # I am delivering incorrect number
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "3.1515"},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, forms.WRONG_ANSWER_TEXT)
        self.assertEqual(models.TeamProgress.objects.filter(team=self.new_user.team).count(), 3)

        # I am delivering incorrect number
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "3.1499"},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, forms.WRONG_ANSWER_TEXT)
        self.assertEqual(models.TeamProgress.objects.filter(team=self.new_user.team).count(), 3)

        # I am delivering correct number, the difference behind second decimal should be accepted
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "3.1449"},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.TeamProgress.objects.filter(team=self.new_user.team).count(), 4)

        self.assertTemplateUsed(response, "congrats.html")

