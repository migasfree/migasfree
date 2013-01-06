if (typeof active_accordion == 'undefined')
{
    var active_accordion = 0;
}

$(document).ready(function() {
    setInterval(function() {
        $('#status').load("{% url 'ajax_status' %}");
    }, 10000);

    $('.messagelist').fadeOut(5000);

    $("section nav").accordion({
        collapsible: true,
        active: active_accordion,
        heightStyle: "content"
    });

    // progressive enhancement!!!
    $("body").addClass("full");
    $("section nav").toggle();
    $("#sliding-panel").toggle();
    $("a#show_button").css("display", "block");

    $("a.panel_button").click(function(){
        $("section nav").toggle();
        $("section nav").animate({
            width: "25%"
        })
        .animate({
            width: "20%"
        }, "fast");

        $("a.panel_button").toggle();
        $("a#hide_button").css("display", "block");
        $("#sliding-panel").css("left", "18.5%");
        $("body").removeClass("full");

        return false;
    });

    $("a#hide_button").click(function(){
        $("section nav").animate({
            width: "0"
        }, "fast");

        $("body").addClass("full");
        $("#sliding-panel").css("left", "0");
        $(this).css("display", "none");

        return false;
    });
});
