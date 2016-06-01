function changeData()
{
    if ($("#id_model").val() !== "")
    {
        $.getJSON("/connections_model/?id=" + $("#id_model").val(), function(connectionList)
        {
            var html = "";
            for (var i = 0; i < connectionList.length; i++)
            {
                if (connectionList[i].pk === parseInt($("#id_connection").val()))
                {
                    if (connectionList[i].fields.fields !== "")
                    {
                        html += "<div class='row join'>";
                        var fields = connectionList[i].fields.fields.split(",");
                        var data = eval("(" + $("#id_data").val() + ")");
                        for (var j = 0; j < fields.length; j++)
                        {
                            var value = (typeof data[fields[j]] !== "undefined") ? data[fields[j]] : "";
                            html += "<div class='control-group'>";
                            html += "<div class='col-md-12 form-group'>";
                            html += "<div class='control-label col-sm-3'>";
                            html += "<label for='join_" + fields[j] + "'>" + fields[j] + "</label>";
                            html += "</div>";
                            html += "<div class='controls col-sm-9'>";
                            html += "<input id='join_" + fields[j] + "' type='text' class='form-control join_field' value='" + value + "' />";
                            html += "</div>";
                            html += "</div>";
                            html += "</div>";
                        }
                        html += "</div>";
                    }
                }
            }

            // remove fields
            $("div.join").remove();

            // append new related fields
            $("div.fields").append(html);
        });
    }
}


function changeModel(defaultValue)
{
    defaultValue = defaultValue || "";

    if ($("#id_model").val() === "")
    {
        $("#id_connection").attr("disabled", true);
    }
    else
    {
        $.getJSON("/connections_model/?id="+$("#id_model").val(), function(j) {
            var options = "";
            for (var i = 0; i < j.length; i++) {
                options += "<option value='" + parseInt(j[i].pk) + "'>" + j[i].fields.name + "</option>";
            }
            $("#id_connection").html(options);
            $("#id_connection").attr("disabled", false);

            if (typeof defaultValue === "string" && defaultValue !== "")
            {
                $("#id_connection option[value=" + defaultValue + "]").attr("selected", true);
            }
        });
        $("#id_model").attr("selected", "selected");
        changeData();
    }
}


$(function() {
    if ($("#device_form").length) {
        $(".field-data label").addClass("sr-only");
        $("#id_data").closest("div").hide();
        $("#id_data").attr("hidden", "hidden");

        if ($("#id_model").val() === "")
        {
            $("#id_connection").attr("disabled", true);
        }

        changeModel($("#id_connection").val());

        $("#id_model").change(changeModel);
        $("#id_connection").change(changeData);

        $("#device_form").submit(function(event) {
            var data = '';
            $(".join_field").each(function(i) {
                data += '"' + $(this).attr("id").substring("join_".length) + '"';
                data += ":";
                data += '"' + $(this).val() + '",';
            });
            $("#id_data").val("{" + data.substring(0, data.length - 1) + "}");

            return;
        });
    }
});
