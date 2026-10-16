function togglePasswordVisibility(inputId, button) {
    const input = document.getElementById(inputId);
    if (!input) return;

    const isPassword = input.type === 'password';
    input.type = isPassword ? 'text' : 'password';

    button.setAttribute('aria-label', isPassword ? 'Ocultar senha' : 'Mostrar senha');
    button.setAttribute('aria-pressed', isPassword ? 'true' : 'false');

    const icon = button.querySelector('i');
    if (icon) {
        icon.classList.toggle('bi-eye', !isPassword);
        icon.classList.toggle('bi-eye-slash', isPassword);
    }
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    modal.classList.remove('hidden');
    const firstInput = modal.querySelector('input:not([type="hidden"]), button:not([data-close-modal])');
    if (firstInput) {
        firstInput.focus();
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    modal.classList.add('hidden');
    const feedback = modal.querySelector('#recoveryFeedback');
    if (feedback) feedback.classList.add('hidden');
    const openBtn = document.querySelector(`[data-open-modal="${modalId}"]`);
    if (openBtn) {
        openBtn.focus();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const toggleButtons = document.querySelectorAll('[data-toggle-password]');
    toggleButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-toggle-password');
            togglePasswordVisibility(targetId, button);
        });
    });

    const openModalButtons = document.querySelectorAll('[data-open-modal]');
    openModalButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const modalId = button.getAttribute('data-open-modal');
            openModal(modalId);
        });
    });

    const closeModalButtons = document.querySelectorAll('[data-close-modal]');
    closeModalButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const modalId = button.getAttribute('data-close-modal');
            closeModal(modalId);
        });
    });

    document.querySelectorAll('[role="dialog"]').forEach((modal) => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const openModalEl = document.querySelector('[role="dialog"]:not(.hidden)');
            if (openModalEl) {
                closeModal(openModalEl.id);
            }
        }
    });

    const recoveryForm = document.getElementById('formRecoverPassword');
    if (recoveryForm) {
        recoveryForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const feedback = document.getElementById('recoveryFeedback');
            const submitBtn = document.getElementById('btnSubmitRecovery');
            if (feedback) feedback.classList.remove('hidden');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.classList.add('opacity-70', 'cursor-not-allowed');
            }
        });
    }
});
