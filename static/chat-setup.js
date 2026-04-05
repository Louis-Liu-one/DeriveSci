
let activeUser = document.getElementsByClassName('user-item active')[0];
let timeOfLastMessage = '';
let elements = {};
messageInputElement.addEventListener('keypress', (event) => {
    if (event.key == 'Enter' && messageInputElement.value) sendMessage(); });

window.addEventListener('beforeunload', (event) => {
    if (!target.value) return;
    navigator.sendBeacon('/api/chat/update-lastvisit', new Blob(
        [JSON.stringify({
            receiver_uid: currentUid, sender_uid: parseInt(target.value)})],
        {type: "application/json; charset=UTF-8"}));
});

async function updateMessages() {
    if (!activeUser) return;
    try {
        const response = await fetch('/api/chat/messages', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                receiver_uid: currentUid, lastmsgtime: timeOfLastMessage})});
        const new_chats = await response.json();
        for (let uid in new_chats) {
            if (new_chats[uid].messages) {
                messages = new_chats[uid].messages;
                if (uid != target.value) allChats[uid].messages
                    = allChats[uid].messages.concat(messages);
                else addMessages(messages);
                updatedTimeOfLastMessage
                    = messages[messages.length - 1].timestamp;
                if (!timeOfLastMessage || timeOfLastMessage
                    && timeOfLastMessage < updatedTimeOfLastMessage)
                    timeOfLastMessage = updatedTimeOfLastMessage;
            }
            setUnreadCircle(uid, new_chats[uid].unread);
        }
    } catch (err) { }
}

async function sendMessage() {
    try {
        await fetch('/api/chat/send', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                receiver_uid: parseInt(target.value), sender_uid: currentUid,
                message: messageInputElement.value})});
        messageInputElement.value = '';
    } catch (err) { alert('发送失败'); }
}

async function updateUserLastVisit(receiver_uid, sender_uid) {
    try {
        const response = await fetch('/api/chat/update-lastvisit', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                receiver_uid: receiver_uid, sender_uid: sender_uid})});
        const result = await response.json();
    } catch (err) { console.error(err); }
}

async function switchUser(element, uid) {
    messageSenderArea.className = 'send-area';
    if (window.viewCommentsItem) viewCommentsItem.style.display = 'none';
    if (target.value == uid) return;
    elements[uid] = element;
    messageInputElement.disabled = messageSenderButton.disabled = false;
    if (activeUser) activeUser.className = 'user-item';
    activeUser = element; target.value = uid;
    messageAreaTitle.innerHTML = activeUser.innerHTML;
    activeUser.className = 'user-item active';
    redCircle = activeUser.querySelector('div.unread-badge');
    if (redCircle) redCircle.style.display = 'none';
    messageArea.innerHTML = '';
    if (uid in allChats) addMessages(allChats[uid].messages);
    else allChats[uid] = {messages: []};
    await updateUserLastVisit(currentUid, uid);
}

function setUnreadCircle(uid, num) {
    if (!(uid in elements) || !num) return;
    redCircle = elements[uid].querySelector('div.unread-badge');
    redCircle.style.display = 'inline';
    redCircle.textContent = num;
}

function addMessages(messages) {
    for (let i in messages) addMessage(messages[i]);
    updatedTimeOfLastMessage = messages[messages.length - 1].timestamp;
    if (messages.length && (!timeOfLastMessage
        || timeOfLastMessage && timeOfLastMessage < updatedTimeOfLastMessage))
        timeOfLastMessage = updatedTimeOfLastMessage;
}

function addMessage(messageInfo) {
    const divElement = document.createElement('div');
    divElement.className = messageInfo.othersend
        ? 'message other-message' : 'message my-message';
    divElement.innerText = messageInfo.content;
    messageArea.appendChild(divElement);
    messageArea.scrollTop = messageArea.scrollHeight;
    if (!target.value) allChats[target.value] = {messages: []};
    allChats[target.value].messages.push(messageInfo);
}

setInterval(updateMessages, 2000);
