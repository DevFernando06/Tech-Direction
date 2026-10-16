/**
 * Tech Direction - Controle Responsivo da Sidebar (Menu Lateral)
 * Fecha automaticamente em telas menores e permite alternar abertura/fechamento.
 */

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    const toggleIcon = document.getElementById('sidebarToggleIcon');
    const closeBtn = document.getElementById('sidebarClose');
    const backdrop = document.getElementById('sidebarBackdrop');
    const spacer = document.getElementById('sidebarSpacer');
    const footer = document.getElementById('appFooter');

    if (!sidebar) return;

    const lgMediaQuery = window.matchMedia('(min-width: 1024px)');
    let isOpen = lgMediaQuery.matches;

    function applySidebarState(open, { focusToggle = false } = {}) {
        isOpen = open;
        const isDesktop = lgMediaQuery.matches;

        if (toggleBtn) {
            toggleBtn.setAttribute('aria-expanded', String(open));
            toggleBtn.setAttribute('aria-label', open ? 'Fechar menu lateral' : 'Abrir menu lateral');
        }

        if (toggleIcon) {
            const showCloseIcon = open && !isDesktop;
            toggleIcon.classList.toggle('bi-list', !showCloseIcon);
            toggleIcon.classList.toggle('bi-x-lg', showCloseIcon);
        }

        if (open) {
            sidebar.classList.remove('-translate-x-full', 'lg:-translate-x-full');
            sidebar.classList.add('translate-x-0', 'lg:translate-x-0');
            sidebar.removeAttribute('aria-hidden');
            sidebar.removeAttribute('inert');
        } else {
            sidebar.classList.remove('translate-x-0', 'lg:translate-x-0');
            sidebar.classList.add('-translate-x-full', 'lg:-translate-x-full');
            sidebar.setAttribute('aria-hidden', 'true');
            sidebar.setAttribute('inert', '');
        }

        if (backdrop) {
            if (open && !isDesktop) {
                backdrop.classList.remove('hidden');
                document.body.classList.add('overflow-hidden', 'lg:overflow-auto');
            } else {
                backdrop.classList.add('hidden');
                document.body.classList.remove('overflow-hidden', 'lg:overflow-auto');
            }
        }

        if (spacer) {
            spacer.classList.toggle('lg:w-60', open);
            spacer.classList.toggle('lg:w-0', !open);
        }

        if (footer) {
            footer.classList.toggle('lg:pl-60', open);
            footer.classList.toggle('lg:pl-0', !open);
        }

        if (focusToggle && toggleBtn) {
            toggleBtn.focus();
        }
    }

    // Estado inicial sincronizado com o tamanho da tela
    applySidebarState(lgMediaQuery.matches);

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            applySidebarState(!isOpen);
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            applySidebarState(false, { focusToggle: true });
        });
    }

    if (backdrop) {
        backdrop.addEventListener('click', () => {
            applySidebarState(false, { focusToggle: true });
        });
    }

    // Fecha automaticamente ao clicar em qualquer link da sidebar no mobile/tablet
    const sidebarLinks = sidebar.querySelectorAll('a');
    sidebarLinks.forEach((link) => {
        link.addEventListener('click', () => {
            if (!lgMediaQuery.matches && isOpen) {
                applySidebarState(false);
            }
        });
    });

    // Fecha automaticamente quando a tela diminui para mobile/tablet e reabre no desktop
    const handleBreakpointChange = (e) => {
        applySidebarState(e.matches);
    };

    if (typeof lgMediaQuery.addEventListener === 'function') {
        lgMediaQuery.addEventListener('change', handleBreakpointChange);
    } else if (typeof lgMediaQuery.addListener === 'function') {
        lgMediaQuery.addListener(handleBreakpointChange);
    }

    // Fecha com a tecla Escape quando aberto no mobile/tablet
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isOpen && !lgMediaQuery.matches) {
            applySidebarState(false, { focusToggle: true });
        }
    });
});
