"""Tests for models in the projectroles Django app"""

import datetime as dt

from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.utils import timezone

from test_plus.test import TestCase

from ..models import Project, Role, RoleAssignment, ProjectInvite, \
    OMICS_CONSTANTS
from ..utils import save_default_project_settings

# Omics constants
PROJECT_ROLE_OWNER = OMICS_CONSTANTS['PROJECT_ROLE_OWNER']
PROJECT_ROLE_DELEGATE = OMICS_CONSTANTS['PROJECT_ROLE_DELEGATE']
PROJECT_ROLE_CONTRIBUTOR = OMICS_CONSTANTS['PROJECT_ROLE_CONTRIBUTOR']
PROJECT_ROLE_GUEST = OMICS_CONSTANTS['PROJECT_ROLE_GUEST']
PROJECT_ROLE_STAFF = OMICS_CONSTANTS['PROJECT_ROLE_STAFF']
PROJECT_TYPE_CATEGORY = OMICS_CONSTANTS['PROJECT_TYPE_CATEGORY']
PROJECT_TYPE_PROJECT = OMICS_CONSTANTS['PROJECT_TYPE_PROJECT']
SUBMIT_STATUS_OK = OMICS_CONSTANTS['SUBMIT_STATUS_OK']
SUBMIT_STATUS_PENDING = OMICS_CONSTANTS['SUBMIT_STATUS_PENDING']
SUBMIT_STATUS_PENDING_TASKFLOW = OMICS_CONSTANTS['SUBMIT_STATUS_PENDING']


# Settings
INVITE_EXPIRY_DAYS = settings.PROJECTROLES_INVITE_EXPIRY_DAYS


# Local constants
SECRET = 'rsd886hi8276nypuvw066sbvv0rb2a6x'


class ProjectMixin:
    """Helper mixin for Project creation"""

    @classmethod
    def _make_project(cls, title, type, parent, submit_status=SUBMIT_STATUS_OK):
        """Make and save a Project"""
        values = {
            'title': title,
            'type': type,
            'parent': parent,
            'submit_status': submit_status,
            'description': ''}
        project = Project(**values)
        project.save()

        # Save default project settings (only for non-categories)
        if project.type == PROJECT_TYPE_PROJECT:
            save_default_project_settings(project)

        return project


class ProjectInviteMixin:
    """Helper mixin for ProjectInvite creation"""
    @classmethod
    def _make_invite(
            cls, email, project, role, issuer, message, date_expire=None):
        """Make and save a ProjectInvite"""
        values = {
            'email': email,
            'project': project,
            'role': role,
            'issuer': issuer,
            'message': message,
            'date_expire': date_expire if date_expire else (
                timezone.now() + dt.timedelta(days=INVITE_EXPIRY_DAYS)),
            'secret': SECRET,
            'active': True}
        invite = ProjectInvite(**values)
        invite.save()

        return invite


class TestProject(TestCase, ProjectMixin):
    """Tests for model.Project"""

    def setUp(self):
        # Top level category
        self.category_top = self._make_project(
            title='TestCategoryTop',
            type=PROJECT_TYPE_CATEGORY,
            parent=None)
        # Subproject under category_top
        self.project_sub = self._make_project(
            title='TestProjectSub',
            type=PROJECT_TYPE_PROJECT,
            parent=self.category_top)
        # Top level project
        self.project_top = self._make_project(
            title='TestProjectTop',
            type=PROJECT_TYPE_PROJECT,
            parent=None)

    def test_initialization(self):
        expected = {
            'id': self.project_sub.pk,
            'title': 'TestProjectSub',
            'type': PROJECT_TYPE_PROJECT,
            'parent': self.category_top.pk,
            'submit_status': SUBMIT_STATUS_OK,
            'description': ''}
        model_dict = model_to_dict(self.project_sub)
        # HACK: Can't compare markupfields like this. Better solution?
        model_dict.pop('readme', None)
        self.assertEqual(model_dict, expected)

    def test__str__(self):
        expected = 'TestCategoryTop / TestProjectSub'
        self.assertEqual(str(self.project_sub), expected)

    def test__repr__(self):
        expected = "Project('TestProjectSub', 'PROJECT', " \
            "'TestCategoryTop')"
        self.assertEqual(repr(self.project_sub), expected)

    def test_validate_parent(self):
        """Test parent ForeignKey validation: project can't be its own
        parent"""
        with self.assertRaises(ValidationError):
            project_tmp = self.project_top
            project_tmp.parent = project_tmp
            project_tmp.save()


class TestRole(TestCase):

    def setUp(self):
        self.role = Role.objects.get(
            name=PROJECT_ROLE_OWNER)

    def test_initialization(self):
        expected = {
            'id': self.role.pk,
            'name': PROJECT_ROLE_OWNER,
            'description': self.role.description}
        self.assertEquals(model_to_dict(self.role), expected)

    def test__str__(self):
        expected = PROJECT_ROLE_OWNER
        self.assertEqual(str(self.role), expected)

    def test__repr__(self):
        expected = "Role('{}')".format(PROJECT_ROLE_OWNER)
        self.assertEqual(repr(self.role), expected)


class RoleAssignmentMixin:
    """Helper mixin for RoleAssignment creation
    """

    @classmethod
    def _make_assignment(cls, project, user, role):
        """Make and save a RoleAssignment"""
        values = {
            'project': project,
            'user': user,
            'role': role}
        result = RoleAssignment(**values)
        result.save()
        return result


class TestRoleAssignment(TestCase, ProjectMixin, RoleAssignmentMixin):
    """Tests for model.RoleAssignment"""

    def setUp(self):
        # Init projects/categories
        # Top level category
        self.category_top = self._make_project(
            title='TestCategoryTop',
            type=PROJECT_TYPE_CATEGORY,
            parent=None)
        # Subproject under category_top
        self.project_sub = self._make_project(
            title='TestProjectSub',
            type=PROJECT_TYPE_PROJECT,
            parent=self.category_top)
        # Top level project
        self.project_top = self._make_project(
            title='TestProjectTop',
            type=PROJECT_TYPE_PROJECT,
            parent=None)

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
        self.user_alice = self.make_user('alice')
        self.user_bob = self.make_user('bob')
        self.user_carol = self.make_user('carol')
        self.user_dan = self.make_user('dan')
        self.user_erin = self.make_user('erin')
        self.user_frank = self.make_user('frank')

        # Init assignment
        self.assignment_owner = self._make_assignment(
            self.category_top, self.user_alice, self.role_owner)

        self.expected_default = {
            'id': self.assignment_owner.pk,
            'project': self.category_top.pk,
            'user': self.user_alice.pk,
            'role': self.role_owner.pk}

    def test_initialization(self):
        self.assertEqual(
            model_to_dict(self.assignment_owner), self.expected_default)

    def test__str__(self):
        expected = 'TestCategoryTop: {}: alice'.format(PROJECT_ROLE_OWNER)
        self.assertEquals(str(self.assignment_owner), expected)

    def test__repr__(self):
        expected = "RoleAssignment('TestCategoryTop', 'alice', '{}')".format(
            PROJECT_ROLE_OWNER)
        self.assertEquals(repr(self.assignment_owner), expected)

    def test_validate_user(self):
        """Test user role uniqueness validation: can't add more than one
        role for user in project at once"""
        with self.assertRaises(ValidationError):
            self._make_assignment(
                self.category_top, self.user_alice, self.role_contributor)

    def test_validate_owner(self):
        """Test owner uniqueness validation: can't add owner for project if
        one already exists"""
        with self.assertRaises(ValidationError):
            self._make_assignment(
                self.category_top, self.user_bob, self.role_owner)

    def test_validate_delegate(self):
        """Test delegate validation: can't add delegate for project if one
        already exists"""
        self._make_assignment(
            self.project_sub, self.user_bob, self.role_delegate)

        with self.assertRaises(ValidationError):
            self._make_assignment(
                self.project_sub, self.user_carol, self.role_delegate)

    def test_validate_category(self):
        """Test category validation: can't add roles other than owner for
        projects of type CATEGORY"""
        with self.assertRaises(ValidationError):
            self._make_assignment(
                self.category_top, self.user_bob, self.role_contributor)

    # Tests for RoleAssignmentManager

    def test_get_assignment(self):
        """Test get_assignment() results"""
        self.assertEquals(
            model_to_dict(RoleAssignment.objects.get_assignment(
                self.user_alice, self.category_top)), self.expected_default)

    def test_get_project_owner(self):
        """Test get_project_owner() results"""
        self.assertEquals(self.category_top.get_owner().user, self.user_alice)

    def test_get_project_delegate(self):
        """Test get_project_delegate() results"""
        assignment_del = self._make_assignment(
            self.project_top, self.user_carol, self.role_delegate)
        self.assertEquals(
            self.project_top.get_delegate().user, self.user_carol)

    def test_get_project_staff(self):
        """Test get_project_staff() results"""
        assignment_staff = self._make_assignment(
            self.project_top, self.user_dan, self.role_staff)
        self.assertEquals(
            self.project_top.get_staff()[0].user, self.user_dan)

    def test_get_project_members(self):
        """Test get_project_members() results"""
        assignment_c0 = self._make_assignment(
            self.project_top, self.user_erin, self.role_contributor)
        assignment_c1 = self._make_assignment(
            self.project_top, self.user_frank, self.role_contributor)

        expected = [
            {
                'id': assignment_c0.pk,
                'project': self.project_top.pk,
                'user': self.user_erin.pk,
                'role': self.role_contributor.pk
            },
            {
                'id': assignment_c1.pk,
                'project': self.project_top.pk,
                'user': self.user_frank.pk,
                'role': self.role_contributor.pk
            }
        ]

        members = self.project_top.get_members()

        for i in range(0, members.count()):
            self.assertEquals(model_to_dict(members[i]), expected[i])


class TestProjectInvite(
        TestCase, ProjectMixin, RoleAssignmentMixin, ProjectInviteMixin):
    """Tests for model.ProjectInvite"""

    def setUp(self):
        # Init project
        self.project = self._make_project(
            title='TestProject',
            type=PROJECT_TYPE_PROJECT,
            parent=None)

        # Init roles
        self.role_owner = Role.objects.get(
            name=PROJECT_ROLE_OWNER)
        self.role_delegate = Role.objects.get(
            name=PROJECT_ROLE_DELEGATE)
        self.role_staff = Role.objects.get(
            name=PROJECT_ROLE_STAFF)
        self.role_contributor = Role.objects.get(
            name=PROJECT_ROLE_CONTRIBUTOR)

        # Init user & role
        self.user = self.make_user('owner')
        self.owner_as = self._make_assignment(
            self.project, self.user, self.role_owner)

        # Init invite
        self.invite = self._make_invite(
            email='test@example.com',
            project=self.project,
            role=self.role_contributor,
            issuer=self.user,
            message='')

    def test_initialization(self):
        expected = {
            'id': self.invite.pk,
            'email': 'test@example.com',
            'project': self.project.pk,
            'role': self.role_contributor.pk,
            'issuer': self.user.pk,
            'date_expire': self.invite.date_expire,
            'message': '',
            'secret': SECRET,
            'active': True}
        self.assertEqual(model_to_dict(self.invite), expected)

    def test__str__(self):
        expected = 'TestProject: test@example.com (project contributor) ' \
                   '[ACTIVE]'
        self.assertEqual(str(self.invite), expected)

    def test__repr__(self):
        expected = "ProjectInvite('TestProject', 'test@example.com', " \
            "'project contributor', True)"
        self.assertEqual(repr(self.invite), expected)