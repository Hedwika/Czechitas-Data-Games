import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from . import models


class LoginAndGameTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create(username="test")
        user.set_password("1X<ISRUkw+tuK")
        user.save()
        LoginAndGameTest.create_events()

    @classmethod
    def create_events(cls):
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

    @classmethod
    def create_tasks(cls, event: models.Event):
        assignment1 = models.Assignment(description="Assignment 1",
                                        answer_type="TEXT", right_answer="Test right answer", order=1, event=event,
                                        id=1)
        assignment1.save()

        assignment2 = models.Assignment(description="Assignment 1",
                                        answer_type="TEXT", right_answer="Test right answer", order=2, event=event,
                                        id=2)
        assignment2.save()

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

        # I am trying a wrong answer so the assigment should stay the same
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "Wrong text answer"},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["assignment"].id, 1)

        # I am trying the right answer so the assigment should be the second one
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "Test right answer"},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["assignment"].id, 2)

        # I am trying the right answer so I should see the congratulations page
        response = self.client.post(reverse('ukoly', kwargs={'event': 1}), {"answer": "Test right answer"},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "congrats.html")

