$(function(){
    var successMsg = function(msg) {
        $("article[role='main']").prepend(
            '<div class="alert alert-success alert-dismissible" role="alert">' +
            '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
            '<span aria-hidden="true">&times;</span></button>' + msg + '</div>'
        );
    };

    var ajaxSelect2Array = function(value) {
        var tmp = value.split("|");
        tmp = tmp.filter(function(x){
            return (x !== (undefined || null || ""));
        });

        return (tmp.length > 0) ? tmp.map(Number) : null;
    };

    $.ajaxSetup({
        headers: {"X-CSRFToken": Cookies.get("csrftoken")},  // FIXME setting
        url: "/api/v1/token/computers/" + $("input#computer-id").val() + "/",
        error: function( jqXHR, textStatus, errorThrown ) {
            if (jqXHR.status === 0) {
                console.log("Not connect: Verify Network.");
            } else if (jqXHR.status === 404) {
                console.log("Requested page not found [404]");
            } else if (jqXHR.status === 500) {
                console.log("Internal Server Error [500].");
            } else if (textStatus === "parsererror") {
                console.log("Requested JSON parse failed.");
            } else if (textStatus === "timeout") {
                console.log("Time out error.");
            } else if (textStatus === "abort") {
                console.log("Ajax request aborted.");
            } else {
                console.log("Uncaught Error: " + jqXHR.responseText);
            }
        }
    });

    $("#update-name").on("click", function() {
        $(this).prop("disabled", true);
        $.ajax({
            type: "PATCH",
            data: {
                name: $("#id_name").val()
            },
            dataType: "json",
            success: (result) => {
                $("#id_name").val(result.name);
                successMsg(gettext("Name has been changed!"));
            }
        });
        $(this).prop("disabled", false);
    });

    $("#update-last-hardware-capture").on("click", function() {
        $(this).prop("disabled", true);
        $.ajax({
            type: "PATCH",
            data: {
                last_hardware_capture: $("input#id_last_hardware_capture").val()
            },
            dataType: "json",
            success: (result) => {
                successMsg(gettext("Last hardware capture has been changed!"));
            }
        });
        $(this).prop("disabled", false);
    });

    $("#update-current-situation").on("click", function() {
        $(this).prop("disabled", true);
        $.ajax({
            type: "PATCH",
            data: {
                status: $("#id_status").val(),
                comment: $("#id_comment").val(),
                tags: ajaxSelect2Array($("#id_tags").val())
            },
            dataType: "json",
            traditional: true,
            success: (result) => {
                successMsg(gettext("Current Situation has been changed!"));
            }
        });
        $(this).prop("disabled", false);
    });

    $("#update-devices").on("click", function() {
        $(this).prop("disabled", true);
        $.ajax({
            type: "PATCH",
            data: {
                default_logical_device: $("#id_default_logical_device").val(),
                assigned_logical_devices_to_cid: $("#id_assigned_logical_devices_to_cid").val()
            },
            dataType: "json",
            success: (result) => {
                successMsg(gettext("Devices have been changed!"));
            }
        });
        $(this).prop("disabled", false);
    });
});
