var renderMath = () => renderMathInElement(document.body, {
  throwOnError: false,
  delimiters: [
    {left: "$$", right: "$$", display: true},
    {left: "\\[", right: "\\]", display: true},
    {left: "$", right: "$", display: false},
    {left: "\\(", right: "\\)", display: false}
  ]
})

function encodeB64(str) {
  // first we use encodeURIComponent to get percent-encoded UTF-8,
  // then we convert the percent encodings into raw bytes which
  // can be fed into btoa.
  return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g,
    (match, p1) => String.fromCharCode('0x' + p1)));
}

function decodeB64(str) {
  // Going backwards: from bytestream, to percent-encoding, to original string.
  return decodeURIComponent(atob(str)
    .split('')
    .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
    .join(''));
}

var getQueryParam = name => {
    name = name.replace(/[\[\]]/g, "\\$&")
    var url     = window.location.href
    var regex   = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)")
    var results = regex.exec(url)

    if (!results) return null
    if (!results[2]) return ''
    return decodeB64(decodeURIComponent(results[2].replace(/\+/g, " ")))
}


window.onload = e => {
  renderMath()
  hljs.initHighlighting()

  var paragraph = getQueryParam('p')
  if (paragraph) {
    var node = document.evaluate(paragraph, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE).singleNodeValue

    node.style.border = "4px dashed rgba(244, 67, 54, 0.58)"
    node.scrollIntoView()
  }


  document.onmouseup = e => {
    r = window.getSelection();
    if (r.toString().rangeCount < 2) return;

    // var $button = document.querySelector('#mistake')
    // $button.style.display = 'block'
    //
    // var rect = r.getRangeAt(0).getBoundingClientRect();
    // var relative = document.body.parentNode.getBoundingClientRect();
    // $button.style.top   = `${r.bottom}px`;
    // $button.style.right = `${r.right}px`;
    // $button.style.opacity = 1

    var wholeParagraph = r.anchorNode.parentNode.innerText
    var cite = wholeParagraph.split('\n').map(s => '> ' + s).join('\n')

    var url = location.href.replace(location.hash, '')
    var xpath = getElementXpath(r.anchorNode.parentNode)
    var backlink = `${url}?p=${encodeURIComponent(encodeB64(xpath))}`

    var newIssue = 'https://github.com/xamgore/au-conspectus/issues/new'
    var msg = `Ребят, кажется у вас [ошибка](${backlink}) во фразе\`${r.toString()}\`, в параграфе:\n${cite}\n\n`
    var title = encodeURIComponent(`Ошибка в конспекте`)
    var link = `${newIssue}?title=${title}&body=${encodeURIComponent(msg)}`
    console.log(link)
  }
};
