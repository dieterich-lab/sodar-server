from django import template

from ..models import Investigation
from ..rendering import get_study_table as r_get_study_table, \
    get_assay_table as r_get_assay_table, \
    render_cell as r_render_cell, \
    render_top_header as r_render_top_header, \
    render_header as r_render_header


register = template.Library()


@register.simple_tag
def get_investigation(project):
    """Return Investigation for a project"""
    try:
        return Investigation.objects.get(project=project)

    except Investigation.DoesNotExist:
        return None


@register.simple_tag
def get_study_table(study):
    """Return data grid for an HTML study table"""
    return r_get_study_table(study)


@register.simple_tag
def get_assay_table(assay):
    """Return data grid for an HTML assay table"""
    return r_get_assay_table(assay)


@register.simple_tag
def render_cell(cell):
    """Return assay table cell as HTML"""
    return r_render_cell(cell)


@register.simple_tag
def render_top_header(section):
    """Render section of top header"""
    return r_render_top_header(section)


@register.simple_tag
def render_header(header):
    """Render section of top header"""
    return r_render_header(header)


@register.simple_tag
def get_study_title(study):
    """Return printable study title"""
    return study.title if study.title else study.file_name.split('.')[0]


@register.simple_tag
def get_assay_title(assay):
    """Return printable assy title"""
    # TODO: How to construct assay title?
    return assay.file_name.split('.')[0]
