$(function () {
    $("body").prepend($(createTOC())).find("#innertoc div").hide();
    showhideTOC();
    pageSection();
    
    if (window.location.hash) {
        $("#innertoc a, #pages li a").filter(function () {
            return $(this).attr("href") == window.location.hash;
        }).click();
        window.location.hash = window.location.hash
    }
});

function pageSection() {
    var sections = new Array();
    $("section").each(function (i) {
        sections.push({text: $(this).find("h2").text(), id: i});
    });

    var pages = $("<ul id='pages'></ul>");
    var elem = $("<li><a href='./'>&#8613; To Parent</a></li>");
    pages.append(elem);
    
    for(var i=0; i < sections.length; i++) {
        var s = sections[i];
        elem = $("<li><a href='#" + s.id + "'>" + s.text + "</a></li>");
        elem.find("a").click(function() {
            $("section").hide();
            $("#pages li").removeClass("selected");
            $("section").eq($(this).attr("href").slice(1)).show();
            $("#pages li").eq($(this).attr("href").slice(1) - 0 + 1).addClass("selected");
            return 0;
        });
        pages.append(elem);
    }

    $("hr").after(pages);

    $("#innertoc a").click(function() {
        if ($($(this).attr("href")).height() == 0) {
            var sec = $($(this).attr("href")).parent("section").find("h2").html();
            $("#pages li a").filter(function () {
                return $(this).html() == sec;
            }).click();
        }
    });

    $("#pages li a").eq(1).click();
}