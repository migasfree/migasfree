function addMigasEvents() {
    $(".btn-migas").parent().on("show.bs.dropdown", function() {
        var that = $(".btn-migas", this);
        var app = that.data("app");
        var model = that.data("model");
        var pk = that.data("pk");

        $.get("/link/?app=" + app + "&model=" + model + "&pk=" + pk, function(data) {
            that.parent().children("ul").html(data);
        });
    });
}
