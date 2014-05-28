
function fnGetQuery() {
    return "?start_timestamp=" + fnGetThreshold($("#select_minutes option:selected").val());
}


function fnGetTableSettings(sAjaxSource) {
    return {
        "aaSorting": [[2, "desc"], [0, "asc"]],
        "iDisplayLength": 20,
        "aLengthMenu": [20, 50, 100],
        "sAjaxSource": sAjaxSource,
        "fnServerData": fnObjectsToArray()
    }
}

function fnObjectsToArray() {
    return function (sSource, aoData, fnCallback) {
        $.ajax({
            "dataType": 'json',
            "type": "GET",
            "url": sSource,
            "data": aoData,
            "success": function (json) {
                json.aaData = [];
                if (json.status == "ok") {
                    for (var i = 0 ; i < json.download.length ; i++) {
                        var row = {}

                        row["DT_RowId"] = "row_" + i;
                        row["0"] = json.download[i].collector_ip_address;
                        row["1"] = json.download[i].url;
                        row["2"] = moment.unix(json.download[i].start_timestamp).format("YYYY-MM-DD HH:mm:ss");

                        if (json.download[i].status == "done") {
                            var size = json.download[i].filesize;
                            var spend = json.download[i].end_timestamp - json.download[i].start_timestamp;
                            var speed = size / spend;
                            var formatSize;

                            if (size > 1024 * 1024) {
                                formatSize = (size / (1024 * 1024)).toFixed(2) + 'MB';
                            } else if (size > 1024) {
                                formatSize = (size / 1024).toFixed(2) + 'KB';
                            } else {
                                formatSize = size + 'B';
                            }

                            if (speed > 1024 * 1024) {
                                speed = (speed / (1024 * 1024)).toFixed(2) + 'MB/s'
                            } else if (speed > 1024) {
                                speed = (speed / 1024).toFixed(2) + 'KB/s'
                            } else {
                                speed = speed + 'B/s'
                            }

                            row["3"] = formatSize;
                            row["4"] = spend < 1 ? (spend * 1000).toFixed(0) + 'ms' : spend.toFixed(2) + 's';
                            row["5"] = speed;
                        } else {
                            row["3"] = null;
                            row["4"] = null;
                            row["5"] = null;
                        }

                        row["6"] = json.download[i].status;
                        row["7"] = json.download[i].description;

                        json.aaData.push(row);
                    }
                }
                fnCallback(json);
            }
        });
    };
}

