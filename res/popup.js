'use strict'

let $ = s => document.querySelectorAll(s)

var links = $('.term')

for (var i=0; i < links.length; ++i) {
    var a = links[i]
    a.setAttribute("data-popup", terms[a.innerText].wiki.extract.substring(0, 250)+"...")
    a.setAttribute("href", terms[a.innerText].wiki.wiki_url)
}
