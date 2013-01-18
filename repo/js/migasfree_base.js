if (typeof active_accordion == 'undefined')
{
    var active_accordion = 0;
}

$(document).ready(function() {
    $('.messagelist').fadeOut(5000);

    $("section nav").accordion({
        collapsible: true,
        active: active_accordion,
        heightStyle: "content"
    });

    // progressive enhancement!!!
    $("#sliding-panel").toggle();
    $("a#hide_button").css("display", "block");

    function expand_sidebar()
    {
        $("section nav").show();
        $("section nav").animate({
            width: "25%"
        })
        .animate({
            width: "20%"
        }, "fast");

        $("a#show_button").css("display", "none");
        $("a#hide_button").css("display", "block");

        $("#sliding-panel").css("left", "18.5%");
        $("body").removeClass("full");

        document.cookie = 'sidebar=expanded;path=/';

        return false;
    }

    function collapse_sidebar()
    {
        $("section nav").hide();
        $("section nav").animate({
            width: "0"
        }, "fast");

        $("body").addClass("full");
        $("#sliding-panel").css("left", "0");

        $("a#hide_button").css("display", "none");
        $("a#show_button").css("display", "block");

        document.cookie = 'sidebar=collapsed;path=/';

        return false;
    }

    function sidebar_is_collapsed()
    {
        return $("section nav").is(':not(:visible)');
    }

    function set_position_from_cookie()
    {
        if (!document.cookie)
            return;

        var items = document.cookie.split(';');
        for (var k = 0; k < items.length; k++)
        {
            var key_val = items[k].split('=');
            var key = $.trim(key_val[0]);
            if (key == 'sidebar')
            {
                var value = $.trim(key_val[1]);
                if ((value == 'collapsed') && (!sidebar_is_collapsed()))
                    collapse_sidebar();
                else if ((value == 'expanded') && (sidebar_is_collapsed()))
                    expand_sidebar();
            }
        }
    }

    $("a.panel_button").click(expand_sidebar);
    $("a#hide_button").click(collapse_sidebar);
    set_position_from_cookie();
});
