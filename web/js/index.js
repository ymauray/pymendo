(function ($) {

    'use strict';

    var backlog = function (data, status, jqXHR) {
        var grid = $("#grid");
        var vignette = $("#templates #vignette");
        vignette.removeAttr("id");
        $(data).each(function (i, o) {
            var clone = vignette.clone();
            clone.find(".vignette").css("background-image", "url('" + o.image + "')");
            clone.find(".title").text(o.name);
            clone.find(".artist").text(o.artist_name);
            clone.find("a").attr("href", "album.html?id=" + o.id + "&single=" + o.single);
            clone.find("a").attr("title", o.name);
            grid.append(clone);
        });
    };

    $(document).ready(function () {
        $.get("rest/backlog").done(backlog);
    });

})(window.jQuery);