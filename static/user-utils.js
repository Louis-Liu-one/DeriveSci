
async function userLogin() {
    try {
        const response = await fetch('/api/user/login', {
            method: 'POST', body: new FormData(loginForm)});
        const data = await response.json();
        if (data.ok) location.replace(loginForm.dataset.nextpage);
        else alert(`登录失败：${data.error}`);
    } catch (err) { alert(`登录失败：${err}`); }
}

async function userRegister() {
    try {
        const response = await fetch('/api/user/register', {
            method: 'POST', body: new FormData(registerForm)});
        const data = await response.json();
        if (data.ok) location.replace(registerForm.dataset.nextpage);
        else alert(`注册失败：${data.error}`);
    } catch (err) { alert(`注册失败：${err}`); }
}

async function userEditProfile() {
    try {
        const response = await fetch('/api/user/edit-profile', {
            method: 'POST', body: new FormData(editForm)});
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`操作失败：${data.error}`);
    } catch (err) { alert(`操作失败：${err}`); }
}

async function userLogout() {
    try {
        const response = await fetch('/api/user/logout', {method: 'POST'});
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`登出失败：${data.error}`);
    } catch (err) { alert(`登出失败：${err}`); }
}

async function userUnregister() {
    if (!confirm('确定要注销账户？')) return;
    try {
        const response = await fetch('/api/user/unregister', {method: 'POST'});
        const data = await response.json();
        if (data.ok) location.replace(data.url);
        else alert(`注销失败：${data.error}`);
    } catch (err) { alert(`注销失败：${err}`); }
}
