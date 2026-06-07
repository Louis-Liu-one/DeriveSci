
function debounce(fn, wait) {
    let t; return function () {
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
        mo.observe(tbody, { childList: true, subtree: true });
    }
    // set up client-side filtering for fields except 'statement'
    const probNo = document.getElementById('probNo');
    const probTitle = document.getElementById('probTitle');
    const probLabels = document.getElementById('probLabels');
    const source = document.getElementById('source');
    const probType = document.getElementById('probType');
    const reviewStatus = document.getElementById('reviewStatus');
    const form = document.querySelector('.form-base');

    // SERVER_RESULTS holds backend-returned results as a list of probno strings
    window.SERVER_RESULTS = Array.isArray(window.PROBS_DATA) ? window.PROBS_DATA.slice() : [];

    function normalize(s) { return (s || '').toString().toLowerCase().trim(); }

    function matchRow(row) {
        const d = row.dataset;
        // probno
        const qno = normalize(probNo && probNo.value);
        if (qno && !normalize(d.probno).includes(qno)) return false;
        // title
        const qtitle = normalize(probTitle && probTitle.value);
        if (qtitle && !normalize(d.title).includes(qtitle)) return false;
        let wantLabels = [];
        const probLabelsJson = document.getElementById('probLabels_json');
        if (probLabelsJson && probLabelsJson.value)
            wantLabels = JSON.parse(probLabelsJson.value || '[]');
        else wantLabels = [];
        if (wantLabels.length) {
            const have = JSON.parse(d.labels || '[]').map(s => s.toString().toLowerCase());
            for (const w of wantLabels)
                if (!have.includes(w.toLowerCase ? w.toLowerCase() : w)) return false;
        }
        let wantSrc = [];
        const sourceJson = document.getElementById('source_json');
        if (sourceJson && sourceJson.value)
            wantSrc = JSON.parse(sourceJson.value || '[]');
        else wantSrc = [];
        if (wantSrc.length) {
            const have = normalize(d.source);
            let ok = false;
            for (const w of wantSrc)
                if (have.includes((w || '').toString().toLowerCase())) { ok = true; break; }
            if (!ok) return false;
        }
        // prob type
        if (probType) {
            const v = probType.value;
            if (v === 'officialprobs' && d.isofficial !== '1') return false;
            if (v === 'noofficialprobs' && d.isofficial !== '0') return false;
        }
        // review status (only present when select exists)
        if (reviewStatus) {
            const v = reviewStatus.value;
            if (v === 'toreview' && d.review != '-1') return false;
            if (v === 'accepted' && d.review != '1') return false;
            if (v === 'rejected' && d.review != '0') return false;
        }
        return true;
    }

    function applyFilter() {
        // Hide/show existing table rows based on SERVER_RESULTS and other filters.
        const wrap = document.querySelector('div.problist-wrap');
        const tbody = wrap ? wrap.querySelector('table.problist tbody') : null;
        if (!tbody) return;
        // Build set of allowed probnos from SERVER_RESULTS (array of probno strings)
        const base = Array.isArray(window.SERVER_RESULTS) ? window.SERVER_RESULTS : (
            Array.isArray(window.PROBS_DATA) ? window.PROBS_DATA : []);
        const allowed = new Set(base);
        const rows = Array.from(tbody.querySelectorAll('tr'))
            .filter(r => !r.classList.contains('probhead'));
        let anyVisible = false;
        for (const row of rows) {
            if (row.classList.contains('filler')) continue;
            const probno = row.dataset.probno || '';
            if (!allowed.has(probno)) { row.style.display = 'none'; continue; }
            const ok = matchRow(row);
            row.style.display = ok ? '' : 'none';
            anyVisible = anyVisible || ok;
        }
        const noEl = document.getElementById('noResults');
        if (noEl) {
            if (!anyVisible) { noEl.style.display = 'block'; if (wrap) wrap.style.display = 'none'; }
            else { noEl.style.display = 'none'; if (wrap) wrap.style.display = ''; }
        }
        adjustProblist();
    }

    // expose filter function globally so tag-input.js can call it
    window.applyProblistFilter = applyFilter;

    const inputs = [probNo, probTitle, probLabels, source];
    inputs.forEach(inp => {
        if (inp) inp.addEventListener('input', debounce(applyFilter, 120));
    });
    // re-run local filter when statement is cleared; copy PROBS_DATA into SERVER_RESULTS
    const statement = document.getElementById('statement');
    if (statement) {
        statement.addEventListener('input', debounce(function () {
            if (!this.value || this.value.trim().length === 0) {
                // restore server-results to full PROBS_DATA (as probno list)
                window.SERVER_RESULTS = Array.isArray(window.PROBS_DATA)
                    ? window.PROBS_DATA.slice() : [];
                applyFilter();
            }
        }, 120));
    }
    if (probType) probType.addEventListener('change', applyFilter);
    if (reviewStatus) reviewStatus.addEventListener('change', applyFilter);

    // intercept form submit: if statement is empty, perform client-side filter instead of posting
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const statementVal = statement ? (statement.value || '').trim() : '';
            if (!statementVal) {
                // no content -> reset server results to full and apply local filter
                window.SERVER_RESULTS = Array.isArray(window.PROBS_DATA) ? window.PROBS_DATA.slice() : [];
                applyFilter(); return;
            }
            // fetch backend results for 'statement' only
            try {
                const resp = await fetch('/api/prob/search-content', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        statement: statementVal,
                        reviewmode: window.REVIEWMODE === true || window.REVIEWMODE === 'true',
                        oflabel: window.OF_LABEL === true || window.OF_LABEL === 'true',
                        labelname: window.LABEL_NAME || null
                    })
                });
                if (resp.ok) {
                    const data = await resp.json();
                    // accept backend results as list of probno
                    window.SERVER_RESULTS = Array.isArray(data.results) ? data.results : [];
                    applyFilter();
                } else console.error('Fail to fetch backend results: ', resp.status);
            } catch (err) { console.error(err); }
        });
    }
});

window.addEventListener('resize', debounce(adjustProblist, 120));
