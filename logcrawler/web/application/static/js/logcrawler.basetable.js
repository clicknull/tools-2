var anUpdateItems = []
var anCreateItems = []

/* Init dataTable */
function fnInitDatatable(sAjaxSource, fnInitComplete) {
    var oTable = $('#main').dataTable({
        "bSort":          false,
        "iDisplayLength": 100,
        "aLengthMenu":    [20, 50, 100],
        "sAjaxSource":    sAjaxSource,
        "fnServerData":   fnObjectsToArray(),
        "fnInitComplete": fnInitComplete,
        "bAutoWidth":     false,
        "aoColumnDefs": [
            {
                "sClass": "limit_width_300",
                "aTargets": [5]
            },
            {
                "sClass": "limit_width_600",
                "aTargets": [0]
            },            
        ]
    });
}

/* Onclick for add new configure */
function fnAddRow(oDefaultData) {
    var oTable = $('#main').dataTable();
    var index = oTable.fnGetData().length;

    oTable.fnAddData(oDefaultData);
    fnMakeEditable();

    fnNotifyCreate(index);
}

/* Onclick for save all modifaction */
function fnClickSave() {
    var oTable = $('#main').dataTable();
    var i;
    passwd = prompt("请输入密码", "");
    if ( btoa(passwd) == "bG9nY3Jhd2xlcg==" ) {
        for (i = 0 ; i < anCreateItems.length ; i++) {
            var nIndex = anCreateItems[i];
            var oData = oTable.fnGetData()[nIndex];
            fnCreateInternalData(oData);
        }
        for (i = 0 ; i < anUpdateItems.length ; i++) {
            var nIndex = anUpdateItems[i];
            var oData = oTable.fnGetData()[nIndex];
            fnUpdateInternalData(oData);
        }
        fnUpdateTable();
        fnUpdateComplete();
        fnCreateComplete();
        $('#save').hide();
    } else {
        alert("密码错误！");
    }
}


/* Show save link if item was created */
function fnNotifyCreate(nIndex, sType) {
    if ($.inArray(nIndex, anCreateItems) == -1) {
        anCreateItems.push(nIndex);
    }

    $('#save').show();
}

/* Show save link if item was updated */
function fnNotifyUpdate(nIndex, sType) {
    if ($.inArray(nIndex, anUpdateItems) == -1 && $.inArray(nIndex, anCreateItems) == -1) {
        anUpdateItems.push(nIndex);
    }

    $('#save').show();
}


/* Clear update items buffer */
function fnUpdateComplete() {
    anUpdateItems.length = 0;
}

/* Clear Create items buffer */
function fnCreateComplete() {
    anCreateItems.length = 0;
}

/* Update table content by reloading ajax */
function fnUpdateTable() {
    var oTable = $('#main').dataTable();
    var sAjaxSource = fnGetAjaxSource();

    oTable.fnReloadAjax(sAjaxSource);
}