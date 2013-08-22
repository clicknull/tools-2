var MAP = {}

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
                    for (var i = 0 ; i < json.rule.length ; i++) {
                        var row = {}

                        row["id"] = json.rule[i].id;
                        row["0"] = json.rule[i].IDC_name + " - "
                            + json.rule[i].IDC_ip_address_port + " - "
                            + json.rule[i].service_name;
                        row["1"] = json.rule[i].regexp;
                        row["2"] = json.rule[i].dealwith_manner;
                        row["3"] = json.rule[i].parameters;
                        row["4"] = json.rule[i].status;
                        row["5"] = json.rule[i].timestamp;

                        json.aaData.push(row);
                    }
                }
                fnCallback(json);
            }
        })
    }
}

function fnGetPrimaryOptions() {
    var sSource = "/_logcrawler/logcrawler_rest_api/IDC_collect/get/";
    var oPrimary = {};

    $.ajax({
        "dataType": "json",
        "type":     "GET",
        "url":       sSource,
        "async":     false,
        "success":   function (json) {
            json.aaData = [];
            if (json.status == "ok") {
                for (var i = 0 ; i < json.idc_collect.length ; i++) {
                    var key = json.idc_collect[i].IDC_name + " - " +
                        json.idc_collect[i].IDC_ip_address_port + " - " +
                        json.idc_collect[i].service_name;
                    var value = key
                    oPrimary[key] = value;
                }
            }
        }
    })
    return oPrimary;
}

function fnMakeEditable() {
    var oTable = $('#main').dataTable();
    var aPrimaryOptions = fnGetPrimaryOptions();

    var fnOnEditDone = function(value, settings) {
        if (value == this.revert)
            return value;

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

        if (nIndex == 0) {
            aPrimaryOptions['selected'] = $(this).html();

            oSettings['type'] = 'select';
            oSettings['data'] = aPrimaryOptions;
        } else if (nIndex == 1) {
            oSettings['type'] = 'textarea'
        } else if (nIndex == 2) {
            oSettings['type'] = 'select';
            oSettings['data'] = {
                sendtokafka: 'sendtokafka',
                onserver:    'onserver',
                selected: $(this).html()
            };
        } else if (nIndex == 4) {
            oSettings['type'] = 'select';
            oSettings['data'] = {
                active:   'active',
                inactive: 'inactive',
                selected: $(this).html()};
        } else {
            return
        }

        $(this).editable(fnOnEditDone, oSettings);
    })
}

function fnClickAdd() {
    var oTable = $('#main').dataTable();
    var oDefaultData = {}

    oDefaultData[0] = "BeiJing_YiZhuang_CTC_log111_100 - 192.168.111.100:80 - haproxy_access";
    oDefaultData[1] = "*";
    oDefaultData[2] = "sendtokafka";
    oDefaultData[3] = "";
    oDefaultData[4] = "inactive";
    oDefaultData[5] = "";

    fnAddRow(oDefaultData)
}

/* Update idc data by ajax */
function fnUpdateInternalData(oData) {
    $.ajax({
        type:        "post",
        url:         "/_logcrawler/logcrawler_rest_api/analyze_process_rules/update/",
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
        async:       false,
        type:        "post",
        url:         "/_logcrawler/logcrawler_rest_api/analyze_process_rules/create/",
        data:        fnConvertToJson(oData),
        contentType: "application/json; charset=utf-8",
        dataType:    "json",

        beforeSend: function(xmlHttpRequest){
            xmlHttpRequest.setRequestHeader("Authorization",
                "Basic " + btoa("root:root"));  // btoa() --> encodeBase64
        },

        success: function (result) {
            if (result["status"] != "ok")
                alert("更新失败" + result["detail"])
        }
    });
}

function fnVerifyInternalData(oData) {
    $.ajax({
        //"async":       false, 
        "type":        "post",
        "url":         "/_logcrawler/logcrawler_rest_api/regexp_verification/create/",
        "data":        fnConvertToJsonForVerify(oData),
        "contentType": "application/json; charset=utf-8",
        "dataType":    "json",
        "timeout":     5000,
        "error": function (XMLHttpRequest, error, exception) {
            alert("请求失败\n"+ error + exception);
        },

        "success": function (result) {
            if (result["status"] == "ok") {
                setting = {};
                setting['pid'] = result['pid'];
                setting['request_lines'] = 50;
                fnVerifyShow(oData, setting);
            } else {
                alert("创建校验失败\n"+result["detail"]);
            }
        }
    });
}

function fnVerifyShow(oData, setting) {
    var reg = new RegExp("[^a-zA-Z0-9]+","g");
    var timestamp = new Date().getTime();
    var verifyId = oData[0].replace(reg, '-')+"__"+oData[1].replace(reg, '-')+getHashCode(oData[1]+timestamp);
    url = "/_logcrawler/logcrawler_rest_api/regexp_verification/get/?pid=" +setting['pid']+ "&file_offset=0&request_lines=" +setting['request_lines'];

    MAP[verifyId] = [url];

    pre = oData[0]+'&nbsp;|&nbsp;'+oData[1] + '</br>';
    pre += '<a id="'+verifyId+'prev" style="padding-left:0px" href="javascript:void(0);" onclick=\'fnClickVerifyPrev("'+verifyId+'",'+JSON.stringify(setting)+');\'>&lt;-</a>';
    pre += '&nbsp;<font id="' + verifyId + 'curr">' + 0 + '</font>&nbsp;'
    pre += '<a id="'+verifyId+'next" style="padding-left:0px" href="javascript:void(0);" onclick=\'fnClickVerifyNext("'+verifyId+'",'+JSON.stringify(setting)+');\'>-&gt;</a>';
    pre += '</br><pre id="'+verifyId+'"></pre>';

    $('#verification').append(pre);

    //setTimeout('fnClickVerifyNext("' +verifyId+ '",' + JSON.stringify(setting) +')', 2000);
}

function fnClickVerifyPrev(verifyId, setting) {
    pageId = parseInt($('font#'+verifyId+'curr').text());
    pageId -= 1;
    if (pageId < 1) {
        pageId = 1;
    }
    fnClickVerifyFlush(verifyId, setting, pageId);
}

function fnClickVerifyNext(verifyId, setting) {
    pageId = parseInt($('font#'+verifyId+'curr').text());
    pageId += 1;
    fnClickVerifyFlush(verifyId, setting, pageId);
}

function fnClickVerifyFlush(verifyId, setting, pageId) {
    // 在此减少局部变量的使用（当多函数异步调用时可能会引起局部变量值混乱）
    if (pageId >= 1 && pageId <= MAP[verifyId].length - 1) {
        $('#'+verifyId).html(MAP[verifyId][pageId]);
        $('font#'+verifyId+'curr').text(pageId);

    } else if (pageId == MAP[verifyId].length) {
        url = MAP[verifyId].shift();
        response = fnRequestForVerify(url);
        if (response['status'] != 'ok' || response['response_lines'] == 0) {
            MAP[verifyId].unshift(url);
            //alert("获取校验失败\n" + response['detail']);
            $('#'+verifyId).html("<font color=#ff0000>获取校验失败</font></br>" + response['detail']);
            return;
        }
        all_line = '';
        for (id in response['lines']) {
            all_line += response['lines'][id];
        }
        MAP[verifyId].push(all_line);
        $('#'+verifyId).html(all_line);
        $('font#'+verifyId+'curr').text(pageId);

        queries = [];
        queries.push("pid=" + setting['pid']);
        queries.push("file_offset=" + response['current_offset']);
        queries.push("request_lines=" + setting['request_lines']);
        // unshift(next_url)
        MAP[verifyId].unshift("/_logcrawler/logcrawler_rest_api/regexp_verification/get/?"+queries.join("&"));

    } else {
        $('#'+verifyId).html("");
        $('font#'+verifyId+'curr').text(0);
        // $('#'+verifyId).text(MAP[verifyId][1]);
        // $('font#'+verifyId+'curr').text(1);
    }
}

function fnRequestForVerify(url) {
    reponse = {};
    $.ajax({
        "async":     false,
        "dataType": "json",
        "type":     "GET",
        "url":       url,
        "success":   function (result) {
            response = result;
        }
    })
    return response;
}

function fnConvertToJson(oData) {
    var aElements = oData[0].split(' - ', 3);
    var sIDC  = aElements[0]
    var sAddr = aElements[1]
    var sService = aElements[2]

    return JSON.stringify({
        id:                       oData['id'],
        IDC_name:                 sIDC,
        IDC_ip_address_port:      sAddr,
        service_name:             sService,
        regexp:                   oData[1],
        dealwith_manner:          oData[2],
        status:                   oData[4]
    })
}

function fnConvertToJsonForVerify(oData) {
    var aElements = oData[0].split(' - ', 3);
    var sIDC  = aElements[0]
    var sAddr = aElements[1]
    var sService = aElements[2]

    return JSON.stringify({
        IDC_name:                 sIDC,
        IDC_ip_address_port:      sAddr,
        service_name:             sService,
        regexp:                   oData[1]
    })
}

function fnClickVerify() {
    var oTable = $('#main').dataTable();
    MAP = {};
    $('#verification').empty();

    for (i = 0 ; i < anCreateItems.length ; i++) {
        var nIndex = anCreateItems[i];
        var oData = oTable.fnGetData()[nIndex];
        fnVerifyInternalData(oData);
    }

    for (i = 0 ; i < anUpdateItems.length ; i++) {
        var nIndex = anUpdateItems[i];
        var oData = oTable.fnGetData()[nIndex];
        fnVerifyInternalData(oData);
    }
}

function getHashCode(str){
    var hash = 0;
    if (str.length == 0) return hash;
    for (i = 0; i < str.length; i++) {
        char = str.charCodeAt(i);
        hash = ((hash<<5)-hash)+char;
        hash = hash & hash; // Convert to 32bit integer  ( javascript中的int值和java中有区别 )
    }
    return hash;
}

