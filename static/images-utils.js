
function bindImagesList() {
    const main = document.getElementById('imagesMain');
    if (!main) return;
    document.querySelectorAll('.image-row').forEach(row => {
        row.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const name = row.dataset.name;
                const postType = main.dataset.postType;
                const postIdent = main.dataset.postIdent;
                if (name && postType && postIdent) window.location.href
                    = `/images/${encodeURIComponent(postType)}/`
                        `${encodeURIComponent(postIdent)}/`
                        `${encodeURIComponent(name)}/view`;
            }
        });
        row.tabIndex = 0;
    });
}

function bindImagePreview() {
    const main = document.getElementById('imageMain');
    if (!main) return;
    const postType = main.dataset.postType;
    const postIdent = main.dataset.postIdent;
    const imagename = main.dataset.imagename;
    const display = document.getElementById('imageTitleDisplay');
    const form = document.getElementById('imageTitleForm');
    const input = document.getElementById('imageTitleInput');
    const saveBtn = document.getElementById('saveTitleBtn');

    if (display && form && input) {
        display.addEventListener('click', () => {
            display.classList.add('hidden');
            form.classList.remove('hidden');
            input.focus();
        });
        input.addEventListener('blur', async () => {
            if (form.classList.contains('hidden')) return;
            const newVal = (input.value || '').trim();
            const original = display.textContent.trim();
            if (newVal === original) {
                form.classList.add('hidden'); display.classList.remove('hidden'); return;
            }
            try {
                const resp = await fetch('/api/image/rename', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        post_type: postType, post_ident: postIdent,
                        oldname: imagename, newname: newVal
                    })
                });
                const data = await resp.json();
                if (data.ok) {
                    window.location.href = data.newurl;
                } else alert('重命名失败：' + (data.error || '未知错误'));
            } catch (err) { alert('重命名失败：' + err); }
        });
        saveBtn.addEventListener('click', (ev) => { ev.preventDefault(); input.blur(); });
    }

    // Reupload dialog handling
    const reuploadModal = document.getElementById('reuploadModal');
    const reuploadForm = document.getElementById('reuploadForm');
    const reuploadCancel = document.getElementById('reuploadCancel');
    if (reuploadModal && reuploadForm) {
        reuploadCancel && reuploadCancel.addEventListener('click', () => {
            if (reuploadModal.close) reuploadModal.close();
            else reuploadModal.classList.add('hidden');
        });
        reuploadForm.addEventListener('submit', async function (ev) {
            ev.preventDefault();
            const fileInput = document.getElementById('reuploadFile');
            if (!fileInput || !fileInput.files.length) { alert('请选择文件'); return; }
            const fd = new FormData();
            fd.append('post_type', postType);
            fd.append('post_ident', postIdent);
            fd.append('name', imagename);
            fd.append('imgfile', fileInput.files[0]);
            try {
                const resp = await fetch('/api/image/reupload', { method: 'POST', body: fd });
                const data = await resp.json();
                if (data.ok) alert('上传成功，但是图片缓存需要更新，请清空浏览器缓存或者等待稍后查看效果。');
                else alert('上传失败：' + (data.error || '未知错误'));
            } catch (err) { alert('上传失败：' + err); }
        });
    }

    // Delete
    window.deleteImage = async function () {
        if (!confirm('确定删除此图片吗？此操作不可撤销。')) return;
        try {
            const resp = await fetch('/api/image/delete', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    post_type: postType, post_ident: postIdent, name: imagename
                })
            });
            const data = await resp.json();
            if (data.ok) window.location.href = data.url;
            else alert('删除失败：' + (data.error || '未知错误'));
        } catch (err) { alert('删除失败：' + err); }
    };

    // helper to show modal/dialog
    window.showReuploadModal = function () {
        if (reuploadModal) {
            if (reuploadModal.showModal) reuploadModal.showModal();
            else reuploadModal.classList.remove('hidden');
        }
    };
}

document.addEventListener('DOMContentLoaded',
    () => { bindImagesList(); bindImagePreview(); });
