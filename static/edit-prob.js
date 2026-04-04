
answerlist_js = [];

function addAnswer(context, answer) {
    try {
        if (!context) context = '{}';
        answerlist_js.push([JSON.parse(context), answer]);
        const li = document.createElement('li');
        li.innerHTML = `${escapeHTML(context)}
            <i class="fa-solid fa-arrow-right"></i> ${escapeHTML(answer)}
            <i onclick="removeAnswer(${ulanswerlist.children.length})"
                class="minus fa-solid fa-circle-minus"></i>`;
        ulanswerlist.appendChild(li);
    } catch (error) { alert(error); }
}

function addAnswerHTML(context, answer) {
    addAnswer(context.value, answer.value);
    context.value = ''; answer.value = '';
}

function removeAnswer(index) {
    ulanswerlist.removeChild(ulanswerlist.children[index]);
    answerlist_js.splice(index, 1);
}

function addAnswersBefore(answerlist_jsbefore) {
    for (var i = 0; i < answerlist_jsbefore.length; i++)
        addAnswer(JSON.stringify(
            answerlist_jsbefore[i][0]), answerlist_jsbefore[i][1]);
}

async function uploadProb() {
    const answerlist_input = document.createElement('input');
    answerlist_input.type = 'hidden'; answerlist_input.name = 'answers';
    answerlist_input.value = JSON.stringify(answerlist_js);
    editform.appendChild(answerlist_input);
    try {
        const response = await fetch('/api/prob/upload', {
            method: 'POST', body: new FormData(editform)});
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`操作失败：${data.error}`);
    } catch (err) { alert(`操作失败：${err}`); }
}

async function editProb() {
    const answerlist_input = document.createElement('input');
    answerlist_input.type = 'hidden'; answerlist_input.name = 'answers';
    answerlist_input.value = JSON.stringify(answerlist_js);
    editform.appendChild(answerlist_input);
    try {
        const response = await fetch('/api/prob/edit', {
            method: 'POST', body: new FormData(editform)});
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`操作失败：${data.error}`);
    } catch (err) { alert(`操作失败：${err}`); }
}
