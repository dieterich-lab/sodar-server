"""Tests for permissions in the projectroles Django app"""

from django.core.urlresolvers import reverse

from test_plus.test import TestCase

from ..models import Role, OMICS_CONSTANTS
from .test_models import ProjectMixin, RoleAssignmentMixin, ProjectInviteMixin

# Omics constants
PROJECT_ROLE_OWNER = OMICS_CONSTANTS['PROJECT_ROLE_OWNER']
PROJECT_ROLE_DELEGATE = OMICS_CONSTANTS['PROJECT_ROLE_DELEGATE']
PROJECT_ROLE_CONTRIBUTOR = OMICS_CONSTANTS['PROJECT_ROLE_CONTRIBUTOR']
PROJECT_ROLE_GUEST = OMICS_CONSTANTS['PROJECT_ROLE_GUEST']
PROJECT_ROLE_STAFF = OMICS_CONSTANTS['PROJECT_ROLE_STAFF']
PROJECT_TYPE_CATEGORY = OMICS_CONSTANTS['PROJECT_TYPE_CATEGORY']
PROJECT_TYPE_PROJECT = OMICS_CONSTANTS['PROJECT_TYPE_PROJECT']


class TestPermissionBase(
        TestCase, ProjectMixin, RoleAssignmentMixin, ProjectInviteMixin):
    """Base class for testing permissions"""

    def setUp(self):
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

        # Superuser
        self.superuser = self.make_user('superuser')
        self.superuser.is_staff = True
        self.superuser.is_superuser = True
        self.superuser.save()

        # No user
        self.anonymous = None

        # Users with role assignments
        self.user_owner = self.make_user('user_owner')
        self.user_delegate = self.make_user('user_delegate')
        self.user_staff = self.make_user('user_staff')
        self.user_contributor = self.make_user('user_contributor')
        self.user_guest = self.make_user('user_guest')

        # User without role assignments
        self.user_no_roles = self.make_user('user_no_roles')

        # Init projects

        # Top level category
        self.category = self._make_project(
            title='TestCategoryTop',
            type=PROJECT_TYPE_CATEGORY,
            parent=None)

        # Subproject under category
        self.project = self._make_project(
            title='TestProjectSub',
            type=PROJECT_TYPE_PROJECT,
            parent=self.category)

        # Init role assignments

        self._make_assignment(
            self.category, self.user_owner, self.role_owner)
        self.as_owner = self._make_assignment(
            self.project, self.user_owner, self.role_owner)
        self.as_delegate = self._make_assignment(
            self.project, self.user_delegate, self.role_delegate)
        self.as_staff = self._make_assignment(
            self.project, self.user_staff, self.role_staff)
        self.as_contributor = self._make_assignment(
            self.project, self.user_contributor, self.role_contributor)
        self.as_guest = self._make_assignment(
            self.project, self.user_guest, self.role_guest)

    def assert_render200_ok(self, url, users):
        """
        Assert successful HTTP request for url with a list of users.
        :param url: Target URL for the request
        :param users: Users to test
        """
        for user in users:
            # Authenticated user
            if user:
                with self.login(user):
                    response = self.client.get(url)

                    self.assertEquals(
                        response.status_code, 200, 'user={}'.format(user))

            # Anonymous
            else:
                response = self.client.get(url)
                self.assertEquals(
                    response.status_code, 200, 'user={}'.format(user))

    def assert_redirect(
            self, url, users, redirect_user=None, redirect_anon=None):
        """
        Assert redirection to an appropriate page if user is not authorized.
        Adapted from flowcelltool.
        :param url: Target URL for the request
        :param users: Users to test
        :param redirect_user: Redirect URL for signed in user (None=default)
        :param redirect_anon: Redirect URL for anonymous (None=default)
        """
        for user in users:
            # Authenticated user
            if user:
                if redirect_user is None:
                    redirect_user = reverse('home')
                with self.login(user):
                    response = self.client.get(url)
                    self.assertRedirects(
                        response, redirect_user,
                        msg_prefix='user={}'.format(user))

            # Anonymous
            else:
                if not redirect_anon:
                    redirect_anon = reverse('account_login') + '?next=' + url
                response = self.client.get(url)
                self.assertRedirects(
                    response, redirect_anon,
                    msg_prefix='user={}'.format(user))


class TestBaseViews(TestPermissionBase):
    """Tests for base views"""

    def test_home(self):
        url = reverse('home')
        good_users = [
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        bad_users = [
            self.anonymous]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_login(self):
        url = reverse('account_login')
        good_users = [
            self.anonymous,
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]

        self.assert_render200_ok(url, good_users)

    def test_logout(self):
        url = reverse('account_logout')
        good_users = [
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_redirect(
            url,
            good_users,
            redirect_user='/login/',
            redirect_anon='/login/')

    def test_about(self):
        url = reverse('about')
        good_users = [
            self.anonymous,
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)

    def test_admin(self):
        url = '/admin/'
        good_users = [
            self.superuser]
        bad_users = [
            self.anonymous,
            self.as_owner.user,
            self.as_delegate.user,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(
            url, bad_users,
            redirect_user='/admin/login/?next=/admin/',
            redirect_anon='/admin/login/?next=/admin/')


class TestProjectViews(TestPermissionBase):
    """Tests for Project views"""

    def test_category_details(self):
        """Test access to category details"""
        url = reverse('project_detail', kwargs={'pk': self.category.pk})
        good_users = [
            self.superuser,
            self.as_owner.user]
        bad_users = [
            self.anonymous,
            self.as_delegate.user,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_project_details(self):
        """Test access to project details"""
        url = reverse('project_detail', kwargs={'pk': self.project.pk})
        good_users = [
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user]
        bad_users = [
            self.anonymous,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_update(self):
        """Test access to project updating"""
        url = reverse('project_update', kwargs={'pk': self.project.pk})
        good_users = [
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user]
        bad_users = [
            self.anonymous,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_create_top(self):
        """Test access to top level project creation"""
        url = reverse('project_create')
        good_users = [
            self.superuser]
        bad_users = [
            self.anonymous,
            self.as_owner.user,
            self.as_delegate.user,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_create_sub(self):
        """Test access to subproject creation"""
        url = reverse('project_create', kwargs={'parent': self.category.pk})
        good_users = [
            self.superuser,
            self.as_owner.user]
        bad_users = [
            self.anonymous,
            self.as_delegate.user,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_roles(self):
        """Test access to role list"""
        url = reverse('project_roles', kwargs={'pk': self.project.pk})
        good_users = [
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user]
        bad_users = [
            self.anonymous,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_role_create(self):
        """Test access to role creation"""
        url = reverse(
            'role_create',
            kwargs={
                'project': self.project.pk})
        good_users = [
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user,
            self.as_staff.user]
        bad_users = [
            self.anonymous,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_role_update(self):
        """Test access to role updating"""
        url = reverse(
            'role_update',
            kwargs={
                'project': self.project.pk,
                'pk': self.as_contributor.pk})
        good_users = [
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user,
            self.as_staff.user]
        bad_users = [
            self.anonymous,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_role_delete(self):
        """Test access to role deletion"""
        url = reverse(
            'role_delete',
            kwargs={
                'project': self.project.pk,
                'pk': self.as_contributor.pk})
        good_users = [
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user,
            self.as_staff.user]
        bad_users = [
            self.anonymous,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_role_update_owner(self):
        """Test access to owner role update: not allowed, should fail"""
        url = reverse(
            'role_update',
            kwargs={
                'project': self.project.pk,
                'pk': self.as_owner.pk})
        bad_users = [
            self.anonymous,
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_redirect(url, bad_users)

    def test_role_delete_owner(self):
        """Test access to owner role deletion: not allowed, should fail"""
        url = reverse(
            'role_delete',
            kwargs={
                'project': self.project.pk,
                'pk': self.as_owner.pk})
        bad_users = [
            self.anonymous,
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_redirect(url, bad_users)

    def test_role_update_delegate(self):
        """Test access to delegate role update"""
        url = reverse(
            'role_update',
            kwargs={
                'project': self.project.pk,
                'pk': self.as_delegate.pk})
        good_users = [
            self.superuser,
            self.as_owner.user]
        bad_users = [
            self.anonymous,
            self.as_delegate.user,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_role_delete_delegate(self):
        """Test access to role deletion for delegate"""
        url = reverse(
            'role_delete',
            kwargs={
                'project': self.project.pk,
                'pk': self.as_delegate.pk})
        good_users = [
            self.superuser,
            self.as_owner.user]
        bad_users = [
            self.anonymous,
            self.as_delegate.user,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_role_invite_create(self):
        """Test access to role invite creation"""
        url = reverse(
            'role_invite_create',
            kwargs={
                'project': self.project.pk})
        good_users = [
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user]
        bad_users = [
            self.anonymous,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_role_invite_list(self):
        """Test access to role invite list"""
        url = reverse(
            'role_invites',
            kwargs={
                'project': self.project.pk})
        good_users = [
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user]
        bad_users = [
            self.anonymous,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_role_invite_resend(self):
        """Test access to role invite resending"""

        # Init invite
        invite = self._make_invite(
            email='test@example.com',
            project=self.project,
            role=self.role_contributor,
            issuer=self.user_owner,
            message='')

        url = reverse(
            'role_invite_resend',
            kwargs={
                'project': self.project.pk,
                'pk': invite.pk})
        good_users = [
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user]
        bad_users = [
            self.anonymous,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_redirect(
            url,
            good_users,
            redirect_user=reverse(
                'role_invites',
                kwargs={'project': self.project.pk}))
        self.assert_redirect(url, bad_users)

    def test_role_invite_revoke(self):
        """Test access to role invite revoking"""

        # Init invite
        invite = self._make_invite(
            email='test@example.com',
            project=self.project,
            role=self.role_contributor,
            issuer=self.user_owner,
            message='')

        url = reverse(
            'role_invite_revoke',
            kwargs={
                'project': self.project.pk,
                'pk': invite.pk})
        good_users = [
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user]
        bad_users = [
            self.anonymous,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)

    def test_settings_update(self):
        """Test access to settings updating"""
        url = reverse(
            'settings_update',
            kwargs={
                'project': self.project.pk})
        good_users = [
            self.superuser,
            self.as_owner.user,
            self.as_delegate.user]
        bad_users = [
            self.anonymous,
            self.as_staff.user,
            self.as_contributor.user,
            self.as_guest.user,
            self.user_no_roles]
        self.assert_render200_ok(url, good_users)
        self.assert_redirect(url, bad_users)