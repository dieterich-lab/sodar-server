"""Tests for email sending in the projectroles Django app"""

from django.conf import settings
from django.core import mail
from django.urls import reverse

from test_plus.test import TestCase, RequestFactory

from ..models import Role, OMICS_CONSTANTS
from ..email import send_role_change_mail
from .test_models import ProjectMixin, RoleAssignmentMixin


# Omics constants
PROJECT_ROLE_OWNER = OMICS_CONSTANTS['PROJECT_ROLE_OWNER']
PROJECT_ROLE_DELEGATE = OMICS_CONSTANTS['PROJECT_ROLE_DELEGATE']
PROJECT_ROLE_CONTRIBUTOR = OMICS_CONSTANTS['PROJECT_ROLE_CONTRIBUTOR']
PROJECT_ROLE_GUEST = OMICS_CONSTANTS['PROJECT_ROLE_GUEST']
PROJECT_ROLE_STAFF = OMICS_CONSTANTS['PROJECT_ROLE_STAFF']
PROJECT_TYPE_CATEGORY = OMICS_CONSTANTS['PROJECT_TYPE_CATEGORY']
PROJECT_TYPE_PROJECT = OMICS_CONSTANTS['PROJECT_TYPE_PROJECT']


class TestEmailSending(TestCase, ProjectMixin, RoleAssignmentMixin):
    def setUp(self):
        self.factory = RequestFactory()

        # Init roles
        self.role_owner = Role.objects.get_or_create(
            name=PROJECT_ROLE_OWNER)[0]
        self.role_delegate = Role.objects.get_or_create(
            name=PROJECT_ROLE_DELEGATE)[0]
        self.role_staff = Role.objects.get_or_create(
            name=PROJECT_ROLE_STAFF)[0]
        self.role_contributor = Role.objects.get_or_create(
            name=PROJECT_ROLE_CONTRIBUTOR)[0]
        self.role_guest = Role.objects.get_or_create(
            name=PROJECT_ROLE_GUEST)[0]

        # Init users
        self.user_owner = self.make_user('owner')

        # Init project
        self.project = self._make_project(
            'top_project', PROJECT_TYPE_PROJECT, None)

        # Assign owner role
        self.owner_as = self._make_assignment(
            self.project, self.user_owner, self.role_owner)

    def test_role_create_mail(self):
        """Test role creation mail sending"""
        with self.login(self.user_owner):
            request = self.factory.get(reverse('home'))
            request.user = self.user_owner
            email_sent = send_role_change_mail(
                change_type='create',
                project=self.owner_as.project,
                user=self.owner_as.user,
                role=self.owner_as.role,
                request=request)
            self.assertEquals(email_sent, 1)
            self.assertEquals(len(mail.outbox), 1)

    def test_role_update_mail(self):
        """Test role updating mail sending"""
        with self.login(self.user_owner):
            request = self.factory.get(reverse('home'))
            request.user = self.user_owner
            email_sent = send_role_change_mail(
                change_type='update',
                project=self.owner_as.project,
                user=self.owner_as.user,
                role=self.owner_as.role,
                request=request)
            self.assertEquals(email_sent, 1)
            self.assertEquals(len(mail.outbox), 1)

    def test_role_delete_mail(self):
        """Test role deletion mail sending"""
        with self.login(self.user_owner):
            request = self.factory.get(reverse('home'))
            request.user = self.user_owner
            email_sent = send_role_change_mail(
                change_type='delete',
                project=self.owner_as.project,
                user=self.owner_as.user,
                role=None,
                request=request)
            self.assertEquals(email_sent, 1)
            self.assertEquals(len(mail.outbox), 1)