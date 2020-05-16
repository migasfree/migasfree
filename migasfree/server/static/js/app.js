function copyToClipboard(element) {
    var $temp = $("<textarea>");
    var brRegex = /<br\s*[\/]?>/gi;

    $("body").append($temp);
    $temp.val($(element).html().replace(brRegex, "\r\n")).select();
    document.execCommand("copy");
    $temp.remove();
}

$(document).ready(function() {
    $('.controls input[type="text"]').addClass('form-control');
    $('.controls input[type="password"]').addClass('form-control');
    $('.controls textarea').addClass('form-control');
    $('.controls select').addClass('form-control');
    $('.actions select').addClass('form-control input-sm');
    $('input[type="submit"]').addClass('btn');

    // wait until all elements has been drawn
    // https://github.com/crucialfelix/django-ajax-selects/pull/67
    setTimeout(function() {
      $('.inline-group ul.tools a.add, .inline-group div.add-row a, .inline-group .tabular tr.add-row td a')
        .on('click', function() {
          $(window).trigger('init-autocomplete');
        });
      if (typeof addMigasEvents === "function") {
          addMigasEvents();
      }
    }, 100);

    $('article').find('input[type=text], textarea').filter(':visible:first').focus();

    $("#domain-search").keyup(function () {
        var search = $("#domain-search").val().toUpperCase();
        var div = $("#domain-names");
        if (div.length) {
            $.each(div.find("li"), function () {
                if ($(this).text().indexOf(search) !== -1) {
                    $(this).css("display", "block");
                }
                else {
                    $(this).css("display", "none");
                }
            });
        }
    });

    $("#search-objects a").click(function () {
        this.href += "?q=" + $("#search-text").val();
    });
});
