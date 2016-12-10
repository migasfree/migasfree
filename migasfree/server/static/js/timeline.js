function addTimeLineEvents() {
    $(".btn-timeline").click(function () {
        var repository = $(this).data("repository").toString();
        var that = $(this);
        $.get("/timeline/?id=" + repository, function(data) {
            that.parent().children("ul").html(data);
        });
    });
}

$(document).ready(function () {
    addTimeLineEvents();
});


