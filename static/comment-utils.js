
async function deleteComment(commentId) {
    try {
        const response = await fetch('/api/comment/delete', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({commentid: commentId})});
        const data = await response.json();
        if (data.ok) {
            const element = document.querySelector(`div[data-commentid='${commentId}']`);
            if (element) {
                // 删除紧跟的div.comments-sep元素（如果存在）
                const nextSep = element.nextElementSibling;
                if (nextSep && nextSep.classList.contains('comments-sep')) nextSep.remove();
                element.remove();
                // 检查是否需要显示“暂无讨论”
                const commentList = document.querySelector('div.comments-container');
                if (commentList && commentList.querySelectorAll('.comment').length === 0)
                    commentList.insertAdjacentHTML('beforeend', '<p>暂无讨论</p>');
            }
        } else alert(`删除失败：${data.error}`);
    } catch (err) { alert(`删除失败：${err}`); }
}

function handleFormSubmit(form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const textarea = form.querySelector('textarea');
        const content = textarea.value.trim();
        if (!content) return;
        await postComment(form, content);
        textarea.value = '';
        // 只隐藏子评论表单，不隐藏主评论表单
        if (form.id === 'subCommentForm') form.style.display = 'none';
    });
}

function handleCommentSenderButton(button) {
    button.addEventListener('click', () => {
        const commentDiv = button.closest('.comment');
        const form = commentDiv.querySelector('#subCommentForm');
        if (form) form.style.display = form.style.display !== 'inline' ? 'inline' : 'none';
    });
}

async function postComment(element, content) {
    const postType = element.dataset.posttype;
    const postIdent = element.dataset.postident;
    const replyToId = element.dataset.cmtid || null;
    try {
        const response = await fetch('/api/comment/post', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                post_type: +postType, post_ident: postIdent, content,
                replyto_id: replyToId ? +replyToId : null})});
        const data = await response.json();
        if (data.ok) {
            const html = data.html;
            let newCommentElement;
            if (data.is_reply) {
                const repliedComment = document.querySelector(
                    `div[data-commentid='${replyToId}']`);
                let topLevelComment = repliedComment;
                while (topLevelComment.parentElement
                    && !topLevelComment.parentElement.classList.contains('comments-container'))
                    topLevelComment = topLevelComment.parentElement.closest('.comment');
                const subcomments = topLevelComment.querySelector('.subcomments');
                subcomments.insertAdjacentHTML('beforeend', html);
                newCommentElement = subcomments.lastElementChild;
            } else {
                const commentList = document.querySelector('div.comments-container');
                // 移除“暂无讨论”字样
                const noCommentsMsg = commentList.querySelector('p');
                if (noCommentsMsg && noCommentsMsg.textContent === '暂无讨论')
                    noCommentsMsg.remove();
                commentList.insertAdjacentHTML(
                    'afterbegin', html + '<div class="comments-sep"></div>');
                newCommentElement = commentList.firstElementChild;
            }
            // 渲染新评论的Markdown
            if (window.renderElements) renderElements(
                newCommentElement.querySelectorAll('div.comment-content'));
            // 绑定新评论的回复按钮和表单提交事件
            const button = newCommentElement.querySelector('#commentSenderButton');
            if (button) handleCommentSenderButton(button);
            const form = newCommentElement.querySelector('#subCommentForm');
            if (form) handleFormSubmit(form);
            if (typeof flask_moment_render_all === 'function') flask_moment_render_all();
        } else alert(`发表失败：${data.error}`);
    } catch (err) { alert(`发表失败：${err}`); }
}

document.addEventListener('DOMContentLoaded', () => {
    // 绑定初始的回复按钮
    document.querySelectorAll('#commentSenderButton').forEach(
        button => { handleCommentSenderButton(button); });
    // 添加表单提交监听器
    document.querySelectorAll('#commentForm, #subCommentForm').forEach(
        form => { handleFormSubmit(form); });
});
