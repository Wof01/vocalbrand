// SUPREME DESKTOP SIDEBAR TOGGLE - Nuclear fix
(function() {
    'use strict';
    
    console.log('VocalBrand: SUPREME Desktop toggle starting...');
    
    function isDesktop() {
        return window.innerWidth >= 993;
    }
    
    function getSidebar() {
        return document.querySelector('[data-testid="stSidebar"]');
    }
    
    function isCollapsed() {
        const sidebar = getSidebar();
        if (!sidebar) return false;
        
        // Check collapsedControl presence
        const collapsedControl = document.querySelector('[data-testid="collapsedControl"]');
        if (collapsedControl && collapsedControl.offsetParent !== null) return true;
        
        // Check transform
        const style = window.getComputedStyle(sidebar);
        if (style.transform && style.transform.includes('matrix') && style.transform.includes('-')) return true;
        
        // Check position
        const rect = sidebar.getBoundingClientRect();
        return rect.x < -100 || rect.width < 40;
    }
    
    function updateButtonState() {
        const btn = document.getElementById('vb-desktop-toggle');
        if (!btn || !isDesktop()) return;
        
        const collapsed = isCollapsed();
        btn.textContent = collapsed ? '»' : '«';
        document.body.classList.toggle('vb-sidebar-collapsed', collapsed);
        console.log('VocalBrand: Button state updated - collapsed:', collapsed);
    }
    
    function forceSidebarState(shouldBeOpen) {
        const sidebar = getSidebar();
        if (!sidebar) return;
        
        console.log('VocalBrand: Forcing sidebar', shouldBeOpen ? 'OPEN' : 'CLOSED');
        
        if (shouldBeOpen) {
            // FORCE OPEN
            sidebar.style.cssText = `
                position: sticky !important;
                top: 0 !important;
                left: 0 !important;
                transform: translateX(0) !important;
                margin-left: 0 !important;
                width: 21rem !important;
                min-width: 21rem !important;
                max-width: 21rem !important;
                height: 100vh !important;
                z-index: 1 !important;
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                transition: transform 0.3s ease-in-out !important;
            `;
            
            // Hide expand control
            const expandControl = document.querySelector('[data-testid="collapsedControl"]');
            if (expandControl) expandControl.style.display = 'none';
            
        } else {
            // FORCE CLOSED
            sidebar.style.cssText = `
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                transform: translateX(-21rem) !important;
                width: 21rem !important;
                min-width: 21rem !important;
                max-width: 21rem !important;
                height: 100vh !important;
                z-index: 9999 !important;
                transition: transform 0.3s ease-in-out !important;
            `;
            
            // Show expand control
            const expandControl = document.querySelector('[data-testid="collapsedControl"]');
            if (expandControl) {
                expandControl.style.display = 'block';
                expandControl.style.position = 'fixed';
                expandControl.style.left = '0';
                expandControl.style.top = '50%';
                expandControl.style.transform = 'translateY(-50%)';
                expandControl.style.zIndex = '999999';
            }
        }
    }
    
    function handleToggleClick() {
        console.log('VocalBrand: SUPREME Toggle clicked!');
        const currentlyCollapsed = isCollapsed();
        console.log('VocalBrand: Current state - collapsed:', currentlyCollapsed);
        
        // Try clicking Streamlit native buttons first
        if (currentlyCollapsed) {
            const expandBtn = document.querySelector('[data-testid="collapsedControl"] button');
            if (expandBtn) {
                console.log('VocalBrand: Attempting native expand click');
                expandBtn.click();
            }
        } else {
            const collapseBtn = document.querySelector('[data-testid="stSidebar"] button[kind="header"]');
            if (collapseBtn) {
                console.log('VocalBrand: Attempting native collapse click');
                collapseBtn.click();
            }
        }
        
        // FORCE the opposite state via CSS (nuclear option)
        setTimeout(() => {
            forceSidebarState(currentlyCollapsed); // If was collapsed, force open; if was open, force closed
            updateButtonState();
        }, 50);
        
        setTimeout(updateButtonState, 200);
        setTimeout(updateButtonState, 400);
    }
    
    function init() {
        if (!isDesktop()) return;
        
        const btn = document.getElementById('vb-desktop-toggle');
        if (!btn) {
            console.warn('VocalBrand: Desktop toggle button not found!');
            return;
        }
        
        // Wire click handler (only once)
        if (!btn.dataset.supremeBound) {
            btn.addEventListener('click', handleToggleClick);
            btn.dataset.supremeBound = '1';
            console.log('VocalBrand: SUPREME toggle wired!');
        }
        
        // Initial state
        updateButtonState();
    }
    
    // Initialize immediately and on retries
    init();
    setTimeout(init, 100);
    setTimeout(init, 300);
    setTimeout(init, 500);
    setTimeout(init, 1000);
    
    // Keep button state updated
    setInterval(updateButtonState, 700);
    
    // Re-init on resize
    window.addEventListener('resize', () => {
        setTimeout(init, 100);
    });
    
    // Observer for Streamlit redraws
    const observer = new MutationObserver(init);
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log('VocalBrand: SUPREME Desktop toggle initialized! ✓');
})();
