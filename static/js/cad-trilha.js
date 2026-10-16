function insertFormatting(textareaId, prefix, suffix) {
    const textarea = document.getElementById(textareaId);
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

function handleCoverImagePreview(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const img = document.getElementById('coverPreviewImage');
            const container = document.getElementById('coverPreviewContainer');
            if (img && container) {
                img.src = e.target.result;
                container.classList.remove('hidden');
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function toggleLivePreview() {
    const modal = document.getElementById('previewModal');
    if (!modal) return;

    const isHidden = modal.classList.contains('hidden');

    if (isHidden) {
        const titleEl = document.getElementById('trailTitle');
        const categoryEl = document.getElementById('trailCategory');
        const summaryEl = document.getElementById('trailSummary');
        const contentEl = document.getElementById('trailContent');

        document.getElementById('prevTitle').textContent = (titleEl && titleEl.value) || 'Sem título definido';
        document.getElementById('prevBadge').textContent = (categoryEl && categoryEl.value) || 'Categoria';
        document.getElementById('prevSummary').textContent = (summaryEl && summaryEl.value) || 'Sem resumo editorial.';

        const contentArea = document.getElementById('prevContentArea');
        const textValue = contentEl && contentEl.value ? contentEl.value : '<em>Nenhum texto informado ainda.</em>';
        contentArea.innerHTML = `
            <div class="whitespace-pre-line text-ink leading-relaxed text-sm sm:text-base">
                ${textValue}
            </div>
        `;

        modal.classList.remove('hidden');
    } else {
        modal.classList.add('hidden');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const coverInput = document.getElementById('coverImageFile');
    if (coverInput) {
        coverInput.addEventListener('change', () => handleCoverImagePreview(coverInput));
    }

    const previewToggleBtns = document.querySelectorAll('[data-toggle-preview]');
    previewToggleBtns.forEach((btn) => {
        btn.addEventListener('click', toggleLivePreview);
    });

    const saveDraftBtn = document.getElementById('btnSaveDraft');
    if (saveDraftBtn) {
        saveDraftBtn.addEventListener('click', () => {
            alert('Rascunho salvo localmente com sucesso!');
        });
    }

    document.querySelectorAll('[data-format-target]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-format-target');
            const prefix = (btn.getAttribute('data-format-prefix') || '').replace(/\\n/g, '\n');
            const suffix = (btn.getAttribute('data-format-suffix') || '').replace(/\\n/g, '\n');
            insertFormatting(targetId, prefix, suffix);
        });
    });
});
