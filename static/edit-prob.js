
let answerList = []; let labelList = [];

function addAnswer(context, answer) {
    try {
        if (!context) context = '{}';
        answerList.push([JSON.parse(context), answer]);
        const li = document.createElement('li');
        li.dataset.index = answerList.length - 1;
        li.innerHTML = `${escapeHTML(context)}
            <i class="fa-solid fa-arrow-right"></i> ${escapeHTML(answer)}
            <i class="minus fa-solid fa-circle-minus"></i>`;
        const minusIcon = li.querySelector('.minus');
        minusIcon.addEventListener('click',
            () => removeAnswer(parseInt(li.dataset.index)));
        answerListElement.appendChild(li);
    } catch (err) { alert(err); }
}

function addAnswerHTML(context, answer) {
    addAnswer(context.value, answer.value);
    context.value = ''; answer.value = '';
}

function removeAnswer(index) {
    answerListElement.removeChild(answerListElement.children[index]);
    answerList.splice(index, 1);
    // 更新所有li的data-index
    for (let i = 0; i < answerListElement.children.length; i++)
        answerListElement.children[i].dataset.index = i;
}

function addRawAnswers(rawAnswerList) {
    rawAnswerList.forEach(answer => {
        addAnswer(JSON.stringify(answer[0]), answer[1]); });
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
        labelArea.appendChild(labelElement); });
    labelArea.querySelectorAll('i.delete-button').forEach(deleteButton => {
        deleteButton.onclick = () => {
            labelList.splice(+deleteButton.dataset.i, 1);
            renderLabels(); }; });
}

function addRawLabels(rawLabelList) {
    labelList = [...rawLabelList]; renderLabels();
}

function addHiddenInputElementForList(form, name, list)
{
    let element = form.querySelector(`input[name='${name}']`);
    if (!element) element = document.createElement('input');
    element.type = 'hidden'; element.name = name;
    element.value = JSON.stringify(list); form.appendChild(element);
}

async function uploadProb() {
    addHiddenInputElementForList(editForm, 'answers', answerList);
    addHiddenInputElementForList(editForm, 'problabels', labelList);
    try {
        const response = await fetch('/api/prob/upload', {
            method: 'POST', body: new FormData(editForm)});
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`操作失败：${data.error}`);
    } catch (err) { alert(`操作失败：${err}`); }
}

async function editProb() {
    addHiddenInputElementForList(editForm, 'answers', answerList);
    addHiddenInputElementForList(editForm, 'problabels', labelList);
    try {
        const response = await fetch('/api/prob/edit', {
            method: 'POST', body: new FormData(editForm)});
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
        const handleEnter = (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                addAnswerHTML(contextInput, answerInput); } };
        contextInput.addEventListener('keydown', handleEnter);
        answerInput.addEventListener('keydown', handleEnter);
    }
});
