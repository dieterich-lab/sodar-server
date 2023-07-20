from django.urls import path

import samplesheets.views_ajax
import samplesheets.views_api
from samplesheets import views


app_name = 'samplesheets'

# UI views
urls_ui = [
    path(
        route='<uuid:project>',
        view=views.ProjectSheetsView.as_view(),
        name='project_sheets',
    ),
    path(
        route='import/<uuid:project>',
        view=views.SheetImportView.as_view(),
        name='import',
    ),
    path(
        route='sync/<uuid:project>',
        view=views.SheetRemoteSyncView.as_view(),
        name='sync',
    ),
    path(
        route='template/select/<uuid:project>',
        view=views.SheetTemplateSelectView.as_view(),
        name='template_select',
    ),
    path(
        route='template/create/<uuid:project>',
        view=views.SheetTemplateCreateView.as_view(),
        name='template_create',
    ),
    path(
        route='export/excel/study/<uuid:study>',
        view=views.SheetExcelExportView.as_view(),
        name='export_excel',
    ),
    path(
        route='export/excel/assay/<uuid:assay>',
        view=views.SheetExcelExportView.as_view(),
        name='export_excel',
    ),
    path(
        route='export/isa/<uuid:project>',
        view=views.SheetISAExportView.as_view(),
        name='export_isa',
    ),
    path(
        route='export/version/<uuid:isatab>',
        view=views.SheetISAExportView.as_view(),
        name='export_isa',
    ),
    path(
        route='collections/<uuid:project>',
        view=views.IrodsCollsCreateView.as_view(),
        name='collections',
    ),
    path(
        route='delete/<uuid:project>',
        view=views.SheetDeleteView.as_view(),
        name='delete',
    ),
    path(
        route='cache/update/<uuid:project>',
        view=views.SheetCacheUpdateView.as_view(),
        name='cache_update',
    ),
    path(
        route='versions/<uuid:project>',
        view=views.SheetVersionListView.as_view(),
        name='versions',
    ),
    path(
        route='version/restore/<uuid:isatab>',
        view=views.SheetVersionRestoreView.as_view(),
        name='version_restore',
    ),
    path(
        route='version/compare/<uuid:project>',
        view=views.SheetVersionCompareView.as_view(),
        name='version_compare',
    ),
    path(
        route='version/compare/file/<uuid:project>',
        view=views.SheetVersionCompareFileView.as_view(),
        name='version_compare_file',
    ),
    path(
        route='version/update/<uuid:isatab>',
        view=views.SheetVersionUpdateView.as_view(),
        name='version_update',
    ),
    path(
        route='version/delete/<uuid:isatab>',
        view=views.SheetVersionDeleteView.as_view(),
        name='version_delete',
    ),
    path(
        route='version/delete/batch/<uuid:project>',
        view=views.SheetVersionDeleteBatchView.as_view(),
        name='version_delete_batch',
    ),
    path(
        route='irods/tickets/<uuid:project>',
        view=views.IrodsAccessTicketListView.as_view(),
        name='irods_tickets',
    ),
    path(
        route='irods/ticket/create/<uuid:project>',
        view=views.IrodsAccessTicketCreateView.as_view(),
        name='irods_ticket_create',
    ),
    path(
        route='irods/ticket/update/<uuid:irodsaccessticket>',
        view=views.IrodsAccessTicketUpdateView.as_view(),
        name='irods_ticket_update',
    ),
    path(
        route='irods/ticket/delete/<uuid:irodsaccessticket>',
        view=views.IrodsAccessTicketDeleteView.as_view(),
        name='irods_ticket_delete',
    ),
    path(
        route='irods/requests/<uuid:project>',
        view=views.IrodsDataRequestListView.as_view(),
        name='irods_requests',
    ),
    path(
        route='irods/request/create/<uuid:project>',
        view=views.IrodsRequestCreateView.as_view(),
        name='irods_request_create',
    ),
    path(
        route='irods/request/update/<uuid:irodsdatarequest>',
        view=views.IrodsRequestUpdateView.as_view(),
        name='irods_request_update',
    ),
    path(
        route='irods/request/delete/<uuid:irodsdatarequest>',
        view=views.IrodsRequestDeleteView.as_view(),
        name='irods_request_delete',
    ),
    path(
        route='irods/request/accept/<uuid:irodsdatarequest>',
        view=views.IrodsRequestAcceptView.as_view(),
        name='irods_request_accept',
    ),
    path(
        route='irods/request/accept/batch/<uuid:project>',
        view=views.IrodsRequestAcceptBatchView.as_view(),
        name='irods_request_accept_batch',
    ),
    path(
        route='irods/request/reject/<uuid:irodsdatarequest>',
        view=views.IrodsRequestRejectView.as_view(),
        name='irods_request_reject',
    ),
    path(
        route='irods/request/reject/batch/<uuid:project>',
        view=views.IrodsRequestRejectBatchView.as_view(),
        name='irods_request_reject_batch',
    ),
]

# REST API views
urls_api = [
    path(
        route='api/investigation/retrieve/<uuid:project>',
        view=samplesheets.views_api.InvestigationRetrieveAPIView.as_view(),
        name='api_investigation_retrieve',
    ),
    path(
        route='api/irods/collections/create/<uuid:project>',
        view=samplesheets.views_api.IrodsCollsCreateAPIView.as_view(),
        name='api_irods_colls_create',
    ),
    path(
        route='api/irods/requests/<uuid:project>',
        view=samplesheets.views_api.IrodsDataRequestListAPIView.as_view(),
        name='api_irods_request_list',
    ),
    path(
        route='api/irods/request/create/<uuid:project>',
        view=samplesheets.views_api.IrodsRequestCreateAPIView.as_view(),
        name='api_irods_request_create',
    ),
    path(
        route='api/irods/request/update/<uuid:irodsdatarequest>',
        view=samplesheets.views_api.IrodsRequestUpdateAPIView.as_view(),
        name='api_irods_request_update',
    ),
    path(
        route='api/irods/request/delete/<uuid:irodsdatarequest>',
        view=samplesheets.views_api.IrodsRequestDeleteAPIView.as_view(),
        name='api_irods_request_delete',
    ),
    path(
        route='api/irods/request/accept/<uuid:irodsdatarequest>',
        view=samplesheets.views_api.IrodsRequestAcceptAPIView.as_view(),
        name='api_irods_request_accept',
    ),
    path(
        route='api/irods/request/reject/<uuid:irodsdatarequest>',
        view=samplesheets.views_api.IrodsRequestRejectAPIView.as_view(),
        name='api_irods_request_reject',
    ),
    path(
        route='api/import/<uuid:project>',
        view=samplesheets.views_api.SheetImportAPIView.as_view(),
        name='api_import',
    ),
    path(
        route='api/export/zip/<uuid:project>',
        view=samplesheets.views_api.SheetISAExportAPIView.as_view(),
        name='api_export_zip',
    ),
    path(
        route='api/export/json/<uuid:project>',
        view=samplesheets.views_api.SheetISAExportAPIView.as_view(),
        name='api_export_json',
    ),
    path(
        route='api/file/exists',
        view=samplesheets.views_api.SampleDataFileExistsAPIView.as_view(),
        name='api_file_exists',
    ),
    path(
        route='api/remote/get/<uuid:project>/<str:secret>',
        view=samplesheets.views_api.RemoteSheetGetAPIView.as_view(),
        name='api_remote_get',
    ),
    path(
        route='api/file/list/<uuid:project>',
        view=samplesheets.views_api.ProjectIrodsFileListAPIView.as_view(),
        name='api_file_list',
    ),
]

# Ajax API views
urls_ajax = [
    path(
        route='ajax/context/<uuid:project>',
        view=samplesheets.views_ajax.SheetContextAjaxView.as_view(),
        name='ajax_context',
    ),
    path(
        route='ajax/study/tables/<uuid:study>',
        view=samplesheets.views_ajax.StudyTablesAjaxView.as_view(),
        name='ajax_study_tables',
    ),
    path(
        route='ajax/study/links/<uuid:study>',
        view=samplesheets.views_ajax.StudyLinksAjaxView.as_view(),
        name='ajax_study_links',
    ),
    path(
        route='ajax/warnings/<uuid:project>',
        view=samplesheets.views_ajax.SheetWarningsAjaxView.as_view(),
        name='ajax_warnings',
    ),
    path(
        route='ajax/edit/cell/<uuid:project>',
        view=samplesheets.views_ajax.SheetCellEditAjaxView.as_view(),
        name='ajax_edit_cell',
    ),
    path(
        route='ajax/edit/row/insert/<uuid:project>',
        view=samplesheets.views_ajax.SheetRowInsertAjaxView.as_view(),
        name='ajax_edit_row_insert',
    ),
    path(
        route='ajax/edit/row/delete/<uuid:project>',
        view=samplesheets.views_ajax.SheetRowDeleteAjaxView.as_view(),
        name='ajax_edit_row_delete',
    ),
    path(
        route='ajax/version/save/<uuid:project>',
        view=samplesheets.views_ajax.SheetVersionSaveAjaxView.as_view(),
        name='ajax_version_save',
    ),
    path(
        route='ajax/edit/finish/<uuid:project>',
        view=samplesheets.views_ajax.SheetEditFinishAjaxView.as_view(),
        name='ajax_edit_finish',
    ),
    path(
        route='ajax/config/update/<uuid:project>',
        view=samplesheets.views_ajax.SheetEditConfigAjaxView.as_view(),
        name='ajax_config_update',
    ),
    path(
        route='ajax/display/update/<str:study>',
        view=samplesheets.views_ajax.StudyDisplayConfigAjaxView.as_view(),
        name='ajax_display_update',
    ),
    path(
        route='ajax/irods/request/create/<uuid:project>',
        view=samplesheets.views_ajax.IrodsRequestCreateAjaxView.as_view(),
        name='ajax_irods_request_create',
    ),
    path(
        route='ajax/irods/request/delete/<uuid:project>',
        view=samplesheets.views_ajax.IrodsRequestDeleteAjaxView.as_view(),
        name='ajax_irods_request_delete',
    ),
    path(
        route='ajax/irods/objects/<uuid:project>',
        view=samplesheets.views_ajax.IrodsObjectListAjaxView.as_view(),
        name='ajax_irods_objects',
    ),
    path(
        route='ajax/version/compare/<uuid:project>',
        view=samplesheets.views_ajax.SheetVersionCompareAjaxView.as_view(),
        name='ajax_version_compare',
    ),
]

urlpatterns = urls_ui + urls_api + urls_ajax
