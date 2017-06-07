function addTimeLineEvents() {
    $(".btn-timeline").click(function () {
        var deployment = $(this).data("deployment").toString();
        var that = $(this);
        $.get("/timeline/?id=" + deployment, function(data) {
            that.parent().children("ul").html(data);
        });
    });
}

$(document).ready(function () {
    addTimeLineEvents();
});
