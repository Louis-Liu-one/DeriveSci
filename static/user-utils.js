
async function userLogin() {
    try {
        const response = await fetch('/api/user/login', {
            method: 'POST', body: new FormData(loginForm)
        });
        const data = await response.json();
        if (data.ok) location.replace(loginForm.dataset.nextpage);
        else alert(`登录失败：${data.error}`);
    } catch (err) { alert(`登录失败：${err}`); }
}

async function userRegister() {
    try {
        const response = await fetch('/api/user/register', {
            method: 'POST', body: new FormData(registerForm)
        });
        const data = await response.json();
        if (data.ok) location.replace(registerForm.dataset.nextpage);
        else alert(`注册失败：${data.error}`);
    } catch (err) { alert(`注册失败：${err}`); }
}

async function userEditProfile() {
    try {
        const response = await fetch('/api/user/edit-profile', {
            method: 'POST', body: new FormData(editForm)
        });
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`操作失败：${data.error}`);
    } catch (err) { alert(`操作失败：${err}`); }
}

async function userLogout() {
    try {
        const response = await fetch('/api/user/logout', { method: 'POST' });
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`登出失败：${data.error}`);
    } catch (err) { alert(`登出失败：${err}`); }
}

async function userUnregister() {
    if (!confirm('确定要注销账户？')) return;
    try {
        const response = await fetch(
            '/api/user/unregister', { method: 'POST' });
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`注销失败：${data.error}`);
    } catch (err) { alert(`注销失败：${err}`); }
}

function toggleUserIntroductionEdit(originalIntro) {
    toggleUserIntroductionEdit.originalIntroduction = originalIntro;
    const editForm = document.getElementById('introductionEditForm');
    const userIntroDiv = document.getElementById('userIntroductionDisplay');
    const textarea = document.getElementById('introductionTextarea');
    userIntroDiv.addEventListener('click', () => {
        userIntroDiv.classList.add('hidden');
        editForm.classList.remove('hidden');
        textarea.focus();
    });
    textarea.addEventListener('blur', async () => {
        if (editForm.classList.contains('hidden')) return;
        const newVal = (textarea.value || '').trim();
        const oldVal = (
            toggleUserIntroductionEdit.originalIntroduction || '').trim();
        if (newVal === oldVal) {
            if (newVal) {
                editForm.classList.add('hidden');
                userIntroDiv.classList.remove('hidden');
            }
            return;
        }
        try {
            const response = await fetch('/api/user/edit-introduction', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ introduction: textarea.value })
            });
            const data = await response.json();
            if (data.ok) {
                if (newVal) {
                    userIntroDiv.classList.remove('hidden');
                    renderElement(userIntroDiv, textarea.value);
                    editForm.classList.add('hidden');
                    toggleUserIntroductionEdit.originalIntroduction
                        = textarea.value;
                } else alert('修改成功，但简介内容为空，已隐藏简介展示区');
            } else alert(`修改失败：${data.error}`);
        } catch (err) {
            alert(`修改失败：${err}`);
        }
    });
}
