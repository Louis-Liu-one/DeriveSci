
async function renameTag(oldTitle, newTitle) {
    try {
        const response = await fetch('/api/tag/rename', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ old_title: oldTitle, new_title: newTitle })
        });
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`操作失败：${data.error}`);
    } catch (err) { alert(`操作失败：${err}`); }
}

function submitRenameTagForm(ev) {
    ev.preventDefault();
    const form = ev.target;
    const oldTitle = form.dataset.oldTitle;
    const newTitle = form.querySelector('input[name="new_title"]').value.trim();
    if (!newTitle) { alert('新标签名不能为空'); return; }
    if (oldTitle === newTitle) { alert('新标签名与旧标签名相同'); return; }
    renameTag(oldTitle, newTitle);
}

function showRenameTagModal(oldTitle) {
    const modal = document.getElementById('renameTagModal');
    const form = document.getElementById('renameTagForm');
    if (!modal || !form) return;
    form.dataset.oldTitle = oldTitle;
    form.querySelector('input[name="new_title"]').value = oldTitle;
    if (modal.showModal) modal.showModal();
    else alert('浏览器不支持弹窗，请使用现代浏览器。');
}

document.addEventListener('DOMContentLoaded', () => {
    const renameModal = document.getElementById('renameTagModal');
    const renameForm = document.getElementById('renameTagForm');
    const renameCancel = document.getElementById('renameTagCancel');
    if (renameModal && renameCancel)
        renameCancel.addEventListener('click', () => {
            if (renameModal.close) renameModal.close();
        });
    if (renameForm) renameForm.addEventListener('submit', submitRenameTagForm);
});
