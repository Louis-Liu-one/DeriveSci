
async function setOfficialProb(event) {
    event.preventDefault();
    const probno = this.dataset.probno;
    try {
        const response = await fetch('/api/admin/set-official-prob', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({probno: probno})});
        const data = await response.json();
        if (data.isofficial) {
            setofficialdiv.innerHTML
                = '<i class="fa-solid fa-circle-minus"></i>从官方题目移除';
            isofficialtip.className = 'helpslink'; alert('已添加到官方题目');
        } else {
            setofficialdiv.innerHTML
                = '<i class="fa-solid fa-circle-plus"></i>添加到官方题目';
            isofficialtip.className = 'hidden'; alert('已从官方题目移除');
        }
    } catch (err) { alert('操作失败'); }
}

async function reviewProb(btn, accept) {
    try {
        const response = await fetch('/api/admin/review-prob', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                probno: btn.dataset.probno, accept: accept})});
        const data = await response.json();
        alert('操作成功'); location.replace(data.url);
    } catch (err) { alert('操作失败'); }
}
