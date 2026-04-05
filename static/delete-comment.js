
function deleteComment(url, cmtid) {
    const form = document.createElement('form');
    form.method = 'POST'; form.action = url;
    const cmtid_input = document.createElement('input');
    cmtid_input.type = 'hidden'; cmtid_input.name = 'cmtid';
    cmtid_input.value = cmtid;
    form.appendChild(cmtid_input); document.body.appendChild(form);
    form.submit();
}
