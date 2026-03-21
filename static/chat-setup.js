
let activeUser = document.getElementsByClassName('user-item active')[0];

function switchUser(element, uid) {
    msginput.disabled = msgbutton.disabled = false;
    if (activeUser) activeUser.className = 'user-item';
    activeUser = element; target.value = uid;
    chattitle.innerText = `正在和 ${activeUser.innerText} 聊天`;
    activeUser.className = 'user-item active';
    msgarea.innerHTML = '';
    if (uid in all_chats) addMessages(all_chats[uid]);
}

function addMessages(messages) {
    for (let i in messages) addMessage(messages[i]);
}

function addMessage(messageInfo) {
    const divElement = document.createElement('div');
    const [content, flag] = messageInfo;
    divElement.className = flag ?
        'message other-message' : 'message my-message';
    divElement.innerText = content;
    msgarea.appendChild(divElement);
    msgarea.scrollTop = msgarea.scrollHeight;
}
