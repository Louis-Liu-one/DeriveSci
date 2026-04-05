
if (window.commentSenderButton) {
    if (commentSenderButton.length === undefined) {
        commentSenderButton = [commentSenderButton];
        subCommentForm = [subCommentForm];
    }
    Array.from(subCommentForm).forEach((form, i) => {
        commentSenderButton[i].addEventListener('click', (event) => {
            if (form.style.display != 'inline') form.style.display = 'inline';
            else form.style.display = 'none'; }); });
}
