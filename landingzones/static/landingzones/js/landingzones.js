/*****************************
 Zone status updating function
 *****************************/
var updateZoneStatus = function() {
    $('.sodar-lz-zone-tr-existing').each(function(){
        var trId = $(this).attr('id');
        var zoneTr = $('#' + trId);
        var zoneUuid = $(this).attr('zone-uuid');
        var sampleUrl = $(this).attr('sample-url');
        var statusTd = zoneTr.find('td#sodar-lz-zone-status-' + zoneUuid);

        if (statusTd.text() !== 'MOVED' && statusTd.text() !== 'DELETED') {
            $.ajax({
                url: $(this).attr('status-url'),
                method: 'GET',
                dataType: 'json'
            }).done(function (data) {
                // console.log(trId + ': ' + data['status']);  // DEBUG
                var statusInfoSpan = zoneTr.find('span#sodar-lz-zone-status-info-' + zoneUuid);

                // TODO: Should somehow get these from STATUS_STYLES instead
                var statusStyles = {
                    'CREATING': 'bg-warning',
                    'NOT CREATED': 'bg-danger',
                    'ACTIVE': 'bg-info',
                    'PREPARING': 'bg-warning',
                    'VALIDATING': 'bg-warning',
                    'MOVING': 'bg-warning',
                    'MOVED': 'bg-success',
                    'FAILED': 'bg-danger',
                    'DELETING': 'bg-warning',
                    'DELETED': 'bg-secondary'
                };

                if (statusTd.text() !== data['status'] ||
                        statusInfoSpan.text() !== data['status_info']) {
                    statusTd.text(data['status']);
                    statusTd.removeClass();
                    statusTd.addClass(statusStyles[data['status']] + ' text-white');
                    statusInfoSpan.text(data['status_info']);

                    if (data['status'] === 'MOVED' || data['status'] === 'DELETED') {
                        zoneTr.find('p#sodar-lz-zone-stats-container-' + zoneUuid).hide();

                        if (data['status'] === 'MOVED') {
                            var statusMovedSpan = zoneTr.find(
                                'span#sodar-lz-zone-status-moved-' + zoneUuid);
                            statusMovedSpan.html(
                                '<p class="mb-0"><a href="' + sampleUrl + '">' +
                                '<i class="iconify" data-icon="mdi:arrow-right-circle"></i> ' +
                                'Browse files in sample sheet</a></p>');
                        }
                    }

                    // Button modification
                    if (data['status'] !== 'ACTIVE' && data['status'] !== 'FAILED') {
                        zoneTr.find('td.sodar-lz-zone-title').addClass('text-muted');
                        zoneTr.find('td.sodar-lz-zone-assay').addClass('text-muted');
                        zoneTr.find('td.sodar-lz-zone-status-info').addClass('text-muted');

                        zoneTr.find('.btn').each(function() {
                           if ($(this).is('button')) {
                               $(this).attr('disabled', 'disabled');
                           }

                           else if ($(this).is('a')) {
                               $(this).addClass('disabled');
                           }

                           $(this).tooltip('disable');
                        });

                        zoneTr.find('.sodar-list-dropdown').addClass('disabled');
                    }

                    else {
                        zoneTr.find('td.sodar-lz-zone-title').removeClass('text-muted');
                        zoneTr.find('td.sodar-lz-zone-assay').removeClass('text-muted');
                        zoneTr.find('td.sodar-lz-zone-status-info').removeClass('text-muted');
                        zoneTr.find('p#sodar-lz-zone-stats-container-' + zoneUuid).show();

                        zoneTr.find('.btn').each(function() {
                            if ($(this).is('button')) {
                                $(this).removeAttr('disabled');
                            }

                            $(this).removeClass('disabled');

                           $(this).tooltip('enable');
                        });

                        zoneTr.find('.sodar-list-dropdown').removeClass('disabled');
                    }
                }
            });
        }
    });
};

$(document).ready(function() {
    /******************
     Update zone status
     ******************/
    updateZoneStatus();
    var statusInterval = window.statusInterval;

    // Poll and update active zones
    setInterval(function () {
        updateZoneStatus();
    }, statusInterval);

    // Set up zone UUID copy button
    new ClipboardJS('.sodar-lz-zone-btn-copy');
});
