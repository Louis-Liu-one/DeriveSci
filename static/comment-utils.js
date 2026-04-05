
async function deleteComment(commentId) {
    try {
        const response = await fetch('/api/comment/delete', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({commentid: commentId})});
        const data = await response.json();
        if (data.ok) document.querySelector(
            `div[data-commentid='${commentId}']`).remove();
        else alert(`删除失败：${data.error}`);
    } catch (err) { alert(`删除失败：${err}`); }
}

document.addEventListener('DOMContentLoaded', () => {
    if (window.commentSenderButton) {
        if (commentSenderButton.length === undefined) {
            commentSenderButton = [commentSenderButton];
            subCommentForm = [subCommentForm]; }
        Array.from(subCommentForm).forEach((form, i) => {
            commentSenderButton[i].addEventListener('click', (event) => {
                if (form.style.display != 'inline')
                    form.style.display = 'inline';
                else form.style.display = 'none'; }); }); } });
