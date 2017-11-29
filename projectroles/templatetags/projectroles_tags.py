from django import template
from django.conf import settings
from django.utils import timezone

from ..models import Project, RoleAssignment, OMICS_CONSTANTS, \
    PROJECT_TAG_STARRED
from ..project_tags import get_tag_state


# Settings
HELP_HIGHLIGHT_DAYS = settings.PROJECTROLES_HELP_HIGHLIGHT_DAYS

# Local constants
INDENT_PX = 25

PROJECT_TYPE_DISPLAY = {
    'PROJECT': 'Project',
    'CATEGORY': 'Category'}


register = template.Library()


@register.simple_tag
def get_project_list(user, parent=None):
    """Return flat project list for displaying in templates"""
    project_list = []

    if user.is_superuser:
        project_list = Project.objects.filter(
            parent=parent,
            submit_status='OK').order_by('title')

    elif not user.is_anonymous():
        project_list = [
            p for p in Project.objects.filter(
                parent=parent,
                submit_status='OK').order_by('title')
            if p.has_role(user, include_children=True)]

    def append_projects(project):
        lst = [project]

        for c in project.get_children():
            if (user.is_superuser or
                    c.has_role(user, include_children=True)):
                lst += append_projects(c)

        return lst

    flat_list = []

    for p in project_list:
        flat_list += append_projects(p)

    return flat_list


@register.simple_tag
def get_project_list_indent(project, list_parent):
    """Return indent in pixels for project list"""
    project_depth = project.get_depth()

    if list_parent:
        project_depth -= (list_parent.get_depth() + 1)

    return project_depth * INDENT_PX


@register.simple_tag
def find_projects(search_term, user):
    """Return flat project list based on a search term and user permissions"""
    return [p for p in Project.objects.find(
        search_term, project_type='PROJECT') if
            user.has_perm('projectroles.view_project', p)]


@register.simple_tag
def omics_constant(value):
    """Get value from OMICS_CONSTANTS in settings"""
    return OMICS_CONSTANTS[value] \
        if value in OMICS_CONSTANTS else None


@register.simple_tag
def get_description(project):
    """Return description, truncate if needed"""
    max_len = 128
    ret = project.description[:max_len]

    if len(project.description) > max_len:
        ret += '...'

    return ret


@register.simple_tag
def get_user_role_str(project, user):
    if user.is_superuser:
        return '<span class="text-danger">Superuser</span>'

    try:
        role_as = RoleAssignment.objects.get(project=project, user=user)
        return role_as.role.name.split(' ')[1].capitalize()

    except RoleAssignment.DoesNotExist:
        return '<span class="text-muted">N/A</span>'


@register.simple_tag
def get_link_state(app_urls, url_name, link_names=None):
    """Return "active" if url_name is found in app_plugin.urls. If link_names is
    set, only return "active" if url_name is found in link_names."""
    if url_name in [u.name for u in app_urls]:
        if link_names:
            if not isinstance(link_names, list):
                link_names = [link_names]

            if url_name not in link_names:
                return ''

        return 'active'


@register.simple_tag
def get_project_type_str(project, capitalize=True):
    """Return printable version of the project type"""
    ret = PROJECT_TYPE_DISPLAY[project.type]
    return ret.lower() if not capitalize else ret


@register.simple_tag
def get_star(project, user):
    """Return HTML for project star tag state if it is set"""
    if (user.has_perm('projectroles.view_project', project) and
            get_tag_state(project, user, PROJECT_TAG_STARRED)):
        return '<i class="fa fa-star text-warning omics-tag-starred"></i>'
    return ''


@register.simple_tag
def has_star(project, user):
    """Return True/False for project star tag state"""
    return (
        user.has_perm('projectroles.view_project', project) and
        get_tag_state(project, user, PROJECT_TAG_STARRED))


@register.simple_tag
def get_help_highlight(user):
    """Return classes to highlight navbar help link if user has recently
    signed in"""
    if user.__class__.__name__ == 'User' and not user.is_anonymous:
        delta_days = (timezone.now() - user.date_joined).days

        if delta_days < HELP_HIGHLIGHT_DAYS:
            return 'font-weight-bold text-warning'

    return ''
