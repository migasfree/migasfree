function addMigasEvents() {
    $("body").on("click", ".btn-migas", function() {
        var app = $(this).data("app");
        var model = $(this).data("model");
        var pk = $(this).data("pk");
        var that = $(this);
        $.get("/link/?app=" + app + "&model=" + model + "&pk=" + pk, function(data) {
            that.parent().children("ul").html(data);
        });
    });
}
