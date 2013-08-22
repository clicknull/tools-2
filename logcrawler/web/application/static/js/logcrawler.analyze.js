
function fnGetQuery() {
    return "?start_timestamp=" + fnGetThreshold($("#select_minutes option:selected").val());
}


function fnGetTableSettings(sAjaxSource) {
    return {
        "aaSorting":      [],
        "iDisplayLength": 20,
        "aLengthMenu":    [20, 50, 100],
        "sAjaxSource":    sAjaxSource,
        "fnServerData":   fnObjectsToArray(),
        "aoColumnDefs":   [
            {
                "sClass": "limit_width_600",
                "aTargets": [1]
            },
            {
                "sClass": "limit_width_300",
                "aTargets": [6]
            }
        ]
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
                    for (var i = 0 ; i < json.analyze.length ; i++) {
                        var row = {}

                        row["0"] = json.analyze[i].collector_ip_address;
                        row["1"] = json.analyze[i].path;
                        row["2"] = json.analyze[i].filelines;
                        
                        var size = json.analyze[i].filesize;
                        if (size > 1024 * 1024) {
                            size = (size / (1024 * 1024)).toFixed(2) + 'MB';
                        } else if (size > 1024) {
                            size = (size / 1024).toFixed(2) + 'KB';
                        } else {
                            size = size + 'B';
                        }
                        row["3"] = size;

                        row["4"] = moment.unix(json.analyze[i].start_timestamp).format("YYYY-MM-DD HH:mm:ss");
                        row["5"] = moment.unix(json.analyze[i].end_timestamp).format("YYYY-MM-DD HH:mm:ss");

                        var spend = json.analyze[i].end_timestamp - json.analyze[i].start_timestamp;
                        row["6"] = spend.toFixed(2) + 's';

                        row["7"] = json.analyze[i].status;
                        row["8"] = json.analyze[i].description;

                        json.aaData.push(row);
                    }
                }
                fnCallback(json);
            }
        });
    };
}

