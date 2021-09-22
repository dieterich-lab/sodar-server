"""Tests for Celery tasks for the samplesheets app"""

from django.conf import settings
from django.contrib import auth
from django.urls import reverse

from unittest import skipIf

# Projectroles dependency
from projectroles.app_settings import AppSettingAPI
from projectroles.models import SODAR_CONSTANTS
from projectroles.plugins import get_backend_api
from projectroles.tests.test_views_taskflow import TestTaskflowBase

# Sodarcache dependency
from sodarcache.models import JSONCacheItem

# Appalerts dependency
from appalerts.models import AppAlert

# Timeline dependency
from timeline.models import ProjectEvent

from samplesheets.models import ISATab
from samplesheets.tasks import update_project_cache_task, sheet_sync_task
from samplesheets.tests.test_io import SampleSheetIOMixin, SHEET_DIR
from samplesheets.tests.test_views_taskflow import (
    SampleSheetTaskflowMixin,
    TestSheetRemoteSyncBase,
)


app_settings = AppSettingAPI()
User = auth.get_user_model()


# SODAR constants
PROJECT_ROLE_OWNER = SODAR_CONSTANTS['PROJECT_ROLE_OWNER']
PROJECT_ROLE_DELEGATE = SODAR_CONSTANTS['PROJECT_ROLE_DELEGATE']
PROJECT_ROLE_CONTRIBUTOR = SODAR_CONSTANTS['PROJECT_ROLE_CONTRIBUTOR']
PROJECT_ROLE_GUEST = SODAR_CONSTANTS['PROJECT_ROLE_GUEST']
PROJECT_TYPE_CATEGORY = SODAR_CONSTANTS['PROJECT_TYPE_CATEGORY']
PROJECT_TYPE_PROJECT = SODAR_CONSTANTS['PROJECT_TYPE_PROJECT']
SUBMIT_STATUS_OK = SODAR_CONSTANTS['SUBMIT_STATUS_OK']
SUBMIT_STATUS_PENDING = SODAR_CONSTANTS['SUBMIT_STATUS_PENDING']
SUBMIT_STATUS_PENDING_TASKFLOW = SODAR_CONSTANTS[
    'SUBMIT_STATUS_PENDING_TASKFLOW'
]

# Local constants
APP_NAME = 'samplesheets'
SHEET_PATH = SHEET_DIR + 'i_small.zip'
CACHE_ALERT_MESSAGE = 'Testing'
TASKFLOW_ENABLED = (
    True if 'taskflow' in settings.ENABLED_BACKEND_PLUGINS else False
)
TASKFLOW_SKIP_MSG = 'Taskflow not enabled in settings'
IRODS_BACKEND_ENABLED = (
    True if 'omics_irods' in settings.ENABLED_BACKEND_PLUGINS else False
)
IRODS_BACKEND_SKIP_MSG = 'iRODS backend not enabled in settings'


@skipIf(not IRODS_BACKEND_ENABLED, IRODS_BACKEND_SKIP_MSG)
class TestUpdateProjectCacheTask(
    SampleSheetIOMixin, SampleSheetTaskflowMixin, TestTaskflowBase
):
    """Tests for project cache update task"""

    def setUp(self):
        super().setUp()
        self.project, self.owner_as = self._make_project_taskflow(
            title='TestProject',
            type=PROJECT_TYPE_PROJECT,
            parent=self.category,
            owner=self.user,
            description='description',
        )
        self.investigation = self._import_isa_from_file(
            SHEET_PATH, self.project
        )
        self.study = self.investigation.studies.first()
        self.assay = self.study.assays.first()
        self.app_alerts = get_backend_api('appalerts_backend')
        self._make_irods_colls(self.investigation)

    def test_update_cache(self):
        """Test cache update"""
        self.assertEqual(
            JSONCacheItem.objects.filter(project=self.project).count(), 0
        )
        self.assertEqual(AppAlert.objects.all().count(), 1)
        self.assertEqual(ProjectEvent.objects.all().count(), 1)

        update_project_cache_task(
            self.project.sodar_uuid,
            self.user.sodar_uuid,
            add_alert=True,
            alert_msg=CACHE_ALERT_MESSAGE,
        )

        self.assertEqual(
            JSONCacheItem.objects.filter(project=self.project).count(), 1
        )
        cache_item = JSONCacheItem.objects.first()
        self.assertEqual(
            cache_item.name,
            'irods/shortcuts/assay/{}'.format(self.assay.sodar_uuid),
        )
        expected_data = {
            'shortcuts': {
                'misc_files': False,
                'track_hubs': [],
                'results_reports': False,
            }
        }
        self.assertEqual(cache_item.data, expected_data)
        self.assertEqual(AppAlert.objects.all().count(), 2)
        alert = AppAlert.objects.order_by('-pk').first()
        self.assertTrue(alert.message.endswith(CACHE_ALERT_MESSAGE))
        self.assertEqual(ProjectEvent.objects.all().count(), 2)

    def test_update_cache_no_alert(self):
        """Test cache update with app alert disabled"""
        self.assertEqual(
            JSONCacheItem.objects.filter(project=self.project).count(), 0
        )
        self.assertEqual(AppAlert.objects.all().count(), 1)
        self.assertEqual(ProjectEvent.objects.all().count(), 1)

        update_project_cache_task(
            self.project.sodar_uuid, self.user.sodar_uuid, add_alert=False
        )

        self.assertEqual(
            JSONCacheItem.objects.filter(project=self.project).count(), 1
        )
        self.assertEqual(AppAlert.objects.all().count(), 1)
        self.assertEqual(ProjectEvent.objects.all().count(), 2)

    def test_update_cache_no_user(self):
        """Test cache update with no user"""
        self.assertEqual(
            JSONCacheItem.objects.filter(project=self.project).count(), 0
        )
        self.assertEqual(AppAlert.objects.all().count(), 1)
        self.assertEqual(ProjectEvent.objects.all().count(), 1)

        update_project_cache_task(self.project.sodar_uuid, None, add_alert=True)

        self.assertEqual(
            JSONCacheItem.objects.filter(project=self.project).count(), 1
        )
        self.assertEqual(AppAlert.objects.all().count(), 1)
        self.assertEqual(ProjectEvent.objects.all().count(), 2)


# NOTE: TestSheetSyncBase moved to test_views_taskflow due to circular import


@skipIf(not TASKFLOW_ENABLED, TASKFLOW_SKIP_MSG)
class TestSheetRemoteSyncTask(TestSheetRemoteSyncBase):
    """Tests for periodic sample sheet sync task"""

    def test_sync_task(self):
        """Test sync sheet"""
        # Perform sync
        sheet_sync_task(self.user.username)

        # Check if target synced correctly
        self.assertEqual(self.project_source.investigations.count(), 1)
        self.assertEqual(
            self.project_source.investigations.first().studies.count(), 1
        )
        self.assertEqual(
            self.project_source.investigations.first()
            .studies.first()
            .assays.count(),
            1,
        )
        self.assertEqual(self.project_target.investigations.count(), 1)
        self.assertEqual(
            self.project_target.investigations.first().studies.count(), 1
        )
        self.assertEqual(
            self.project_target.investigations.first()
            .studies.first()
            .assays.count(),
            1,
        )
        self.assertEqual(ISATab.objects.count(), 2)

        data_target = ISATab.objects.get(
            investigation_uuid=self.project_target.investigations.first().sodar_uuid
        ).data
        data_source = ISATab.objects.get(
            investigation_uuid=self.inv_source.sodar_uuid
        ).data

        self.assertEqual(data_target, data_source)

    def test_sync_existing_source_newer(self):
        """Test sync sheet with existing sheet and changes in source sheet"""
        # Create investigation for target project
        self._import_isa_from_file(SHEET_PATH, self.project_target)

        # Update source investigation
        material = self.inv_source.studies.first().materials.get(
            unique_name=f'{self.p_id_source}-s0-source-0817'
        )
        material.characteristics['age']['value'] = '200'
        material.save()
        self.inv_source.save()

        # Check if both projects have an investigation
        self.assertEqual(self.project_source.investigations.count(), 1)
        self.assertEqual(self.project_target.investigations.count(), 1)
        self.assertEqual(ISATab.objects.count(), 2)
        self.assertEqual(
            self.project_source.investigations.first()
            .studies.first()
            .materials.get(unique_name=f'{self.p_id_source}-s0-source-0817')
            .characteristics['age']['value'],
            '200',
        )
        self.assertEqual(
            self.project_target.investigations.first()
            .studies.first()
            .materials.get(unique_name=f'{self.p_id_target}-s0-source-0817')
            .characteristics['age']['value'],
            '150',
        )

        # Do the sync
        sheet_sync_task(self.user.username)

        # Check if sync was performed correctly
        self.assertEqual(self.project_source.investigations.count(), 1)
        self.assertEqual(self.project_target.investigations.count(), 1)
        self.assertEqual(ISATab.objects.count(), 3)
        self.assertEqual(
            self.project_source.investigations.first()
            .studies.first()
            .materials.get(unique_name=f'{self.p_id_source}-s0-source-0817')
            .characteristics['age']['value'],
            '200',
        )
        self.assertEqual(
            self.project_target.investigations.first()
            .studies.first()
            .materials.get(unique_name=f'{self.p_id_target}-s0-source-0817')
            .characteristics['age']['value'],
            '200',
        )

    def test_sync_existing_target_newer(self):
        """Test sync sheet with existing sheet and changes in target sheet"""
        # Create investigation for target project
        inv_target = self._import_isa_from_file(SHEET_PATH, self.project_target)
        material = inv_target.studies.first().materials.get(
            unique_name=f'{self.p_id_target}-s0-source-0817'
        )
        material.characteristics['age']['value'] = '300'
        material.save()
        inv_target.save()
        target_date_modified = inv_target.date_modified

        # Check if both projects have an investigation
        self.assertEqual(self.project_source.investigations.count(), 1)
        self.assertEqual(self.project_target.investigations.count(), 1)
        self.assertEqual(ISATab.objects.count(), 2)

        # Do the sync
        sheet_sync_task(self.user.username)

        # Check if sync was not performed
        self.assertEqual(self.project_source.investigations.count(), 1)
        self.assertEqual(self.project_target.investigations.count(), 1)
        self.assertEqual(ISATab.objects.count(), 2)
        self.assertEqual(
            self.project_target.investigations.first().date_modified,
            target_date_modified,
        )
        self.assertEqual(
            self.project_source.investigations.first()
            .studies.first()
            .materials.get(unique_name=f'{self.p_id_source}-s0-source-0817')
            .characteristics['age']['value'],
            '150',
        )
        self.assertEqual(
            self.project_target.investigations.first()
            .studies.first()
            .materials.get(unique_name=f'{self.p_id_target}-s0-source-0817')
            .characteristics['age']['value'],
            '300',
        )

    def test_sync_wrong_token(self):
        """Test sync sheet with wrong token"""
        app_settings.set_app_setting(
            APP_NAME,
            'sheet_sync_token',
            'WRONGTOKEN',
            project=self.project_target,
        )
        # Perform sync
        sheet_sync_task(self.user.username)
        # Check if target synced correctly
        self.assertEqual(self.project_target.investigations.count(), 0)

    def test_sync_enabled_missing_token(self):
        """Test sync sheet with missing token"""
        app_settings.set_app_setting(
            APP_NAME,
            'sheet_sync_token',
            '',
            project=self.project_target,
        )
        # Perform sync
        sheet_sync_task(self.user.username)
        # Check if target synced correctly
        self.assertEqual(self.project_target.investigations.count(), 0)

    def test_sync_enabled_wrong_url(self):
        """Test sync sheet with wrong url"""
        app_settings.set_app_setting(
            APP_NAME,
            'sheet_sync_url',
            'https://qazxdfjajsrd.com',
            project=self.project_target,
        )
        # Perform sync
        sheet_sync_task(self.user.username)
        # Check if target synced correctly
        self.assertEqual(self.project_target.investigations.count(), 0)

    def test_sync_enabled_url_to_nonexisting_sheet(self):
        """Test sync sheet with url to nonexisting sheet"""
        app_settings.set_app_setting(
            APP_NAME,
            'sheet_sync_url',
            self.live_server_url
            + reverse(
                'samplesheets:api_export_json',
                kwargs={'project': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'},
            ),
            project=self.project_target,
        )
        # Perform sync
        sheet_sync_task(self.user.username)
        # Check if target synced correctly
        self.assertEqual(self.project_target.investigations.count(), 0)

    def test_sync_enabled_missing_url(self):
        """Test sync sheet with missing url"""
        app_settings.set_app_setting(
            APP_NAME,
            'sheet_sync_url',
            '',
            project=self.project_target,
        )
        # Perform sync
        sheet_sync_task(self.user.username)
        # Check if target synced correctly
        self.assertEqual(self.project_target.investigations.count(), 0)

    def test_sync_disabled(self):
        """Test sync sheet disabled"""
        app_settings.set_app_setting(
            APP_NAME,
            'sheet_sync_enable',
            False,
            project=self.project_target,
        )
        # Perform sync
        sheet_sync_task(self.user.username)
        # Check if target synced correctly
        self.assertEqual(self.project_target.investigations.count(), 0)
