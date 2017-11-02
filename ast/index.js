const path = require('path')
const unified = require('unified');
const remarkParse = require('remark-parse');
const rehypeParse = require('rehype-parse')
const remarkRehype = require('remark-rehype');
const remarkStringify = require('remark-stringify');
const rehypeStringify = require('rehype-stringify');
const rehypeAutolink = require('rehype-autolink-headings')
const rehypeSlug = require('rehype-slug')
const doc = require('rehype-document')
const vfile = require('to-vfile')
const deepClone = require('lodash/fp/cloneDeep')
const find = require('unist-util-find')
const inspect = require('unist-util-inspect')
const fs = require('fs');

process.argv.length <3 && (console.log(`node ${path.basename(process.argv[1])} source.md`) || process.exit(0))

headers = []
terms = []


function addToHeader(options = {}) {
  return (node, file) => { header(node) }

  function header(node) {
    if (node.type == "heading")
      headers.push(node.children[0].value)
    else
      (node.children || []).forEach(header)
  }
}


function addSpanToEmp(options = {}) {
    return (node, file) => { span(node) }

    function span(node) {
        if (node.type == "emphasis") {
            node.type = "html"
            text = node.children[0].value
            node.value = `<span class="term">${text}</span>`
            delete node.children
            terms.push(text)
        }
        else (node.children || []).forEach(span)
    }
}


function print(options = {}) {
  return tree => { console.log(inspect(tree)) }
  // return tree => { console.log(tree) }
}


const wrapByTemplate = _ => tree => {

  let templateTree = unified().use(rehypeParse)
      .parse(vfile.readSync('./template.html'))

  let contains = substr => node => (node.value || '').indexOf(substr) >= 0

  let body  = find(templateTree, node =>
    node.children && node.children.some(contains('{{ content }}')))

  body.children = [tree]
  return templateTree
}


const replaceTitle = value => tree => {
  find(tree, node => node.tagName == 'title').value = value
}

sourceFileName = process.argv[2]
sourceFile = vfile.readSync(sourceFileName)

unified()
  .use(remarkParse)
  .use(addToHeader)
  .use(addSpanToEmp)
  // .use(print)
  .use(remarkRehype, { commonmark: true, allowDangerousHTML: true })
  .use(rehypeSlug)
  .use(rehypeAutolink)
  // .use(wrapByTemplate)
  // .use(replaceTitle, headers[0] || '')
  // TODO: insert social meta tags (twitter)
  // TODO: термы:
  //   1. отдельный скрипт, который проходит по markdown,
  //      выделяет все термы и в конце работы отдаёт их скрипту Димы
  //      см. child_process.execFile(file, args, opts, callback)
  //      скрипт Димы подготовит JSON словарь вида { term: {info} }
  //      и положит его куда-нибудь
  //
  //   2. этот скрипт должен принимать путь к словарю Димы и md файл
  //      (скрипт подгатавливает конечный html файл для текущего md файла)
  //      теперь нужно все слова из словаря Димы заменить на <span>термы</span>
  //      но не более двух одинаковых термов в одном #h1 блоке
  //
  //   3. этот скрипт так же должен класть в body.children последним узел с
  //      <script>var dict=словарь димы;</script>
  //      чтобы я в JS мог показывать нужные события
  //
  //   4. после отработки rehypeAutolink нужно пройти по всем
  //      h1-h2-h3 и вытаскивать пары (h1.value, h1.id) чтобы можно было
  //      построить индекс для поиска.
  //      если получится, то будет круто, если будет тройка
  //      (h1.value, h1.id, some text below), текст из текстовых нод,
  //      игнорирующий таблицы, код, и всё такое — чисто текст
  //      он нужен, чтобы юзеру показывать заголовок и некий контекст,
  //      чтобы он понял, нужно ли переходить дальше или нет.
  //      результат сложить в какой-нибудь json файл.
  //      скорее всего мы будем запускать эту штуку на "cat *.md",
  //      чтобы построить индекс по всем файлам. поэтому будет хорошо,
  //      если как-то будет доставаться название файла из переменной file
  //      которая передаётся в трансформеры
  .use(rehypeStringify, { allowDangerousHTML: true })
  .process(sourceFile)
  .then(file => {
    //   console.log(typeof(file))
    // console.log(file.contents)
    file.extname = ".html"
    vfile.writeSync(file)
    // console.log(file);
  })
  .catch(err => console.log('errors: ', err))

// console.log(terms)

termsFileName = sourceFileName.substr(0, sourceFileName.lastIndexOf(".")) + ".json";
fs.writeFile(termsFileName, JSON.stringify(terms), function(err) {
  if(err) {
      return console.log(err);
  }

    //   console.log("The file was saved!");
  });



// console.log("headers:", headers)



// Problems:
// 1. добавление якоря к коду - возможно пересечение с именем в самом названии темы или подтемы (пока не сделала)
//   XXX:  нужно будет добавлять какой-нибудь хвост, а-ля dfs-1 dfs-2
//         но это потом, не самая важная фича пока что. может, даже и
//         не будут проявляться баги
// 2. нет содержания
