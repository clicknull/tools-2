function fnGetThreshold(range) {
    var sThreshold = moment().subtract('minutes', range);
    return sThreshold.unix();
}

function fnToggleAutoload() {
    $('#check').click(function() {
        var $this = $(this);
        if ($this.is(':checked')) {
            bAutoloadFlag = true;
            $('label[for=check]').text("Autoload enabled");
        } else {
            bAutoloadFlag = false;
            $('label[for=check]').text("Autoload disabled");
        }
    });
}


