(function ($) {

    'use strict';

    var backlog = function (data, status, jqXHR) {
        console.log(data);
        var releasedate = new Date(data['album']['releasedate']);
        $('#header.album .vignette').css("background-image", "url('" + data['album']['image'] + "')");
        $('#header.album .type').text(data['album']['single'] === '0' ? 'Album' : 'Single');
        $('#header.album .title').text(data['album']['name']);
        $('#header.album .artist').text(data['album']['artist_name']);
        $('#header.album .releasedate').text(releasedate.toLocaleDateString());
        var track = $("#templates #track");
        var tracks = $(".tracks");
        $(data.tracks).each(function(i, t) {
            var clone = track.clone();
            clone.removeAttr("id");
            clone.find(".minivignette").css("background-image", "url('" + t['image'] + "')");
            clone.find(".title").text(t['track_name']);
            clone.find(".artist").text(t['artist_name']);
            clone.find("audio").attr("src", t['audio']);
            tracks.append(clone);
        });
    };

    function getParameter(name) {
        var queryParameters = window.location.search.substring(1);
        var parameters = queryParameters.split('&');
        var value = null;
        $(parameters).each(function(i, parameter) {
            var parameterParts = parameter.split('=');
            if (parameterParts[0] === name) {
                value = decodeURIComponent(parameterParts[1]);
            }
        });
        return value;
    }

    $(document).ready(function () {
        var id = getParameter("id");
        var single = getParameter("single");
        $.get("rest/album/" + id + "/" + single).done(backlog);
        $("#reject-album").on("click", function() {
            $.get("rest/reject/" + id + "/" + single).done(function() {
                window.location = "index.html";
            });
        });
    });

})(window.jQuery);