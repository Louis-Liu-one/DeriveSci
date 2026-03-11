
const md = markdownit({html: true})
    .use(texmath, {engine: katex, delimiters: ['dollars', 'brackets']});
if (window.hljs) md.options['highlight'] = function (str, lang) {
        if (lang && hljs.getLanguage(lang))
            try { return hljs.highlight(
                str, {language: lang, ignoreIllegals: true}).value;
            } catch {} }
if (window.markdownItAnchor) md.use(markdownItAnchor);
if (window.markdownItTocDoneRight) md.use(
    markdownItTocDoneRight, {listType: 'ul'});

function renderElement(element, string, display='inline') {
    element.innerHTML = md.render(string.trim());
    element.style.display = display;
    return element.innerHTML;
}

function renderElements(toRender) {
    for (let divElement of toRender) {
        let textareaElement = divElement.children[0];
        if (textareaElement.tagName == 'TEXTAREA')
            renderElement(divElement, textareaElement.value);
    }
}
