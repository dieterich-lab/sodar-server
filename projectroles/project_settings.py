"""Helper functions for Project settings"""

from projectroles.models import ProjectSetting, PROJECT_SETTING_TYPES, Project
from projectroles.plugins import ProjectAppPluginPoint


def get_project_setting(project, app_name, setting_name):
    """
    Return setting value for a project and an app.
    :param project: Project object
    :param app_name: App name (string, must correspond to "name" in app plugin)
    :param setting_name: Setting name (string)
    :return: String or None
    """
    return ProjectSetting.objects.get_setting_value(
        project, app_name, setting_name)


def set_project_setting(project, app_name, setting_name, value):
    """
    Set value of an existing project settings variable. Mainly intended for
    testing.
    :param project: Project object
    :param app_name: App name (string, must correspond to "name" in app plugin)
    :param setting_name: Setting name (string)
    :param value: Value to be set
    :return: True if changed, False if not changed
    :raise: ValueError if value is not accepted for setting type
    """
    try:
        setting = ProjectSetting.objects.get(
            project=project, app_plugin__name=app_name, name=setting_name)

        if setting.value == value:
            return False

        validate_project_setting(setting.type, value)
        setting.value = value
        setting.save()
        return True

    except ProjectSetting.DoesNotExist:
        return False


def validate_project_setting(setting_type, setting_value):
    """
    Validate setting value according to its type
    :param setting_type: Setting type
    :param setting_value: Setting value
    :raise: ValueError if setting_type or setting_value is invalid
    """
    if setting_type not in PROJECT_SETTING_TYPES:
        raise ValueError('Invalid setting type')

    if setting_type == 'BOOLEAN' and not isinstance(setting_value, bool):
        raise ValueError('Please enter a valid boolean value')

    if setting_type == 'INTEGER' and not setting_value.isdigit():
        raise ValueError('Please enter a valid integer value')


def save_default_project_settings(project):
    """
    Save default project settings for project.
    :param project: Project in which settings will be saved
    """
    plugins = [p for p in ProjectAppPluginPoint.get_plugins() if p.is_active()]
    project = Project.objects.get(pk=project.pk)

    for plugin in [p for p in plugins if hasattr(p, 'project_settings')]:
        for set_key in plugin.project_settings.keys():
            try:
                ProjectSetting.objects.get(
                    project=project,
                    app_plugin=plugin.get_model(),
                    name=set_key)

            except ProjectSetting.DoesNotExist:
                set_def = plugin.project_settings[set_key]
                setting = ProjectSetting(
                    project=project,
                    app_plugin=plugin.get_model(),
                    name=set_key,
                    type=set_def['type'],
                    value=set_def['default'])
                setting.save()
