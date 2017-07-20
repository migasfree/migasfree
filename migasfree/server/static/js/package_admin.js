function getOptions(url, key, value)
{
    var _options = "";
    $.ajaxSetup({async: false});
    while(url) {
        $.getJSON(url, function(q) {
            var j = q["results"];
            for (var i = 0; i < j.length; i++) {
                _options += "<option value='" + j[i][key] + "'>" + j[i][value] + "</option>";
            }
            url = q["next"];
        });
    }
    $.ajaxSetup({async: true});
    return _options;
}

function changeProject(defaultValue)
{
    if (typeof $("#id_project").val() !== "undefined")
    {
        defaultValue = defaultValue || "";
        $("#id_store").html(getOptions(
            "/api/v1/token/stores/?project__id=" + $("#id_project").val(),
            "id",
            "name"
        ));
        $("#id_store").attr("disabled", false);
        if (typeof defaultValue === "string" && defaultValue !== "")
        {
            $("#id_store option[value=" + defaultValue + "]").attr("selected", true);
        }
        $("#id_project").attr("selected", "selected");
    }
}

$(function() {
    changeProject($("#id_store").val());
    $("#id_project").change(changeProject);
});
