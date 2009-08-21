function getElementsByTagNames(list,obj) {
    if (!obj) var obj = document;
    var tagNames = list.split(',');
    var resultArray = new Array();
    for (var i=0;i<tagNames.length;i++) {
        var tags = obj.getElementsByTagName(tagNames[i]);
        for (var j=0;j<tags.length;j++) {
            resultArray.push(tags[j]);
        }
    }
    var testNode = resultArray[0];
    if (!testNode) return [];
    if (testNode.sourceIndex) {
        resultArray.sort(function (a,b) {
            return a.sourceIndex - b.sourceIndex;
        });
    }
    else if (testNode.compareDocumentPosition) {
        resultArray.sort(function (a,b) {
            return 3 - (a.compareDocumentPosition(b) & 6);
        });
    }
    return resultArray;
}

function createTOC() {
    var y = document.createElement('div');
    y.id = 'innertoc';
    y.setAttribute("class", "content");
    var a = y.appendChild(document.createElement('span'));
    a.onclick = showhideTOC;
    a.id = 'contentheader';
    a.innerHTML = 'show table of contents';
    var z = y.appendChild(document.createElement('div'));
//    z.onclick = showhideTOC;
    var toBeTOCced = getElementsByTagNames('h1,h2,h3,h4,h5');
    if (toBeTOCced.length < 2) return false;
    
    for (var i=0;i<toBeTOCced.length;i++) {
        var tmp = document.createElement('a');
        tmp.innerHTML = toBeTOCced[i].innerHTML;
        tmp.className = 'page';
        z.appendChild(tmp);
        if (toBeTOCced[i].nodeName == 'H3')
            tmp.className += ' indent';
        if (toBeTOCced[i].nodeName == 'H4')
            tmp.className += ' extraindent';
        var headerId = toBeTOCced[i].id || 'link' + i;
        tmp.href = '#' + headerId;
        toBeTOCced[i].id = headerId;
        if (toBeTOCced[i].nodeName == 'H1') {
            tmp.innerHTML = 'Top';
            tmp.href = '#top';
            toBeTOCced[i].id = 'top';
        }
    }
    return y;
}
    
var TOCstate = 'none';
    
function showhideTOC() {
    TOCstate = (TOCstate == 'none') ? 'block' : 'none';
    var newText = (TOCstate == 'none') ? 'show table of contents' : 'hide table of contents';
    document.getElementById('contentheader').innerHTML = newText;
    document.getElementById('innertoc').lastChild.style.display = TOCstate;
}
