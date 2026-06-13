
async function updateMessages() {
    if (!activeUser) return;
    try {
        const response = await fetch('/api/chat/messages', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                receiver_uid: window.currentUid, lastmsgtime: timeOfLastMessage
            })
        });
        const newChats = await response.json();
        for (let uid in newChats) {
            if (newChats[uid].messages) {
                if (!(uid in window.allChats)) window.allChats[uid] = { messages: [] };
                messages = newChats[uid].messages;
                if (uid != target.value) window.allChats[uid].messages
                    = window.allChats[uid].messages.concat(messages);
                else addMessages(messages);
                updatedTimeOfLastMessage = messages[messages.length - 1].timestamp;
                if (!window.timeOfLastMessage || window.timeOfLastMessage
                    && window.timeOfLastMessage < updatedTimeOfLastMessage)
                    window.timeOfLastMessage = updatedTimeOfLastMessage;
            }
            setUnreadCircle(uid, newChats[uid].unread);
        }
    } catch (err) { console.error(err); }
}

async function sendMessage() {
    try {
        await fetch('/api/chat/send', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                receiver_uid: parseInt(target.value), sender_uid: window.currentUid,
                message: messageInputElement.value
            })
        });
        messageInputElement.value = '';
    } catch (err) { alert('发送失败'); }
}

async function updateUserLastVisit(receiverUid, senderUid) {
    try {
        const response = await fetch('/api/chat/update-lastvisit', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ receiver_uid: receiverUid, sender_uid: senderUid })
        });
        const result = await response.json();
    } catch (err) { console.error(err); }
}

async function switchUser(element, uid) {
    messageSenderArea.classList.toggle('hidden', false);
    if (window.viewCommentsItem) viewCommentsItem.style.display = 'none';
    if (target.value == uid) return;
    elements[uid] = element;
    messageInputElement.disabled = messageSenderButton.disabled = false;
    if (activeUser) activeUser.classList.toggle('active');
    activeUser = element; target.value = uid;
    messageAreaTitle.innerHTML = activeUser.innerHTML;
    activeUser.classList.toggle('active');
    redCircle = activeUser.querySelector('div.unread-badge');
    if (redCircle) redCircle.style.display = 'none';
    messageArea.innerHTML = '';
    if (uid in window.allChats) addMessages(window.allChats[uid].messages, true);
    else window.allChats[uid] = { messages: [] };
    await updateUserLastVisit(window.currentUid, uid);
}

function setUnreadCircle(uid, num) {
    if (!(uid in elements) || !num) return;
    redCircle = elements[uid].querySelector('div.unread-badge');
    redCircle.style.display = 'inline'; redCircle.textContent = num;
}

function setTimeOfLastMessageBy(orderedMessages) {
    if (orderedMessages.length) {
        updatedTimeOfLastMessage = orderedMessages[orderedMessages.length - 1].timestamp;
        if (!window.timeOfLastMessage || window.timeOfLastMessage < updatedTimeOfLastMessage)
            window.timeOfLastMessage = updatedTimeOfLastMessage;
    }
}

function setTimeOfLastMessageByAllChats() {
    let latestTime = '';
    for (let uid in window.allChats) {
        const messages = window.allChats[uid].messages;
        if (messages.length) {
            const lastMessageTime = messages[messages.length - 1].timestamp;
            if (!latestTime || latestTime < lastMessageTime) latestTime = lastMessageTime;
        }
    }
    window.timeOfLastMessage = latestTime;
}

function addMessages(messages, noAllChats) {
    messages.forEach((m) => addMessage(m, noAllChats));
    setTimeOfLastMessageBy(messages);
}

function addMessage(messageInfo, noAllChats) {
    const divElement = document.createElement('div');
    divElement.classList.add('message');
    divElement.classList.toggle('other-message', messageInfo.othersend);
    divElement.classList.toggle('my-message', !messageInfo.othersend);
    divElement.innerText = messageInfo.content;
    messageArea.appendChild(divElement);
    messageArea.scrollTop = messageArea.scrollHeight;
    if (!target.value) window.allChats[target.value] = { messages: [] };
    if (typeof noAllChats === 'undefined' && !noAllChats) {
        if (!(target.value in window.allChats)) window.allChats[target.value] = { messages: [] };
        window.allChats[target.value].messages.push(messageInfo);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.activeUser = document.getElementsByClassName('user-item active')[0];
    setTimeOfLastMessageByAllChats();
    if (!window.timeOfLastMessage) window.timeOfLastMessage = '';
    window.elements = {};
    messageInputElement.addEventListener('keypress', (event) => {
        if (event.key == 'Enter' && messageInputElement.value) sendMessage();
    });
    setInterval(updateMessages, 2000);
});

window.addEventListener('beforeunload', (event) => {
    if (!target.value) return;
    navigator.sendBeacon('/api/chat/update-lastvisit', new Blob(
        [JSON.stringify({ receiver_uid: window.currentUid, sender_uid: parseInt(target.value) })],
        { type: 'application/json; charset=UTF-8' }));
});
