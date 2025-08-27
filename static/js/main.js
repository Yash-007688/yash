// Main JavaScript for YouTube Automation Platform

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add fade-in animation to cards
    $('.card').addClass('fade-in');

    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000);
        }
    });

    // Form validation
    $('form').on('submit', function(e) {
        var $form = $(this);
        var $submitBtn = $form.find('button[type="submit"]');
        var originalText = $submitBtn.text();
        
        // Show loading state
        $submitBtn.prop('disabled', true);
        $submitBtn.html('<i class="fas fa-spinner fa-spin me-2"></i>Processing...');
        
        // Re-enable after a delay (for demo purposes)
        setTimeout(function() {
            $submitBtn.prop('disabled', false);
            $submitBtn.text(originalText);
        }, 2000);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Add click to dismiss for alerts
    $('.alert').on('click', function() {
        $(this).fadeOut('slow');
    });

    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Add loading spinner to buttons
    $('.btn').on('click', function() {
        var $btn = $(this);
        if (!$btn.hasClass('no-spinner')) {
            var originalText = $btn.html();
            $btn.html('<i class="fas fa-spinner fa-spin me-2"></i>Loading...');
            
            setTimeout(function() {
                $btn.html(originalText);
            }, 2000);
        }
    });

    // Theme switcher (if implemented)
    $('.theme-switch').on('click', function() {
        $('body').toggleClass('dark-theme');
        localStorage.setItem('theme', $('body').hasClass('dark-theme') ? 'dark' : 'light');
    });

    // Check for saved theme preference
    if (localStorage.getItem('theme') === 'dark') {
        $('body').addClass('dark-theme');
    }

    // Add hover effects to cards
    $('.card').hover(
        function() {
            $(this).addClass('shadow-lg');
        },
        function() {
            $(this).removeClass('shadow-lg');
        }
    );

    // Initialize any charts or data visualizations
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }

    // Add keyboard shortcuts
    $(document).keydown(function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.keyCode === 75) {
            e.preventDefault();
            $('#searchInput').focus();
        }
        
        // Escape to close modals
        if (e.keyCode === 27) {
            $('.modal').modal('hide');
        }
    });

    // Add search functionality
    $('#searchInput').on('input', function() {
        var query = $(this).val().toLowerCase();
        $('.searchable').each(function() {
            var text = $(this).text().toLowerCase();
            if (text.includes(query)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });

    // Add copy to clipboard functionality
    $('.copy-btn').on('click', function() {
        var text = $(this).data('clipboard-text');
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copied to clipboard!', 'success');
        });
    });

    // Add file upload preview
    $('input[type="file"]').on('change', function() {
        var file = this.files[0];
        if (file) {
            var reader = new FileReader();
            reader.onload = function(e) {
                $('.file-preview').attr('src', e.target.result).show();
            };
            reader.readAsDataURL(file);
        }
    });

    // Add notification system
    window.showNotification = function(message, type = 'info') {
        var alertClass = 'alert-' + type;
        var icon = type === 'success' ? 'check-circle' : 
                   type === 'error' ? 'exclamation-circle' : 
                   type === 'warning' ? 'exclamation-triangle' : 'info-circle';
        
        var notification = $(`
            <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                <i class="fas fa-${icon} me-2"></i>${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        $('body').append(notification);
        
        setTimeout(function() {
            notification.fadeOut('slow', function() {
                $(this).remove();
            });
        }, 5000);
    };

    // Add toast notification system
    window.showToast = function(message, type = 'info') {
        var toastClass = type === 'success' ? 'bg-success' : 
                        type === 'error' ? 'bg-danger' : 
                        type === 'warning' ? 'bg-warning' : 'bg-info';
        
        var toast = $(`
            <div class="toast align-items-center ${toastClass} text-white border-0" 
                 style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `);
        
        $('body').append(toast);
        var bsToast = new bootstrap.Toast(toast[0]);
        bsToast.show();
        
        toast.on('hidden.bs.toast', function() {
            $(this).remove();
        });
    };

    // Add progress bar animation
    $('.progress-bar').each(function() {
        var $this = $(this);
        var percentage = $this.attr('aria-valuenow');
        $this.css('width', '0%');
        
        setTimeout(function() {
            $this.css('width', percentage + '%');
        }, 500);
    });

    // Add counter animation
    $('.counter').each(function() {
        var $this = $(this);
        var countTo = $this.attr('data-count');
        
        $({ countNum: 0 }).animate({
            countNum: countTo
        }, {
            duration: 2000,
            easing: 'swing',
            step: function() {
                $this.text(Math.floor(this.countNum));
            },
            complete: function() {
                $this.text(this.countNum);
            }
        });
    });

    // Add responsive table wrapper
    $('.table-responsive').each(function() {
        if ($(this).find('table').width() > $(this).width()) {
            $(this).addClass('table-scroll');
        }
    });

    // Add loading states for forms
    $('form').on('submit', function() {
        var $form = $(this);
        var $submitBtn = $form.find('button[type="submit"]');
        
        if ($submitBtn.length) {
            var originalText = $submitBtn.text();
            $submitBtn.prop('disabled', true);
            $submitBtn.html('<i class="fas fa-spinner fa-spin me-2"></i>Processing...');
            
            // Re-enable after form submission (you might want to do this in the success callback)
            setTimeout(function() {
                $submitBtn.prop('disabled', false);
                $submitBtn.text(originalText);
            }, 3000);
        }
    });
});

// Initialize charts function
function initializeCharts() {
    // This function would initialize any charts or data visualizations
    // Implementation depends on the charting library being used
    console.log('Charts initialized');
}

// Utility functions
window.utils = {
    formatNumber: function(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },
    
    formatDate: function(date) {
        return new Date(date).toLocaleDateString();
    },
    
    formatDateTime: function(date) {
        return new Date(date).toLocaleString();
    },
    
    debounce: function(func, wait, immediate) {
        var timeout;
        return function executedFunction() {
            var context = this;
            var args = arguments;
            var later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            var callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    },
    
    throttle: function(func, limit) {
        var inThrottle;
        return function() {
            var args = arguments;
            var context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};