
try {
    if (commentbutton.length === undefined) {
        commentbutton = [commentbutton]; subcommentform = [subcommentform];
    }
    for (let i = 0; i < commentbutton.length; i++) {
        commentbutton[i].addEventListener('click', function (event) {
            if (subcommentform[i].style.display != 'inline')
                subcommentform[i].style.display = 'inline';
            else subcommentform[i].style.display = 'none';
        });
    }
} catch (e) { /* when commentbutton is not defined */ }
