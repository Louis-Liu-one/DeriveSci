
let subprobs = []; let labelList = [];

function renderSubprobs() {
    answerListElement.innerHTML = '';
    subprobs.forEach((sub, i) => {
        const li = document.createElement('li');
        li.className = 'subprob'; li.dataset.index = i;
        const header = document.createElement('div');
        header.className = 'subprob-header';
        // header contains rendered label area and delete button
        header.innerHTML = `<i class="minus delete-subprob `
            + `fa-solid fa-square-minus" data-i="${i}"></i>`;
        const labelDisplay = document.createElement('div');
        labelDisplay.className = 'subprob-label-display';
        const labelEditor = document.createElement('input');
        labelEditor.id = `label-editor-${i}`;
        labelEditor.className = 'subprob-label-editor';
        labelEditor.autocomplete = 'off';
        labelEditor.style.display = 'none';
        labelEditor.rows = 3;
        const defaultLabel = `小题 ${i+1} 的答案`;
        labelEditor.value = sub.label || defaultLabel;
        // render initial label (use default if none provided)
        renderElement(labelDisplay, sub.label || defaultLabel, 'block');
        header.prepend(labelDisplay);
        header.prepend(labelEditor);
        // clicking labelDisplay switches to editor
        labelDisplay.onclick = (ev) => {
            ev.stopPropagation();
            labelDisplay.style.display = 'none';
            labelEditor.style.display = 'block'; labelEditor.focus();
        };
        labelEditor.addEventListener('blur', () => {
            sub.label = labelEditor.value || '';
            labelEditor.style.display = 'none';
            labelDisplay.style.display = 'block';
            if (sub.label) renderElement(labelDisplay, sub.label, 'block');
            else renderElement(labelDisplay, defaultLabel, 'block');
        });
        // clicking header selects
        header.onclick = () => selectSubprob(i);
        li.appendChild(header);
        const ul = document.createElement('ul');
        ul.className = 'subprob-tps';
        sub.tps.forEach((tp, j) => {
            const tpli = document.createElement('li');
            const ctxHtml = escapeHTML(JSON.stringify(tp[0]));
            const ansHtml = escapeHTML(tp[1]);
            tpli.innerHTML = `${ctxHtml}<i class="fa-solid fa-arrow-right"></i>`
                + `<span class="tp-answer">${ansHtml}</span>`
                + `<i class="minus delete-tp fa-solid fa-circle-minus"`
                + ` data-si="${i}" data-ti="${j}"></i>`;
            ul.appendChild(tpli);
        });
        li.appendChild(ul);
        answerListElement.appendChild(li);
    });
    // 绑定删除事件
    answerListElement.querySelectorAll('i.delete-subprob').forEach(btn => {
        btn.onclick = (ev) => {
            ev.stopPropagation(); removeSubprob(+btn.dataset.i); };
    });
    answerListElement.querySelectorAll('i.delete-tp').forEach(btn => {
        btn.onclick = (ev) => {
            ev.stopPropagation(); removeTestpoint(+btn.dataset.si, +btn.dataset.ti); };
    });
    if (window.selectedSub === undefined) window.selectedSub = subprobs.length - 1;
    Array.from(answerListElement.children).forEach((li, idx) => {
        li.classList.toggle('selected', window.selectedSub === idx);
    });
}

function addSubprob() {
    subprobs.push({label: '', tps: []});
    window.selectedSub = subprobs.length - 1;
    renderSubprobs();
}
function removeSubprob(index) {
    subprobs.splice(index, 1);
    if (window.selectedSub >= subprobs.length)
        window.selectedSub = subprobs.length - 1;
    renderSubprobs();
}

function addTestpointToSelected(context, answer) {
    if (!context) context = '{}';
    const parsed = JSON.parse(context);
    if (window.selectedSub === undefined) addSubprob();
    if (!subprobs[window.selectedSub])
        subprobs[window.selectedSub] = {label: '', tps: []};
    subprobs[window.selectedSub].tps.push([parsed, answer]);
    renderSubprobs();
}

function addAnswerHTML(context, answer) {
    addTestpointToSelected(context.value, answer.value);
    context.value = ''; answer.value = '';
}

function selectSubprob(i) { window.selectedSub = i; renderSubprobs(); }

function removeTestpoint(subIndex, tpIndex) {
    if (!subprobs[subIndex]) return;
    if (!subprobs[subIndex].tps) return;
    subprobs[subIndex].tps.splice(tpIndex, 1);
    renderSubprobs();
}

function addRawAnswers(rawAnswerList) {
    if (!rawAnswerList) return;
    // accept two shapes: list of dicts {label, tps} or list of tps (legacy)
    subprobs = rawAnswerList.map(sub => {
        if (Array.isArray(sub)) return {label: '', tps: sub.map(a => [a[0], a[1]])};
        return {label: sub.label || '', tps: (sub.tps || []).map(a => [a[0], a[1]])};
    });
    renderSubprobs();
}

function addLabel(event) {
    if (event.key == 'Enter') {
        event.preventDefault(); const label = probLabel.value.trim();
        if (!label || labelList.includes(label)) return;
        labelList.push(label); renderLabels(); probLabel.value = '';
    }
}

function renderLabels() {
    labelArea.innerHTML = '';
    labelList.forEach((label, i) => {
        const labelElement = document.createElement('a');
        labelElement.className = 'problabel';
        labelElement.innerHTML = `${escapeHTML(label)} <i class="delete-button`
            + ` fa-solid fa-circle-minus" data-i="${i}"></i>`;
        labelArea.appendChild(labelElement);
    });
    labelArea.querySelectorAll('i.delete-button').forEach(deleteButton => {
        deleteButton.onclick = () => {
            labelList.splice(+deleteButton.dataset.i, 1);
            renderLabels();
        };
    });
}

function addRawLabels(rawLabelList) { labelList = [...rawLabelList]; renderLabels(); }

function addHiddenInputElementForList(form, name, list)
{
    let element = form.querySelector(`input[name='${name}']`);
    if (!element) element = document.createElement('input');
    element.type = 'hidden'; element.name = name;
    element.value = JSON.stringify(list); form.appendChild(element);
}

async function uploadProb() {
    addHiddenInputElementForList(editForm, 'answers', subprobs);
    addHiddenInputElementForList(editForm, 'problabels', labelList);
    try {
        const response = await fetch(
            '/api/prob/upload', {method: 'POST', body: new FormData(editForm)});
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`操作失败：${data.error}`);
    } catch (err) { alert(`操作失败：${err}`); }
}

async function editProb() {
    addHiddenInputElementForList(editForm, 'answers', subprobs);
    addHiddenInputElementForList(editForm, 'problabels', labelList);
    try {
        const response = await fetch(
            '/api/prob/edit', {method: 'POST', body: new FormData(editForm)});
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`操作失败：${data.error}`);
    } catch (err) { alert(`操作失败：${err}`); }
}

// 绑定回车键事件到输入框
document.addEventListener('DOMContentLoaded', () => {
    const contextInput = document.getElementById('contextInputElement');
    const answerInput = document.getElementById('answerInputElement');
    if (contextInput && answerInput) {
        const handleEnter = (event) => { if (event.key === 'Enter') {
            event.preventDefault(); addAnswerHTML(contextInput, answerInput); } };
        contextInput.addEventListener('keydown', handleEnter);
        answerInput.addEventListener('keydown', handleEnter);
    }
});
