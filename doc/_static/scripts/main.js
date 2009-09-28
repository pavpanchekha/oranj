$(function () {
    pageSection();
    
    if (window.location.hash) {
        $("#pages li a").filter(function () {
            return $(this).attr("href") == window.location.hash;
        }).click();
        window.location.hash = window.location.hash
    }

    //$(".section h1").hide();
});

function pageSection() {
    var sections = new Array();
    $(".section .section").each(function (i) {
        if ($(this).find("h2").text()) {
            sections.push({text: $(this).find("h2").text().slice(0,-1), id: i});
        }
    });

    var pages = $("<ul id='pages'></ul>");
    
    if (window.location.pathname.match(/index.html$|\/$/)) {
        var elem = $("<li><a href='../index.html'>&#8613; To Parent</a></li>");
    } else {
        var elem = $("<li><a href='./index.html'>&#8613; To Parent</a></li>");
    }
    
    pages.append(elem);
    
    for(var i=0; i < sections.length; i++) {
        var s = sections[i];
        elem = $("<li><a href='#" + s.id + "'>" + s.text + "</a></li>");
        elem.find("a").click(function() {
            el = $(this)

            $(".section .section").hide();
            $("#pages li").removeClass("selected");
            $(".section .section").eq($(this).attr("href").slice(1)).show();
            $("#pages li").filter(function () {
                return $(this).find("a").attr("href") == "#" + el.attr("href").slice(1)
            }).addClass("selected");
            return 0;
        });
        pages.append(elem);
    }

    $("hr").eq(0).after(pages);

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
