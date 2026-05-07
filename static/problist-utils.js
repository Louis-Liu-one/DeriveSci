
function debounce(fn, wait) {
    let t; return function() {
        clearTimeout(t); t = setTimeout(() => fn.apply(this, arguments), wait);
    };
}

function adjustProblist() {
    const wrap = document.querySelector('div.problist-wrap');
    const table = wrap ? wrap.querySelector('table.problist') : null;
    if (!wrap || !table) return;

    const tbody = table.tBodies[0];
    if (!tbody) return;
    Array.from(tbody.querySelectorAll('tr.filler')).forEach(r => r.remove());
    const wrapH = wrap.clientHeight;
    const thead = table.querySelector('thead');
    const headH = thead ? thead.getBoundingClientRect().height : 0;
    const bodyH = tbody.getBoundingClientRect().height;
    const totalH = headH + bodyH;

    if (totalH < wrapH) {
        const sample = tbody.querySelector('tr');
        const needed = Math.ceil((wrapH - totalH) / headH);
        const cols = table.querySelectorAll('tr.probhead th').length || 3;
        for (let i = 0; i < needed; i++) {
            const tr = document.createElement('tr'); tr.className = 'filler';
            for (let j = 0; j < cols; j++) {
                const td = document.createElement('td');
                td.innerHTML = '&nbsp;'; tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }
        wrap.style.overflow = 'hidden';
    } else wrap.style.overflow = '';
}

window.addEventListener('DOMContentLoaded', () => {
    adjustProblist();
    const wrap = document.querySelector('div.problist-wrap');
    if (!wrap) return;
    const tbody = wrap.querySelector('table.problist tbody');
    if (tbody) {
        const mo = new MutationObserver(debounce(adjustProblist, 80));
        mo.observe(tbody, {childList: true, subtree: true});
    }
});
window.addEventListener('resize', debounce(adjustProblist, 120));
