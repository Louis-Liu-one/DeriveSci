
let activeUser = document.getElementsByClassName('user-item active')[0];
let lastmsgtime = '';
msginput.addEventListener('keypress', function (event) {
    if (event.key == 'Enter') sendMessage(); });

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
                receiver_uid: currentUid, sender_uid: parseInt(target.value),
                lastmsgtime: lastmsgtime})});
        const messages = await response.json();
        addMessages(messages);
    } catch (e) { }
}

async function sendMessage()
{
    await fetch('/api/chat/send', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            receiver_uid: parseInt(target.value), sender_uid: currentUid,
            message: msginput.value})});
    addMessages([{
        content: msginput.value, othersend: false,
        timestamp: new Date().toISOString()}]);
    msginput.value = '';
}

async function updateUserLastVisit(receiver_uid, sender_uid)
{
    try {
        const response = await fetch('/api/chat/update-lastvisit', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                receiver_uid: receiver_uid, sender_uid: sender_uid}),
        });
        const result = await response.json();
    } catch (err) { console.error(err); }
}

async function switchUser(element, uid) {
    msginput.disabled = msgbutton.disabled = false;
    if (activeUser) activeUser.className = 'user-item';
    activeUser = element; target.value = uid;
    chattitle.innerHTML = activeUser.innerHTML;
    activeUser.className = 'user-item active';
    redCircle = activeUser.querySelector('div.unread-badge')
    if (redCircle) redCircle.style.display = 'none';
    msgarea.innerHTML = '';
    if (uid in all_chats) addMessages(all_chats[uid].messages);
    await updateUserLastVisit(currentUid, uid);
}

function addMessages(messages) {
    for (let i in messages) addMessage(messages[i]);
    if (messages.length) lastmsgtime = messages[messages.length - 1].timestamp;
}

function addMessage(messageInfo) {
    const divElement = document.createElement('div');
    divElement.className = messageInfo.othersend ?
        'message other-message' : 'message my-message';
    divElement.innerText = messageInfo.content;
    msgarea.appendChild(divElement);
    msgarea.scrollTop = msgarea.scrollHeight;
}

setInterval(updateMessages, 2000);
