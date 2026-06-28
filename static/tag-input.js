{
    function createTagInput(opts) {
        const input = document.getElementById(opts.inputId);
        const area = document.getElementById(opts.areaId);
        if (!input || !area) return null;
        const tags = [];

        function render() {
            area.innerHTML = '';
            tags.forEach((t, i) => {
                const a = document.createElement('a');
                a.innerHTML = escapeHTML(t) + ' <i class="delete-button'
                    + ' fas fa-circle-minus" data-i="' + i + '"></i>';
                area.appendChild(a);
            });
            // update a hidden JSON input for structured data
            const hidId = opts.inputId + '_json';
            let hid = document.getElementById(hidId);
            if (!hid) {
                hid = document.createElement('input');
                hid.type = 'hidden'; hid.id = hidId; hid.name = hidId;
                if (input.parentNode) input.parentNode.appendChild(hid);
                else document.body.appendChild(hid);
            }
            hid.value = JSON.stringify(tags);
            // attach delete handlers
            Array.from(area.querySelectorAll('i.delete-button')).forEach(btn => {
                btn.onclick = function (ev) {
                    ev.stopPropagation(); const i = +this.dataset.i;
                    tags.splice(i, 1); render();
                    if (opts.onTagRemove) opts.onTagRemove(tags.slice());
                };
            });
        }

        function addTag(raw) {
            const t = (raw || '').toString().trim();
            if (!t) return false;
            if (!tags.includes(t)) tags.push(t);
            render();
            if (opts.onTagAdd) opts.onTagAdd(tags.slice());
            return true;
        }

        // initialize
        if (Array.isArray(opts.initial)) {
            opts.initial.forEach(v => { if (v) tags.push(v); });
            render();
        }

        // key handling: Enter creates tag and optionally triggers callback
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const val = input.value.trim();
                const added = addTag(val);
                input.value = '';
            }
        });
        return { addTag, getTags: () => tags.slice(), render };
    }

    window.createTagInput = createTagInput;
}
