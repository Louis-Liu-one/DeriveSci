
async function uploadSolution() {
    try {
        const response = await fetch('/api/solution/upload', {
            method: 'POST', body: new FormData(editForm)
        });
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`操作失败：${data.error}`);
    } catch (err) { alert(`操作失败：${err}`); }
}

async function editSolution() {
    try {
        const response = await fetch('/api/solution/edit', {
            method: 'POST', body: new FormData(editForm)
        });
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`操作失败：${data.error}`);
    } catch (err) { alert(`操作失败：${err}`); }
}
