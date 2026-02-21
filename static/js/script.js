// Scholarship Filtering
document.addEventListener('DOMContentLoaded', function () {
    const typeFilter = document.getElementById('typeFilter');
    const levelFilter = document.getElementById('levelFilter');
    const searchInput = document.getElementById('searchInput');
    const scholarshipCards = document.querySelectorAll('.scholarship-card');
    const noResults = document.getElementById('noResults');

    if (typeFilter && levelFilter && searchInput) {
        // Filter function
        function filterScholarships() {
            const typeValue = typeFilter.value.toLowerCase();
            const levelValue = levelFilter.value.toLowerCase();
            const searchValue = searchInput.value.toLowerCase();
            let visibleCount = 0;

            scholarshipCards.forEach(card => {
                const cardType = card.getAttribute('data-type').toLowerCase();
                const cardLevel = card.getAttribute('data-level').toLowerCase();
                const cardText = card.textContent.toLowerCase();

                const typeMatch = !typeValue || cardType === typeValue;
                const levelMatch = !levelValue || cardLevel === levelValue;
                const searchMatch = !searchValue || cardText.includes(searchValue);

                if (typeMatch && levelMatch && searchMatch) {
                    card.style.display = 'block';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            // Show/hide no results message
            if (noResults) {
                noResults.style.display = visibleCount === 0 ? 'block' : 'none';
            }
        }

        // Add event listeners
        typeFilter.addEventListener('change', filterScholarships);
        levelFilter.addEventListener('change', filterScholarships);
        searchInput.addEventListener('input', filterScholarships);
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add animation to cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all cards
    document.querySelectorAll('.card, .feature-card, .stat-card').forEach(card => {
        observer.observe(card);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Character counter for textarea
    const essayTextarea = document.getElementById('essay');
    if (essayTextarea) {
        const counterDiv = document.createElement('div');
        counterDiv.className = 'text-muted text-end mt-1';
        counterDiv.innerHTML = '<small>Word count: <span id="wordCount">0</span></small>';
        essayTextarea.parentNode.appendChild(counterDiv);

        const wordCountSpan = document.getElementById('wordCount');

        essayTextarea.addEventListener('input', function () {
            const text = this.value.trim();
            const wordCount = text ? text.split(/\s+/).length : 0;
            wordCountSpan.textContent = wordCount;

            // Color coding based on word count
            if (wordCount < 500) {
                wordCountSpan.className = 'text-danger';
            } else if (wordCount > 1000) {
                wordCountSpan.className = 'text-warning';
            } else {
                wordCountSpan.className = 'text-success';
            }
        });
    }

    // Save form data to localStorage (for apply form)
    const applyForm = document.querySelector('form[action*="apply"]');
    if (applyForm) {
        // Load saved data
        const savedData = localStorage.getItem('scholarshipFormData');
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const input = applyForm.querySelector(`[name="${key}"]`);
                if (input && input.type !== 'email' && input.type !== 'text' && key !== 'name') {
                    input.value = data[key];
                }
            });
        }

        // Save data on input
        applyForm.addEventListener('input', function (e) {
            const formData = new FormData(applyForm);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            localStorage.setItem('scholarshipFormData', JSON.stringify(data));
        });

        // Clear saved data on successful submit
        applyForm.addEventListener('submit', function () {
            localStorage.removeItem('scholarshipFormData');
        });
    }

    // Navbar scroll effect (Handled in base.html)
    // Removed to prevent conflict and JS errors

    // Phone number formatting
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function (e) {
            // Allow digits, spaces, dashes, and plus sign
            let value = e.target.value.replace(/[^\d\s\-+]/g, '');
            e.target.value = value;
        });
    }

    // GPA validation
    const gpaInput = document.getElementById('gpa');
    if (gpaInput) {
        gpaInput.addEventListener('input', function (e) {
            let value = parseFloat(e.target.value);
            if (value > 10) {
                e.target.value = 10;
            } else if (value < 0) {
                e.target.value = 0;
            }
        });
    }
});

// Utility function to show toast notifications
function showToast(message, type = 'info') {
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'fixed bottom-6 right-6 z-[100] flex flex-col gap-3 pointer-events-none';
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');

    // Define colors based on type
    let bgColor = 'bg-white dark:bg-slate-800';
    let iconColor = 'text-primary';
    let icon = 'fa-info-circle';

    if (type === 'success') {
        iconColor = 'text-emerald-500';
        icon = 'fa-check-circle';
    } else if (type === 'danger' || type === 'error') {
        iconColor = 'text-rose-500';
        icon = 'fa-exclamation-circle';
    } else if (type === 'warning') {
        iconColor = 'text-amber-500';
        icon = 'fa-exclamation-triangle';
    }

    toast.className = `flex items-center gap-3 px-6 py-4 rounded-2xl shadow-2xl border border-slate-100 dark:border-slate-700 pointer-events-auto transform translate-y-10 opacity-0 transition-all duration-500 ${bgColor}`;

    toast.innerHTML = `
        <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-slate-50 dark:bg-slate-700/50 ${iconColor}">
            <i class="fas ${icon} text-lg"></i>
        </div>
        <div class="text-sm font-semibold text-slate-700 dark:text-slate-200 pr-4">${message}</div>
        <button class="ml-auto text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
            <i class="fas fa-times"></i>
        </button>
    `;

    toastContainer.appendChild(toast);

    // Close button logic
    const closeBtn = toast.querySelector('button');
    const closeToast = () => {
        toast.classList.add('translate-y-10', 'opacity-0');
        setTimeout(() => toast.remove(), 500);
    };
    closeBtn.onclick = closeToast;

    // Animate in
    requestAnimationFrame(() => {
        setTimeout(() => {
            toast.classList.remove('translate-y-10', 'opacity-0');
            toast.classList.add('translate-y-0', 'opacity-100');
        }, 10);
    });

    // Auto-remove
    setTimeout(closeToast, 4000);
}

// Count Up Animation
document.addEventListener('DOMContentLoaded', function () {
    const counters = document.querySelectorAll('.counter');
    const duration = 2000; // Animation duration in ms

    const animateCount = (counter) => {
        const targetAttr = counter.getAttribute('data-target');
        const suffix = counter.getAttribute('data-suffix') || '';
        const prefix = counter.getAttribute('data-prefix') || '';
        const decimals = targetAttr.includes('.') ? targetAttr.split('.')[1].length : 0;

        const target = parseFloat(targetAttr);
        const startTime = performance.now();

        const updateCount = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function for smooth animation
            const easeOutQuad = (t) => t * (2 - t);
            const currentCount = target * easeOutQuad(progress);

            if (decimals > 0) {
                counter.innerText = prefix + currentCount.toFixed(decimals) + suffix;
            } else {
                counter.innerText = prefix + Math.floor(currentCount) + suffix;
            }

            if (progress < 1) {
                requestAnimationFrame(updateCount);
            } else {
                counter.innerText = prefix + target + suffix;
            }
        };

        requestAnimationFrame(updateCount);
    };

    const observerOptions = {
        threshold: 0.5
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                animateCount(counter);
                observer.unobserve(counter);
            }
        });
    }, observerOptions);

    counters.forEach(counter => {
        observer.observe(counter);
    });
});