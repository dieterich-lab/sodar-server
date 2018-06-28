from django.urls import reverse

from djangoplugins.point import PluginPoint

# Projectroles dependency
from projectroles.plugins import ProjectAppPluginPoint, get_backend_api

# Samplesheets dependency
from samplesheets.io import get_assay_dirs
from samplesheets.models import Assay

from .models import LandingZone
from landingzones.urls import urlpatterns


# Landingzones project app plugin ----------------------------------------------


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    # Properties required by django-plugins ------------------------------

    #: Name (slug-safe, used in URLs)
    name = 'landingzones'

    #: Title (used in templates)
    title = 'Landing Zones'

    #: App URLs (will be included in settings by djangoplugins)
    urls = urlpatterns

    # Properties defined in ProjectAppPluginPoint -----------------------

    #: Project settings definition
    project_settings = {}

    #: FontAwesome icon ID string
    icon = 'database'

    #: Entry point URL ID (must take project omics_uuid as "project" argument)
    entry_point_url_id = 'landingzones:list'

    #: Description string
    description = 'Management of sample data landing zones in iRODS'

    #: Required permission for accessing the app
    app_permission = 'landingzones.view_zones_own'

    #: Enable or disable general search from project title bar
    search_enable = False   # TODO: Enable once implemented

    #: List of search object types for the app
    search_types = [
        'zone',
        'file']

    #: Search results template
    search_template = 'landingzones/_search_results.html'

    #: App card title for the main search page
    search_title = 'Landing Zones and Zone Files'

    #: App card template for the project details page
    details_template = 'landingzones/_details_card.html'

    #: App card title for the project details page
    details_title = 'Landing Zones Overview'

    #: Position in plugin ordering
    plugin_ordering = 20

    '''
    def get_info(self, pk):
        """
        Return app information to be displayed on the project details page
        :param pk: Project ID
        :returns: List of tuples
        """

        project = Project.objects.get(pk=pk)
        sheet = project.sheet if hasattr(project, 'sheet') else None
        zones = LandingZone.objects.filter(
            project=project).exclude(status='MOVED')

        info = []
        info.append(
            ('Zones enabled', True if sheet and sheet.irods_dirs else False))
        info.append((
            'Active zones', zones.count()))

        return info
    '''

    def get_taskflow_sync_data(self):
        """
        Return data for syncing taskflow operations
        :return: List of dicts or None.
        """
        sync_flows = []
        irods_backend = get_backend_api('omics_irods')

        if irods_backend:
            # Only sync flows which are not yet moved
            for zone in LandingZone.objects.all().exclude(status='MOVED'):
                flow = {
                    'flow_name': 'landing_zone_create',
                    'project_uuid': str(zone.project.omics_uuid),
                    'flow_data': {
                        'zone_title': zone.title,
                        'zone_uuid': zone.omics_uuid,
                        'user_name': zone.user.username,
                        'user_uuid': str(zone.user.omics_uuid),
                        'assay_path': irods_backend.get_subdir(
                            zone.assay, landing_zone=True),
                        'description': zone.description,
                        'zone_config': zone.configuration,
                        'dirs': get_assay_dirs(zone.assay)}}
                sync_flows.append(flow)

        return sync_flows

    def get_object_link(self, model_str, uuid):
        """
        Return URL for referring to a object used by the app, along with a
        label to be shown to the user for linking.
        :param model_str: Object class (string)
        :param uuid: omics_uuid of the referred object
        :return: Dict or None if not found
        """
        obj = self.get_object(eval(model_str), uuid)

        if not obj:
            return None

        if obj.__class__ == LandingZone and obj.status != 'MOVED':
            return {
                'url': reverse(
                    'landingzones:list',
                    kwargs={'project': obj.project.omics_uuid}) +
                            '#' + str(obj.omics_uuid),
                'label': obj.title}

        elif obj.__class__ == Assay:
            return {
                'url': reverse(
                    'samplesheets:project_sheets',
                    kwargs={'study': obj.study.omics_uuid}) +
                            '#' + str(obj.omics_uuid),
                'label': obj.get_display_name()}


# Landingzones configuration sub-app plugin ------------------------------------


class LandingZoneConfigPluginPoint(PluginPoint):
    """Plugin point for registering landingzones configuration sub-apps"""

    # Properties required by django-plugins ------------------------------

    #: Name (used in code and as unique idenfitier)
    # TODO: Implement this in your config plugin
    # TODO: Recommended in form of landingzones_config_name
    # name = 'landingzones_config_name'

    #: Title (used in templates)
    # TODO: Implement this in your config plugin
    # title = 'Landing Zones X Config App'

    # Properties defined in LandingZoneConfigPluginPoint ------------------

    #: Configuration name (used to identify plugin by configuration string)
    # TODO: Implement this in your config plugin
    config_name = ''

    #: Configuration display name (to be visible in GUI)
    # TODO: Implement this in your config plugin
    config_display_name = 'BIH Proteomics SMB Server'

    #: Description string
    # TODO: Implement this in your config plugin
    description = 'TODO: Write a description for your config plugin'

    #: Additional zone menu items
    # TODO: Implement this in your config plugin
    menu_items = [{
        'label': '',     # Label to be displayed in menu
        'icon': '',      # Icon name without the fa-* prefix
        'url_name': ''}  # URL name, will receive zone as "landingzone" kwarg
    ]

    #: Required permission for accessing the plugin
    # TODO: Implement this in your config plugin (can be None)
    # TODO: TBD: Do we need this?
    permission = None


def get_zone_config_plugin(zone):
    """
    Return active landing zone configuration plugin
    :param zone: LandingZone object
    :return: LandingZoneConfigPlugin object or None if not found
    """
    if not zone.configuration:
        return None

    try:
        return LandingZoneConfigPluginPoint.get_plugin(
            'landingzones_config_' + zone.configuration)

    except LandingZoneConfigPluginPoint.DoesNotExist:
        return None
