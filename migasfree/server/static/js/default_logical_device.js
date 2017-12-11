$(function() {
    $("#id_assigned_logical_devices_to_cid").on("select2:select", function (e) {
        $("#id_default_logical_device").append(
            $("<option></option>").attr("value", e.params.data.id).text(e.params.data.text)
        );
    });

    $("#id_assigned_logical_devices_to_cid").on("select2:unselect", function (e) {
        $("#id_default_logical_device option[value='" + e.params.data.id + "']").remove();
    });
});
