'use strict'


// console.log("TEST")


let $ = s => document.querySelector(s)

var a = $('.term')

a.setAttribute("data-popup", terms[a.innerText].wiki.extract)
a.setAttribute("href", terms[a.innerText].wiki.wiki_url)
