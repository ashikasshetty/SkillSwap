// ===================================================================
// SKILLSWAP - CORE CLIENT LOGIC & THEME CONTROLLER
// Supports Persistent Dark / Light Mode with localStorage
// Full Mobile Touch & Keyboard Accessibility
// ===================================================================

(function() {
  // Theme Management
  const THEME_STORAGE_KEY = 'skillswap-theme';

  function getPreferredTheme() {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    if (savedTheme) {
      return savedTheme;
    }
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);

    // Update toggle icons
    const toggleBtns = document.querySelectorAll('.theme-toggle-btn');
    toggleBtns.forEach(btn => {
      const icon = btn.querySelector('i');
      if (icon) {
        if (theme === 'dark') {
          icon.className = 'fas fa-sun';
          btn.setAttribute('title', 'Switch to Light Mode');
          btn.setAttribute('aria-label', 'Switch to Light Mode');
        } else {
          icon.className = 'fas fa-moon';
          btn.setAttribute('title', 'Switch to Dark Mode');
          btn.setAttribute('aria-label', 'Switch to Dark Mode');
        }
      }
    });

    // Notify any active charts of theme change
    window.dispatchEvent(new CustomEvent('skillswap:themechange', { detail: { theme } }));
  }

  // Initialize theme immediately on page execution
  const currentTheme = getPreferredTheme();
  applyTheme(currentTheme);

  // Expose global helpers
  window.toggleTheme = function() {
    const active = document.documentElement.getAttribute('data-theme') || 'light';
    const next = active === 'dark' ? 'light' : 'dark';
    applyTheme(next);
  };

  window.setTheme = function(theme) {
    if (theme === 'light' || theme === 'dark') {
      applyTheme(theme);
    }
  };

  // DOM Content Loaded Handler
  document.addEventListener('DOMContentLoaded', () => {
    // 1. Attach theme toggle listener
    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
      themeBtn.addEventListener('click', (e) => {
        e.preventDefault();
        window.toggleTheme();
      });
    }

    // 2. Mobile navigation drawer toggle with outside-click & link-click auto-close
    const mobileBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');
    if (mobileBtn && navLinks) {
      mobileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = navLinks.classList.toggle('mobile-open');
        const icon = mobileBtn.querySelector('i');
        if (icon) {
          icon.className = isOpen ? 'fas fa-xmark' : 'fas fa-bars';
        }
      });

      // Close mobile menu when clicking outside
      document.addEventListener('click', (e) => {
        if (!navLinks.contains(e.target) && !mobileBtn.contains(e.target)) {
          if (navLinks.classList.contains('mobile-open')) {
            navLinks.classList.remove('mobile-open');
            const icon = mobileBtn.querySelector('i');
            if (icon) icon.className = 'fas fa-bars';
          }
        }
      });

      // Close mobile menu when clicking any link inside
      navLinks.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
          navLinks.classList.remove('mobile-open');
          const icon = mobileBtn.querySelector('i');
          if (icon) icon.className = 'fas fa-bars';
        });
      });
    }

    // 3. Auto & manual dismiss for alerts
    const alertCloses = document.querySelectorAll('.alert-close');
    alertCloses.forEach(btn => {
      btn.addEventListener('click', () => {
        const alert = btn.closest('.alert');
        if (alert) {
          alert.style.opacity = '0';
          alert.style.transform = 'translateY(-10px)';
          setTimeout(() => alert.remove(), 250);
        }
      });
    });

    // 4. Tab switching logic with horizontal touch-scroll centering
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-target');
        const parentContainer = btn.closest('.tabs-wrapper') || document;
        
        parentContainer.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        parentContainer.querySelectorAll('.tab-pane').forEach(p => p.style.display = 'none');
        
        btn.classList.add('active');
        const targetPane = document.getElementById(targetId);
        if (targetPane) {
          targetPane.style.display = 'block';
        }

        // Scroll tab into view on mobile
        btn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      });
    });

    // 5. Modal dialog helpers
    window.openModal = function(modalId) {
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.add('open');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
      }
    };

    window.closeModal = function(modalId) {
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.remove('open');
        modal.style.display = 'none';
        document.body.style.overflow = '';
      }
    };

    // Close modals when clicking backdrop
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          overlay.classList.remove('open');
          overlay.style.display = 'none';
          document.body.style.overflow = '';
        }
      });
    });

    // Close with Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.open').forEach(modal => {
          modal.classList.remove('open');
          modal.style.display = 'none';
          document.body.style.overflow = '';
        });
        if (navLinks && navLinks.classList.contains('mobile-open')) {
          navLinks.classList.remove('mobile-open');
          const icon = mobileBtn ? mobileBtn.querySelector('i') : null;
          if (icon) icon.className = 'fas fa-bars';
        }
      }
    });

    // 6. Star rating selector in review modal
    const starInputs = document.querySelectorAll('.rating-star-btn');
    const ratingHiddenInput = document.getElementById('selected-rating-value');
    if (starInputs.length > 0 && ratingHiddenInput) {
      starInputs.forEach(star => {
        star.addEventListener('click', (e) => {
          e.preventDefault();
          const value = parseInt(star.getAttribute('data-value'), 10);
          ratingHiddenInput.value = value;
          starInputs.forEach(s => {
            const sVal = parseInt(s.getAttribute('data-value'), 10);
            if (sVal <= value) {
              s.classList.add('active');
              s.querySelector('i').classList.replace('far', 'fas');
            } else {
              s.classList.remove('active');
              s.querySelector('i').classList.replace('fas', 'far');
            }
          });
        });
      });
    }

    // 7. Quick fill demo credentials on login page
    window.fillDemoLogin = function(email, password) {
      const emailField = document.getElementById('login-email');
      const passField = document.getElementById('login-password');
      if (emailField && passField) {
        emailField.value = email;
        passField.value = password;
        const btn = document.getElementById('login-submit-btn');
        if (btn) {
          btn.style.boxShadow = '0 0 0 3px rgba(212, 175, 119, 0.45)';
          btn.focus();
        }
      }
    };
  });
})();
