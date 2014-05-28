
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
                    for (var i = 0 ; i < json.idc_collect.length ; i++) {
                        var row = {}

                        row["id"] = json.idc_collect[i].id;
                        row["0"] = json.idc_collect[i].IDC_name;
                        row["1"] = json.idc_collect[i].IDC_ip_address_port;
                        row["2"] = json.idc_collect[i].description;
                        row["3"] = json.idc_collect[i].service_name;
                        row["4"] = json.idc_collect[i].collect_interval_minutes;
                        row["5"] = json.idc_collect[i].delay_minutes;
                        row["6"] = json.idc_collect[i].max_delay_minutes;
                        row["7"] = json.idc_collect[i].status;
                        row["8"] = json.idc_collect[i].current_status;
                        row["9"] = json.idc_collect[i].timestamp;

                        json.aaData.push(row);
                    }
                }
                fnCallback(json);
            }
        })
    }
}

function fnMakeEditable() {
    var oTable = $('#main').dataTable();

    var fnOnEditDone = function(value, settings) {
        if (value == this.revert)
            return value;

        if ($.isNumeric(value))
            value = parseInt(value);

        var nTdIndex = $(this).index();
        var nTrIndex = $(this).parent().index();
        var oTrData = oTable.fnGetData()[nTrIndex];

        oTrData[nTdIndex] = value;
        fnNotifyUpdate(nTrIndex);

        return value;
    }

    var fnOnSelectDone = function(value, settings) {
        return fnOnEditDone(value, settings);
    }

    oTable.$('td').each(function() {
        var nIndex = $(this).index()        
        var oSettings = {
            onblur:   'submit',
            event:    'dblclick',
            tooltip:  '双击编辑'
        }
        
        if (nIndex < 4) {
            oSettings['type'] = 'textarea';
        } else if (nIndex < 7) {
            // pass
        } else if (nIndex == 7) {
            oSettings['type'] = 'select';
            oSettings['data'] = {
                active:   'active',
                inactive: 'inactive',
                selected: $(this).html()};
        } else if (nIndex == 8) {
            oSettings['type'] = 'select';
            oSettings['data'] = {
                online:   'online',
                offline:  'offline',
                selected: $(this).html()};
        } else {
            return
        }

        $(this).editable(fnOnEditDone, oSettings)
    })
}

function fnClickAdd() {
    var oDefaultData = {}

    oDefaultData[0] = "localhost";
    oDefaultData[1] = "127.0.0.1";
    oDefaultData[2] = "";
    oDefaultData[3] = "haproxy_access";
    oDefaultData[4] = "0";
    oDefaultData[5] = "0";
    oDefaultData[6] = "0";
    oDefaultData[7] = "inactive";
    oDefaultData[8] = "offline";
    oDefaultData[9] = "";
    
    fnAddRow(oDefaultData)
}

/* Update idc data by ajax */
function fnUpdateInternalData(oData) {
    $.ajax({
        type:        "post",
        url:         "/_logcrawler/logcrawler_rest_api/IDC_collect/update/",
        data:        fnConvertToJson(oData),
        contentType: "application/json; charset=utf-8",
        dataType:    "json",

        beforeSend: function(xmlHttpRequest){
            xmlHttpRequest.setRequestHeader("Authorization",
                "Basic " + btoa("root:root"));  // btoa() --> encodeBase64
        },

        success: function (result) {
            if (result["status"] != "ok")
                alert("更新失败:" + result["detail"])
        }
    });
}

/* Create idc data by ajax */
function fnCreateInternalData(oData) {
    $.ajax({
        type:        "post",
        url:         "/_logcrawler/logcrawler_rest_api/IDC_collect/create/",
        data:        fnConvertToJson(oData),
        contentType: "application/json; charset=utf-8",
        dataType:    "json",

        beforeSend: function(xmlHttpRequest){
            xmlHttpRequest.setRequestHeader("Authorization",
                "Basic " + btoa("root:root"));  // btoa() --> encodeBase64
        },

        success: function (result) {
            if (result["status"] != "ok")
                alert("更新失败:" + result["detail"])
        }
    });
}


function fnConvertToJson(oData) {
    return JSON.stringify({
        id:                       oData['id'],
        IDC_name:                 oData[0],
        IDC_ip_address_port:      oData[1],
        description:              oData[2],
        service_name:             oData[3],
        collect_interval_minutes: oData[4],
        delay_minutes:            oData[5],
        max_delay_minutes:        oData[6],
        status:                   oData[7],
        current_status:           oData[8]
    })
}

