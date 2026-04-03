
let activeUser = document.getElementsByClassName('user-item active')[0];
let lastmsgtime = '';
let elements = {};
msginput.addEventListener('keypress', (event) => {
    if (event.key == 'Enter' && msginput.value) sendMessage(); });

window.addEventListener('beforeunload', (event) => {
    if (!target.value) return;
    navigator.sendBeacon('/api/chat/update-lastvisit', new Blob(
        [JSON.stringify({
            receiver_uid: currentUid, sender_uid: parseInt(target.value)})],
        {type: "application/json; charset=UTF-8"}));
});

async function updateMessages()
{
    if (!activeUser) return;
    try {
        const response = await fetch(`/api/chat/messages`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                receiver_uid: currentUid, lastmsgtime: lastmsgtime})});
        const new_chats = await response.json();
        for (let uid in new_chats) {
            if (new_chats[uid].messages) {
                messages = new_chats[uid].messages;
                if (uid != target.value) all_chats[uid].messages
                    = all_chats[uid].messages.concat(messages);
                else addMessages(messages);
                new_lastmsgtime = messages[messages.length - 1].timestamp;
                if (!lastmsgtime
                    || lastmsgtime && lastmsgtime < new_lastmsgtime)
                    lastmsgtime = new_lastmsgtime;
            }
            setUnreadCircle(uid, new_chats[uid].unread);
        }
    } catch (err) { }
}

async function sendMessage()
{
    try {
        await fetch('/api/chat/send', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                receiver_uid: parseInt(target.value), sender_uid: currentUid,
                message: msginput.value})});
        msginput.value = '';
    } catch (err) { alert('发送失败'); }
}

async function updateUserLastVisit(receiver_uid, sender_uid)
{
    try {
        const response = await fetch('/api/chat/update-lastvisit', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                receiver_uid: receiver_uid, sender_uid: sender_uid})});
        const result = await response.json();
    } catch (err) { console.error(err); }
}

async function switchUser(element, uid) {
    sendarea.className = 'send-area';
    if (window.viewcomments) viewcomments.style.display = 'none';
    if (target.value == uid) return;
    elements[uid] = element;
    msginput.disabled = msgbutton.disabled = false;
    if (activeUser) activeUser.className = 'user-item';
    activeUser = element; target.value = uid;
    chattitle.innerHTML = activeUser.innerHTML;
    activeUser.className = 'user-item active';
    redCircle = activeUser.querySelector('div.unread-badge')
    if (redCircle) redCircle.style.display = 'none';
    msgarea.innerHTML = '';
    if (uid in all_chats) addMessages(all_chats[uid].messages);
    else all_chats[uid] = {messages: []};
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
    new_lastmsgtime = messages[messages.length - 1].timestamp;
    if (messages.length && (!lastmsgtime
        || lastmsgtime && lastmsgtime < new_lastmsgtime))
        lastmsgtime = new_lastmsgtime;
}

function addMessage(messageInfo) {
    const divElement = document.createElement('div');
    divElement.className = messageInfo.othersend
        ? 'message other-message' : 'message my-message';
    divElement.innerText = messageInfo.content;
    msgarea.appendChild(divElement);
    msgarea.scrollTop = msgarea.scrollHeight;
    if (!target.value) all_chats[target.value] = {messages: []};
    all_chats[target.value].messages.push(messageInfo);
}

setInterval(updateMessages, 2000);
