///////////// Multiselect field
let multiselect_block = document.querySelectorAll('.multiselect_block');
for (const parent of multiselect_block) {
    console.log(parent);
    let label = parent.querySelector('.field_multiselect');
    let select = parent.querySelector('.field_select');
    if (!label || !select) {
        continue;
    }
    let text = label.innerHTML;
    select.addEventListener('change', (function () {
        let selectedOptions = this.selectedOptions;
        label.innerHTML = '';
        for (let option of selectedOptions) {
            let button = document.createElement('button');
            button.type = 'button';
            button.className = 'btn_multiselect';
            button.textContent = option.innerText;
            button.onclick = _ => {
                option.selected = false;
                button.remove();
                if (!select.selectedOptions.length) label.innerHTML = text;
            };
            label.append(button);
        }
    }));
}