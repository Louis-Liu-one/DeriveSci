async function uploadArticle() {
    try {
        const response = await fetch('/api/article/upload', {
            method: 'POST', body: new FormData(editForm)
        });
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`操作失败：${data.error}`);
    } catch (err) { alert(`操作失败：${err}`); }
}

async function editArticle() {
    try {
        const response = await fetch('/api/article/edit', {
            method: 'POST', body: new FormData(editForm)
        });
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`操作失败：${data.error}`);
    } catch (err) { alert(`操作失败：${err}`); }
}

async function deleteArticle(article_id) {
    try {
        const response = await fetch('/api/article/delete', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ article_id })
        });
        const data = await response.json();
        if (data.ok) { alert('操作成功'); location.replace(data.url); }
        else alert(`操作失败：${data.error}`);
    } catch (err) { alert(`操作失败：${err}`); }
}

function toggleArticleToc() {
    const toc = document.getElementById('tocBlock');
    if (!toc) return;
    const tocNav = toc.querySelector('nav.table-of-contents');
    if (!tocNav || !tocNav.innerHTML) return;
    const isOpen = toc.classList.toggle('open');
    if (window.matchMedia('(max-width: 768px)').matches) {
        const sidebarToggle = document.getElementById('sidebar-toggle');
        if (sidebarToggle && sidebarToggle.checked)
            sidebarToggle.checked = false;
    }
}
