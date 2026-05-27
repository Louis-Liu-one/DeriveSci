
const md = markdownit({html: true})
    .use(mdItPluginKatex.katex, {
        output: 'html', delimiters: 'all', throwOnError: false,
        macros: {
            '\\dif': '\\mathrm{d}',
            '\\dx': '\\dif{x}', '\\dy': '\\dif{y}', '\\dz': '\\dif{z}',
            '\\dt': '\\dif{t}', '\\du': '\\dif{u}', '\\dv': '\\dif{v}',
            '\\E': '\\mathrm{e}', '\\e': '\\mathrm{e}',
            '\\I': '\\mathrm{i}', '\\i': '\\mathrm{i}',
            '\\paren': '\\left(#1\\right)',
        }})
    .use(mdItPluginFigure.figure);

md.renderer.rules.image = function(tokens, idx, options, env, self) {
    const token = tokens[idx];
    const srcIndex = token.attrIndex('src');
    if (srcIndex >= 0) {
        const originalSrc = token.attrs[srcIndex][1];
        if (originalSrc && !originalSrc.startsWith('/') &&
                !/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(originalSrc) &&
                !originalSrc.startsWith('#') && !originalSrc.startsWith('data:')) {
            let base = env && env.imageBasePath ? env.imageBasePath : '';
            if (!base && typeof window !== 'undefined' && window.__markdownImageBasePath)
                base = window.__markdownImageBasePath;
            if (base && base.endsWith('/')) {
                const src = originalSrc.replace(/^\.\/+/, '');
                token.attrs[srcIndex][1] = base + src;
            }
        }
    }
    return self.renderToken(tokens, idx, options); };

if (window.hljs) md.options['highlight'] = function(str, lang) {
        if (lang && hljs.getLanguage(lang))
            try { return hljs.highlight(
                str, {language: lang, ignoreIllegals: true}).value; } catch { } };
if (window.markdownItAnchor) md.use(markdownItAnchor);
if (window.markdownItTocDoneRight) md.use(markdownItTocDoneRight, {listType: 'ul'});

function renderElement(element, string, display='inline', imageBasePath='') {
    const basePath = imageBasePath ||
        (typeof window !== 'undefined' && window.__markdownImageBasePath) || '';
    element.innerHTML = md.render(string.trim(), {imageBasePath: basePath});
    element.style.display = display;
    return element.innerHTML;
}

function renderElements(toRender, imageBasePath='') {
    const basePath = imageBasePath ||
        (typeof window !== 'undefined' && window.__markdownImageBasePath) || '';
    Array.from(toRender).forEach((divElement) => {
        let textareaElement = divElement.getElementsByTagName('textarea')[0];
        if (textareaElement) renderElement(divElement, textareaElement.value, 'inline', basePath);
    });
}
