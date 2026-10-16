function toggleBookmark(btn) {
    const isPressed = btn.getAttribute('aria-pressed') === 'true';
    const nextState = !isPressed;
    btn.setAttribute('aria-pressed', String(nextState));
    btn.classList.toggle('text-brand-action', nextState);

    const icon = btn.querySelector('i');
    if (icon) {
        icon.classList.toggle('bi-bookmark', !nextState);
        icon.classList.toggle('bi-bookmark-fill', nextState);
    }
}

function copyCode(btn) {
    const container = btn.closest('.code-block-container') || btn.closest('.rounded-2xl');
    const codeBlock = container ? container.querySelector('code') : null;
    if (codeBlock) {
        navigator.clipboard.writeText(codeBlock.innerText).then(() => {
            const span = btn.querySelector('span');
            if (span) {
                const orig = span.textContent;
                span.textContent = 'Copiado!';
                setTimeout(() => {
                    span.textContent = orig;
                }, 2000);
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const bookmarkBtn = document.getElementById('btnBookmark');
    if (bookmarkBtn) {
        bookmarkBtn.addEventListener('click', () => toggleBookmark(bookmarkBtn));
    }

    const copyBtns = document.querySelectorAll('[data-copy-code]');
    copyBtns.forEach((btn) => {
        btn.addEventListener('click', () => copyCode(btn));
    });
});
