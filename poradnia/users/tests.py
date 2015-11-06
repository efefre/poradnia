from __future__ import absolute_import
from django.core import mail
from django.core.urlresolvers import reverse_lazy
from django.test import TestCase, RequestFactory
from guardian.shortcuts import assign_perm
from users.factories import UserFactory
from users.models import User
from users.forms import UserForm
from users.views import UserListView


class UserTestCase(TestCase):

    def test_get_user_by_get_by_email_or_create(self):
        self.assertEqual(User.objects.count(), 1)
        new_user = User.objects.get_by_email_or_create('sarah@example.com')
        self.assertEqual(User.objects.count(), 2)
        get_user = User.objects.get_by_email_or_create('sarah@example.com')
        self.assertEqual(new_user, get_user)
        self.assertEqual(User.objects.count(), 2)

    def _create_user(self, email, username):
        User.objects.email_to_unique_username(email)
        self.assertEqual(username, username)
        User.objects.create_user(username=username)

    def test_email_to_username(self):
        self._create_user('example@example.com', 'example_example_com')
        for i in range(1, 11):
            self._create_user('example@example.com', 'example_example_com-' + str(i))
        with self.assertRaises(ValueError):
            self._create_user('example@example.com', 'example_example_com-11')

    def test_has_picture(self):
        self.assertTrue(UserFactory().picture)


class UserQuerySetTestCase(TestCase):

    def test_for_user_manager(self):
        u1 = User.objects.create(username="X-1")
        u2 = User.objects.create(username="X-2", is_staff=True)
        u3 = User.objects.create(username="X-3", is_staff=True, is_superuser=True)
        qs = User.objects.for_user(u1).registered().all()
        self.assertQuerysetEqual(list(qs), [repr(u1), repr(u2), repr(u3)], ordered=False)
        qs = User.objects.for_user(u2).registered().all()
        self.assertQuerysetEqual(list(qs), [repr(u2), repr(u3)], ordered=False)
        qs = User.objects.for_user(u3).registered().all()
        self.assertQuerysetEqual(list(qs), [repr(u1), repr(u2), repr(u3)], ordered=False)

    def _register_email_count(self, notify, count):
        u = User.objects.register_email(email='sarah@example.com', notify=notify)
        self.assertEqual(len(mail.outbox), count)
        self.assertEqual(User.objects.get(email='sarah@example.com'), u)

    def test_register_email_no_notify(self):
        self._register_email_count(notify=True, count=1)

    def test_register_email_notify(self):
        self._register_email_count(notify=False, count=0)


class UserFormTestCase(TestCase):

    def test_has_avatar(self):
        self.assertIn('picture', UserForm().fields)


class UserDetailViewTestCase(TestCase):

    def setUp(self):
        self.object = UserFactory(is_staff=False)

    def login(self, user=None):
        self.client.login(username=(user or self.object).username, password='pass')

    def get(self):
        return self.client.get(self.object.get_absolute_url())

    def own_resp(self):
        self.login()
        return self.get()

    def test_contains_username(self):
        self.assertContains(self.own_resp(), self.object.username)

    def test_contains_assigned_cases(self):
        url = reverse_lazy('cases:list') + '?permission='+str(self.object.pk)
        self.login()
        self.assertNotContains(self.own_resp(), url)

        user = UserFactory()
        assign_perm('users.can_view_other', user)
        assign_perm('cases.can_assign', user)
        self.login(user=user)
        self.assertContains(self.get(), url)


class UserListViewTestCase(TestCase):
    url = reverse_lazy('users:list')

    def setUp(self):
        self.user_list = UserFactory.create_batch(size=1, is_staff=False)
        self.staff_list = UserFactory.create_batch(size=1, is_staff=True)
        self.object_list = self.user_list + self.staff_list

    def test_permission_access_and_filter(self):
        self.client.login(username=UserFactory().username, password='pass')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)

        self.client.login(username=UserFactory(is_staff=True).username, password='pass')
        resp = self.client.get(self.url)
        self.assertContains(resp, self.staff_list[0].username)
        self.assertNotContains(resp, self.user_list[0].username)

        user = UserFactory(is_staff=True)
        assign_perm('users.can_view_other', user)
        self.client.login(username=user.username, password='pass')
        resp = self.client.get(self.url)
        self.assertContains(resp, self.object_list[0].username)
        self.assertContains(resp, self.object_list[0].username)

    def test_contains_filter(self):
        self.client.login(username=UserFactory(is_staff=True).username, password='pass')
        resp = self.client.get(self.url)
        self.assertIn('filter', resp.context)

    def get_view(self, **kwargs):
        return self.client.get(self.url, data=kwargs).context_data['view']

    def test_get_is_staff_choice(self):
        self.client.login(username=UserFactory(is_staff=True).username, password='pass')
        self.assertEqual(self.get_view().get_is_staff_choice(), 0)  # Default
        self.assertEqual(self.get_view(is_staff='a').get_is_staff_choice(), 0)  # Non-num
        self.assertEqual(self.get_view(is_staff='5').get_is_staff_choice(), 0)  # Too large
        self.assertEqual(self.get_view(is_staff=1).get_is_staff_choice(), 1)  # Correct

    def _test_get_queryset(self, iss, **kwargs):
        qs = self.get_view(**kwargs).get_queryset()
        qs = qs.filter(pk=UserFactory(is_staff=iss).pk)
        return qs.exists()

    def test_get_queryset_is_staff_choice(self):
        self.client.login(username=UserFactory(is_staff=True, is_superuser=True).username,
                          password='pass')
        # 0 - _
        self.assertTrue(self._test_get_queryset(iss=True))
        self.assertTrue(self._test_get_queryset(iss=False))
        # 1 - is_staff=True
        self.assertTrue(self._test_get_queryset(iss=True, is_staff='1'))
        self.assertFalse(self._test_get_queryset(iss=False, is_staff='1'))
        # 2 - is_staff=False
        self.assertTrue(self._test_get_queryset(iss=False, is_staff='2'))
        self.assertFalse(self._test_get_queryset(iss=True, is_staff='2'))

    def test_get_context_data_is_staff(self):
        self.client.login(username=UserFactory(is_staff=True, is_superuser=True).username,
                          password='pass')
        resp = self.client.get(self.url, data={'is_staff': 1})
        context_data = resp.context_data
        self.assertIn('is_staff', context_data)
        self.assertEqual(context_data['is_staff']['selected'], 1)
        self.assertIn('choices', context_data['is_staff'])


class LoginPageTestCase(TestCase):
    url = reverse_lazy('account_login')

    def test_login_page_integrate(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, '<form ')
        self.assertContains(resp, 'login')
        self.assertContains(resp, 'password')
