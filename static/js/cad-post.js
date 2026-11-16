/**
 * Tech Direction - Cadastro de Post
 */

function insertFormattingInTextarea(textarea, prefix, suffix) {
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    const selectedText = text.substring(start, end);

    const replacement = prefix + (selectedText || 'texto') + suffix;
    textarea.value = text.substring(0, start) + replacement + text.substring(end);
    textarea.focus();
    textarea.setSelectionRange(start + prefix.length, start + prefix.length + (selectedText.length || 5));
}

function updateSectionNumbers() {
    const container = document.getElementById('sectionsContainer');
    if (!container) return;

    const items = container.querySelectorAll('.post-section-item');
    items.forEach((item, index) => {
        const number = index + 1;
        const badge = item.querySelector('.section-badge');
        if (badge) {
            badge.innerHTML = `<span class="w-6 h-6 rounded-lg bg-brand-dark text-white flex items-center justify-center text-[11px]">${number}</span> Seção ${number}`;
        }

        const removeBtn = item.querySelector('.btn-remove-section');
        if (removeBtn) {
            removeBtn.classList.toggle('hidden', items.length === 1);
        }
    });
}

function addNewSection() {
    const container = document.getElementById('sectionsContainer');
    if (!container) return;

    const firstSection = container.querySelector('.post-section-item');
    if (!firstSection) return;

    const clone = firstSection.cloneNode(true);
    clone.querySelectorAll('input, textarea').forEach((field) => {
        field.value = '';
    });

    const previewBox = clone.querySelector('.section-img-preview');
    const previewImg = clone.querySelector('.section-img-preview-el');
    if (previewBox && previewImg) {
        previewBox.classList.add('hidden');
        previewImg.removeAttribute('src');
    }

    container.appendChild(clone);
    updateSectionNumbers();
}

function handleSectionImagePreview(input) {
    const item = input.closest('.post-section-item');
    const previewBox = item?.querySelector('.section-img-preview');
    const previewImg = item?.querySelector('.section-img-preview-el');
    if (!previewBox || !previewImg) return;

    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            previewBox.classList.remove('hidden');
        };
        reader.readAsDataURL(input.files[0]);
    } else {
        previewImg.removeAttribute('src');
        previewBox.classList.add('hidden');
    }
}

function openPreviewModal() {
    const modal = document.getElementById('previewModal');
    if (!modal) return;

    const titleEl = document.getElementById('postTitle');
    const descEl = document.getElementById('postDescription');

    const prevTitle = document.getElementById('prevTitle');
    const prevDesc = document.getElementById('prevDescription');
    const prevArea = document.getElementById('prevSectionsArea');

    if (prevTitle) {
        prevTitle.textContent = (titleEl && titleEl.value.trim()) || 'Sem título definido';
    }
    if (prevDesc) {
        prevDesc.textContent = (descEl && descEl.value.trim()) || 'Sem descrição informada.';
    }

    if (prevArea) {
        prevArea.innerHTML = '';
        const sections = document.querySelectorAll('.post-section-item');

        sections.forEach((sec, idx) => {
            const subtitle = sec.querySelector('.section-subtitle-input')?.value.trim();
            const text = sec.querySelector('.section-text-input')?.value.trim();
            const previewImg = sec.querySelector('.section-img-preview-el');
            const previewBox = sec.querySelector('.section-img-preview');
            const imgSrc = previewImg && previewBox && !previewBox.classList.contains('hidden')
                ? previewImg.getAttribute('src')
                : '';

            const block = document.createElement('div');
            block.className = 'space-y-3 pb-6 border-b border-line last:border-b-0';

            if (subtitle) {
                const h3 = document.createElement('h3');
                h3.className = 'text-lg sm:text-xl font-bold text-brand-dark';
                h3.textContent = subtitle;
                block.appendChild(h3);
            }

            if (imgSrc) {
                const img = document.createElement('img');
                img.src = imgSrc;
                img.alt = subtitle || `Imagem da seção ${idx + 1}`;
                img.className = 'w-full max-h-72 object-cover rounded-xl border border-line shadow-xs';
                block.appendChild(img);
            }

            const p = document.createElement('p');
            p.className = 'whitespace-pre-line text-ink leading-relaxed text-sm sm:text-base';
            p.textContent = text || '(Esta seção ainda não possui texto)';
            block.appendChild(p);

            prevArea.appendChild(block);
        });
    }

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.classList.add('overflow-hidden');
}

function closePreviewModal() {
    const modal = document.getElementById('previewModal');
    if (!modal) return;
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    document.body.classList.remove('overflow-hidden');
}

function toggleLivePreview() {
    const modal = document.getElementById('previewModal');
    if (!modal) return;

    if (modal.classList.contains('hidden')) {
        openPreviewModal();
    } else {
        closePreviewModal();
    }
}

function initCadPost() {
    const addBtn = document.getElementById('btnAddSection');
    if (addBtn) {
        addBtn.addEventListener('click', (e) => {
            e.preventDefault();
            addNewSection();
        });
    }

    const container = document.getElementById('sectionsContainer');
    if (container) {
        container.addEventListener('change', (e) => {
            if (e.target.classList.contains('section-img-input')) {
                handleSectionImagePreview(e.target);
            }
        });

        container.addEventListener('click', (e) => {
            const removeBtn = e.target.closest('.btn-remove-section');
            if (removeBtn) {
                e.preventDefault();
                const item = removeBtn.closest('.post-section-item');
                if (item && container.querySelectorAll('.post-section-item').length > 1) {
                    item.remove();
                    updateSectionNumbers();
                }
                return;
            }

            const formatBtn = e.target.closest('.btn-format');
            if (formatBtn) {
                e.preventDefault();
                const item = formatBtn.closest('.post-section-item');
                const textarea = item?.querySelector('.section-text-input');
                const prefix = (formatBtn.getAttribute('data-format-prefix') || '').replace(/\\n/g, '\n');
                const suffix = (formatBtn.getAttribute('data-format-suffix') || '').replace(/\\n/g, '\n');
                insertFormattingInTextarea(textarea, prefix, suffix);
            }
        });
    }

    document.querySelectorAll('[data-toggle-preview]').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            toggleLivePreview();
        });
    });

    const modal = document.getElementById('previewModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closePreviewModal();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                closePreviewModal();
            }
        });
    }

    updateSectionNumbers();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCadPost);
} else {
    initCadPost();
}
