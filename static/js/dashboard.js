// Dashboard JavaScript for YouTube Automation Platform

$(document).ready(function() {
    let automationRunning = false;
    let logsUpdateInterval;
    let progressInterval;

    // Initialize dashboard
    initializeDashboard();

    // Automation Controls
    $('#startAutomation').on('click', function() {
        startAutomation();
    });

    $('#stopAutomation').on('click', function() {
        stopAutomation();
    });

    // Account Management
    $('#saveInstagramAccount').on('click', function() {
        addInstagramAccount();
    });

    $('#saveYouTubeAccount').on('click', function() {
        addYouTubeAccount();
    });

    // Refresh Data
    $('#refreshData').on('click', function() {
        refreshDashboardData();
    });

    // Initialize real-time updates
    startRealTimeUpdates();

    function initializeDashboard() {
        // Add loading animation to stats cards
        $('.card-body h4').each(function() {
            $(this).addClass('counter');
            $(this).attr('data-count', $(this).text());
            $(this).text('0');
        });

        // Animate counters
        setTimeout(function() {
            $('.counter').each(function() {
                var $this = $(this);
                var countTo = parseInt($this.attr('data-count')) || 0;
                
                $({ countNum: 0 }).animate({
                    countNum: countTo
                }, {
                    duration: 1500,
                    easing: 'swing',
                    step: function() {
                        $this.text(Math.floor(this.countNum));
                    },
                    complete: function() {
                        $this.text(this.countNum);
                    }
                });
            });
        }, 500);

        // Initialize tooltips
        $('[data-bs-toggle="tooltip"]').tooltip();

        // Add hover effects to table rows
        $('#reelsTable tr').hover(
            function() {
                $(this).addClass('table-active');
            },
            function() {
                $(this).removeClass('table-active');
            }
        );
    }

    function startAutomation() {
        if (automationRunning) {
            showToast('Automation is already running!', 'warning');
            return;
        }

        var $btn = $('#startAutomation');
        var originalText = $btn.html();
        
        $btn.prop('disabled', true);
        $btn.html('<i class="fas fa-spinner fa-spin me-2"></i>Starting...');

        $.ajax({
            url: '/api/start_automation',
            method: 'POST',
            success: function(response) {
                if (response.success) {
                    automationRunning = true;
                    updateAutomationStatus(true);
                    showToast('Automation started successfully!', 'success');
                    startProgressAnimation();
                } else {
                    showToast(response.message || 'Failed to start automation', 'error');
                }
            },
            error: function() {
                showToast('Error starting automation', 'error');
            },
            complete: function() {
                $btn.prop('disabled', false);
                $btn.html(originalText);
            }
        });
    }

    function stopAutomation() {
        if (!automationRunning) {
            showToast('Automation is not running!', 'warning');
            return;
        }

        var $btn = $('#stopAutomation');
        var originalText = $btn.html();
        
        $btn.prop('disabled', true);
        $btn.html('<i class="fas fa-spinner fa-spin me-2"></i>Stopping...');

        $.ajax({
            url: '/api/stop_automation',
            method: 'POST',
            success: function(response) {
                if (response.success) {
                    automationRunning = false;
                    updateAutomationStatus(false);
                    showToast('Automation stopped successfully!', 'success');
                    stopProgressAnimation();
                } else {
                    showToast(response.message || 'Failed to stop automation', 'error');
                }
            },
            error: function() {
                showToast('Error stopping automation', 'error');
            },
            complete: function() {
                $btn.prop('disabled', false);
                $btn.html(originalText);
            }
        });
    }

    function addInstagramAccount() {
        var username = $('#instagramUsername').val();
        var password = $('#instagramPassword').val();

        if (!username || !password) {
            showToast('Please fill in all fields', 'warning');
            return;
        }

        var $btn = $('#saveInstagramAccount');
        var originalText = $btn.html();
        
        $btn.prop('disabled', true);
        $btn.html('<i class="fas fa-spinner fa-spin me-2"></i>Saving...');

        $.ajax({
            url: '/api/add_instagram_account',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                username: username,
                password: password
            }),
            success: function(response) {
                if (response.success) {
                    showToast('Instagram account added successfully!', 'success');
                    $('#addInstagramModal').modal('hide');
                    $('#instagramUsername').val('');
                    $('#instagramPassword').val('');
                    refreshDashboardData();
                } else {
                    showToast('Failed to add Instagram account', 'error');
                }
            },
            error: function() {
                showToast('Error adding Instagram account', 'error');
            },
            complete: function() {
                $btn.prop('disabled', false);
                $btn.html(originalText);
            }
        });
    }

    function addYouTubeAccount() {
        var email = $('#youtubeEmail').val();
        var password = $('#youtubePassword').val();

        if (!email || !password) {
            showToast('Please fill in all fields', 'warning');
            return;
        }

        var $btn = $('#saveYouTubeAccount');
        var originalText = $btn.html();
        
        $btn.prop('disabled', true);
        $btn.html('<i class="fas fa-spinner fa-spin me-2"></i>Saving...');

        $.ajax({
            url: '/api/add_youtube_account',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                email: email,
                password: password
            }),
            success: function(response) {
                if (response.success) {
                    showToast('YouTube account added successfully!', 'success');
                    $('#addYouTubeModal').modal('hide');
                    $('#youtubeEmail').val('');
                    $('#youtubePassword').val('');
                    refreshDashboardData();
                } else {
                    showToast('Failed to add YouTube account', 'error');
                }
            },
            error: function() {
                showToast('Error adding YouTube account', 'error');
            },
            complete: function() {
                $btn.prop('disabled', false);
                $btn.html(originalText);
            }
        });
    }

    function refreshDashboardData() {
        var $btn = $('#refreshData');
        var originalText = $btn.html();
        
        $btn.prop('disabled', true);
        $btn.html('<i class="fas fa-spinner fa-spin me-2"></i>Refreshing...');

        // Simulate data refresh
        setTimeout(function() {
            updateStats();
            updateLogs();
            $btn.prop('disabled', false);
            $btn.html(originalText);
            showToast('Dashboard data refreshed!', 'success');
        }, 2000);
    }

    function updateAutomationStatus(running) {
        var $status = $('#automationStatus');
        var $statusText = $('#automationStatusText');
        
        if (running) {
            $status.removeClass('bg-success').addClass('bg-warning');
            $status.html('<i class="fas fa-play me-1"></i>Automation Running');
            $statusText.text('Automation is currently processing reels...');
        } else {
            $status.removeClass('bg-warning').addClass('bg-success');
            $status.html('<i class="fas fa-play me-1"></i>Automation Ready');
            $statusText.text('Automation is ready to start');
        }
    }

    function startProgressAnimation() {
        var progress = 0;
        progressInterval = setInterval(function() {
            progress += Math.random() * 10;
            if (progress > 100) progress = 100;
            
            $('#automationProgress').css('width', progress + '%');
            $('#automationProgress').attr('aria-valuenow', Math.floor(progress));
            
            if (progress >= 100) {
                clearInterval(progressInterval);
            }
        }, 2000);
    }

    function stopProgressAnimation() {
        if (progressInterval) {
            clearInterval(progressInterval);
        }
        $('#automationProgress').css('width', '0%');
        $('#automationProgress').attr('aria-valuenow', 0);
    }

    function startRealTimeUpdates() {
        // Update logs every 5 seconds
        logsUpdateInterval = setInterval(function() {
            updateLogs();
        }, 5000);

        // Update stats every 30 seconds
        setInterval(function() {
            updateStats();
        }, 30000);
    }

    function updateLogs() {
        $.ajax({
            url: '/api/get_logs',
            method: 'GET',
            success: function(response) {
                var $container = $('#logsContainer');
                $container.empty();
                
                response.forEach(function(log) {
                    var badgeClass = log.level === 'success' ? 'bg-success' : 
                                   log.level === 'error' ? 'bg-danger' : 'bg-info';
                    
                    var logEntry = $(`
                        <div class="log-entry p-3 border-bottom">
                            <div class="d-flex justify-content-between align-items-start">
                                <div class="flex-grow-1">
                                    <div class="log-message">${log.message}</div>
                                    <small class="text-muted">${log.created_at}</small>
                                </div>
                                <span class="badge ${badgeClass} ms-2">${log.level}</span>
                            </div>
                        </div>
                    `);
                    
                    $container.prepend(logEntry);
                });
                
                // Limit to 20 log entries
                if ($container.children().length > 20) {
                    $container.children().slice(20).remove();
                }
            },
            error: function() {
                console.log('Failed to update logs');
            }
        });
    }

    function updateStats() {
        // Simulate updating stats
        var totalViews = Math.floor(Math.random() * 10000) + 1000;
        $('#totalViews').text(totalViews.toLocaleString());
        
        // Update reel stats randomly
        $('#reelsTable tr').each(function() {
            var $row = $(this);
            var $views = $row.find('td:eq(2)');
            var $likes = $row.find('td:eq(3)');
            var $comments = $row.find('td:eq(4)');
            
            if ($views.length) {
                var currentViews = parseInt($views.text()) || 0;
                var newViews = currentViews + Math.floor(Math.random() * 50);
                $views.text(newViews);
            }
            
            if ($likes.length) {
                var currentLikes = parseInt($likes.text()) || 0;
                var newLikes = currentLikes + Math.floor(Math.random() * 10);
                $likes.text(newLikes);
            }
            
            if ($comments.length) {
                var currentComments = parseInt($comments.text()) || 0;
                var newComments = currentComments + Math.floor(Math.random() * 5);
                $comments.text(newComments);
            }
        });
    }

    // Modal event handlers
    $('#addInstagramModal').on('hidden.bs.modal', function() {
        $('#instagramUsername').val('');
        $('#instagramPassword').val('');
    });

    $('#addYouTubeModal').on('hidden.bs.modal', function() {
        $('#youtubeEmail').val('');
        $('#youtubePassword').val('');
    });

    // Keyboard shortcuts for dashboard
    $(document).keydown(function(e) {
        // Space to start/stop automation
        if (e.keyCode === 32 && !$(e.target).is('input, textarea')) {
            e.preventDefault();
            if (automationRunning) {
                stopAutomation();
            } else {
                startAutomation();
            }
        }
        
        // R to refresh data
        if (e.keyCode === 82 && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            refreshDashboardData();
        }
    });

    // Add real-time notifications
    function addNotification(message, type = 'info') {
        var icon = type === 'success' ? 'check-circle' : 
                   type === 'error' ? 'exclamation-circle' : 
                   type === 'warning' ? 'exclamation-triangle' : 'info-circle';
        
        var notification = $(`
            <div class="alert alert-${type} alert-dismissible fade show position-fixed" 
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
    }

    // Cleanup on page unload
    $(window).on('beforeunload', function() {
        if (logsUpdateInterval) {
            clearInterval(logsUpdateInterval);
        }
        if (progressInterval) {
            clearInterval(progressInterval);
        }
    });

    // Initialize with sample data if no data exists
    if ($('#reelsTable tr').length === 0) {
        addSampleData();
    }

    // Thumbnail Generator Functionality
    $('.template-btn').on('click', function() {
        var title = $(this).data('title');
        $('#thumbnailTitle').val(title);
    });

    $('#generateThumbnail').on('click', function() {
        var title = $('#thumbnailTitle').val();
        var style = $('#thumbnailStyle').val();
        
        if (!title) {
            showToast('Please enter a title for your thumbnail!', 'warning');
            return;
        }
        
        var $btn = $(this);
        var originalText = $btn.html();
        
        $btn.prop('disabled', true);
        $btn.html('<i class="fas fa-spinner fa-spin me-2"></i>Creating EPIC Thumbnail...');
        
        // Show loading in preview
        $('#thumbnailPreview').html('<div class="thumbnail-loading"></div>');
        $('#thumbnailActions').hide();
        
        $.ajax({
            url: '/api/generate_thumbnail',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                title: title,
                style: style
            }),
            success: function(response) {
                if (response.success) {
                    // Display thumbnail
                    $('#thumbnailPreview').html(`
                        <img src="${response.thumbnail_base64}" alt="Generated Thumbnail" class="thumbnail-success">
                    `);
                    
                    // Show action buttons
                    $('#thumbnailActions').show();
                    
                    // Store thumbnail path for download
                    $('#downloadThumbnail').data('path', response.thumbnail_path);
                    $('#downloadThumbnail').data('base64', response.thumbnail_base64);
                    
                    showToast(response.message, 'success');
                } else {
                    showToast(response.message, 'error');
                    $('#thumbnailPreview').html(`
                        <div class="text-center text-danger py-5">
                            <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                            <p>Failed to generate thumbnail</p>
                        </div>
                    `);
                }
            },
            error: function() {
                showToast('Error generating thumbnail', 'error');
                $('#thumbnailPreview').html(`
                    <div class="text-center text-danger py-5">
                        <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                        <p>Error generating thumbnail</p>
                    </div>
                `);
            },
            complete: function() {
                $btn.prop('disabled', false);
                $btn.html(originalText);
            }
        });
    });

    $('#downloadThumbnail').on('click', function() {
        var base64 = $(this).data('base64');
        if (base64) {
            // Create download link
            var link = document.createElement('a');
            link.href = base64;
            link.download = 'epic_youtube_thumbnail.jpg';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showToast('Thumbnail downloaded successfully!', 'success');
        }
    });

    $('#useForVideo').on('click', function() {
        var path = $(this).data('path');
        if (path) {
            // Add to reels table or use for current video
            showToast('Thumbnail applied to video!', 'success');
            $('#thumbnailGeneratorModal').modal('hide');
        }
    });

    // Auto-generate random title suggestions
    function generateRandomTitle() {
        var templates = [
            "INSANE Hindi Comedy That Will Make You CRY! 😂",
            "EPIC Gaming Moment You Won't Believe! 🎮", 
            "OMG This Vlog Will BLOW YOUR MIND! 🔥",
            "CRAZY Dance Challenge Gone Wrong! 💃",
            "AMAZING Cooking Hack That Actually Works! 👨‍🍳",
            "WOW This Reaction is PURE GOLD! ⚡",
            "INSANE Prank That Went Too Far! 😱",
            "EPIC Fail That Made Me Famous! 🏆",
            "MIND-BLOWING Secret Revealed! 🤯",
            "UNBELIEVABLE Transformation! ✨",
            "CRAZY Challenge That Broke the Internet! 🌐",
            "EPIC Comeback That Shocked Everyone! 💪"
        ];
        
        var randomTitle = templates[Math.floor(Math.random() * templates.length)];
        $('#thumbnailTitle').val(randomTitle);
    }

    // Add random title generator button
    $('#thumbnailTitle').after(`
        <button type="button" class="btn btn-outline-info btn-sm mt-2" id="randomTitleBtn">
            <i class="fas fa-dice me-1"></i>Generate Random Title
        </button>
    `);

    $('#randomTitleBtn').on('click', function() {
        generateRandomTitle();
    });

    // Instagram Account Creation
    $('#createInstagramAccount').on('click', function() {
        var usernamePrefix = $('#usernamePrefix').val();
        var accountType = $('#accountType').val();
        
        if (!usernamePrefix) {
            showToast('Please enter a username prefix!', 'warning');
            return;
        }
        
        var $btn = $(this);
        var originalText = $btn.html();
        
        $btn.prop('disabled', true);
        $btn.html('<i class="fas fa-spinner fa-spin me-2"></i>Creating Account...');
        
        $.ajax({
            url: '/api/create_instagram_account',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                username_prefix: usernamePrefix,
                account_type: accountType
            }),
            success: function(response) {
                if (response.success) {
                    showToast(response.message, 'success');
                    
                    // Show account details
                    var accountDetails = `
                        <div class="alert alert-success">
                            <h6><i class="fas fa-check-circle me-2"></i>Instagram Account Created Successfully!</h6>
                            <p><strong>Username:</strong> @${response.account.username}</p>
                            <p><strong>Password:</strong> ${response.account.password}</p>
                            <small class="text-muted">This account will be used to watch reels from target accounts</small>
                        </div>
                    `;
                    
                    $('#createInstagramForm').prepend(accountDetails);
                    
                    // Refresh accounts list
                    refreshInstagramAccountsList();
                } else {
                    showToast(response.message || 'Failed to create Instagram account', 'error');
                }
            },
            error: function(xhr) {
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    showToast(xhr.responseJSON.message, 'error');
                } else {
                    showToast('Error creating Instagram account', 'error');
                }
            },
            complete: function() {
                $btn.prop('disabled', false);
                $btn.html(originalText);
            }
        });
    });

    function refreshInstagramAccountsList() {
        $.ajax({
            url: '/api/get_instagram_accounts',
            method: 'GET',
            success: function(response) {
                var html = '';
                if (response.length > 0) {
                    response.forEach(function(account) {
                        var statusBadge = account.login_status === 'active' ? 
                            '<span class="badge bg-success">Active</span>' : 
                            '<span class="badge bg-warning">New</span>';
                        
                        html += `
                            <div class="card mb-2 instagram-account-item" data-id="${account.id}">
                                <div class="card-body p-3">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div>
                                            <h6 class="mb-1">@${account.username}</h6>
                                            <small class="text-muted">Reel Watcher Account</small>
                                            <br>
                                            <small class="text-muted">Status: ${account.login_status}</small>
                                        </div>
                                        <div>
                                            <button class="btn btn-sm btn-outline-primary me-2" onclick="testInstagramLogin(${account.id})">
                                                <i class="fas fa-sign-in-alt"></i> Test Login
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger" onclick="removeInstagramAccount(${account.id})">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                } else {
                    html = `
                        <div class="text-center text-muted py-4">
                            <i class="fab fa-instagram fa-3x mb-3"></i>
                            <p>No Instagram account created</p>
                            <small>Create your Instagram account to start watching reels</small>
                        </div>
                    `;
                }
                $('#instagramAccountsList').html(html);
            },
            error: function() {
                showToast('Error loading Instagram account', 'error');
            }
        });
    }

    // Test Instagram login function
    window.testInstagramLogin = function(accountId) {
        var $btn = $(`[onclick="testInstagramLogin(${accountId})"]`);
        var originalText = $btn.html();
        
        $btn.prop('disabled', true);
        $btn.html('<i class="fas fa-spinner fa-spin me-2"></i>Testing...');
        
        $.ajax({
            url: `/api/test_instagram_login/${accountId}`,
            method: 'POST',
            success: function(response) {
                if (response.success) {
                    showToast(response.message, 'success');
                } else {
                    showToast(response.message, 'error');
                }
                refreshInstagramAccountsList();
            },
            error: function() {
                showToast('Error testing login', 'error');
            },
            complete: function() {
                $btn.prop('disabled', false);
                $btn.html(originalText);
            }
        });
    };

    // Remove Instagram account function
    window.removeInstagramAccount = function(accountId) {
        if (confirm('Are you sure you want to remove this Instagram account?')) {
            // Add remove functionality here
            showToast('Instagram account removed', 'success');
            refreshInstagramAccountsList();
        }
    };

    // Target Account Management
    $('#addTargetAccount').on('click', function() {
        var username = $('#targetUsername').val();
        var accountType = $('#accountType').val();
        
        if (!username) {
            showToast('Please enter an Instagram username!', 'warning');
            return;
        }
        
        var $btn = $(this);
        var originalText = $btn.html();
        
        $btn.prop('disabled', true);
        $btn.html('<i class="fas fa-spinner fa-spin me-2"></i>Adding...');
        
        $.ajax({
            url: '/api/add_target_account',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                username: username,
                account_type: accountType
            }),
            success: function(response) {
                if (response.success) {
                    showToast(response.message, 'success');
                    $('#targetUsername').val('');
                    refreshTargetAccountsList();
                } else {
                    showToast('Failed to add target account', 'error');
                }
            },
            error: function() {
                showToast('Error adding target account', 'error');
            },
            complete: function() {
                $btn.prop('disabled', false);
                $btn.html(originalText);
            }
        });
    });

    function refreshTargetAccountsList() {
        $.ajax({
            url: '/api/get_target_accounts',
            method: 'GET',
            success: function(response) {
                var html = '';
                if (response.length > 0) {
                    response.forEach(function(account) {
                        html += `
                            <div class="card mb-2 target-account-item" data-id="${account.id}">
                                <div class="card-body p-3">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div>
                                            <h6 class="mb-1">@${account.username}</h6>
                                            <small class="text-muted">${account.account_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</small>
                                        </div>
                                        <div>
                                            <span class="badge bg-success me-2">Active</span>
                                            <button class="btn btn-sm btn-outline-danger" onclick="removeTargetAccount(${account.id})">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                } else {
                    html = `
                        <div class="text-center text-muted py-4">
                            <i class="fas fa-target fa-3x mb-3"></i>
                            <p>No target accounts configured</p>
                            <small>Add Instagram accounts to start monitoring their content</small>
                        </div>
                    `;
                }
                $('#targetAccountsList').html(html);
            },
            error: function() {
                showToast('Error loading target accounts', 'error');
            }
        });
    }

    // Remove target account function
    window.removeTargetAccount = function(accountId) {
        if (confirm('Are you sure you want to remove this account from monitoring?')) {
            $.ajax({
                url: `/api/remove_target_account/${accountId}`,
                method: 'DELETE',
                success: function(response) {
                    if (response.success) {
                        showToast(response.message, 'success');
                        refreshTargetAccountsList();
                    } else {
                        showToast('Failed to remove account', 'error');
                    }
                },
                error: function() {
                    showToast('Error removing account', 'error');
                }
            });
        }
    };

    // Thumbnail preview function
    window.previewThumbnail = function(src) {
        // Create modal for thumbnail preview
        var modal = $(`
            <div class="modal fade" id="thumbnailPreviewModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-warning text-dark">
                            <h5 class="modal-title">
                                <i class="fas fa-eye me-2"></i>Thumbnail Preview
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body text-center">
                            <img src="${src}" class="img-fluid rounded" alt="Thumbnail Preview">
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-success" onclick="downloadThumbnail('${src}')">
                                <i class="fas fa-download me-2"></i>Download
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `);
        
        $('body').append(modal);
        modal.modal('show');
        
        modal.on('hidden.bs.modal', function() {
            modal.remove();
        });
    };

    // Download thumbnail function
    window.downloadThumbnail = function(src) {
        var link = document.createElement('a');
        link.href = src;
        link.download = 'epic_youtube_thumbnail.jpg';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showToast('Thumbnail downloaded successfully!', 'success');
    };
});

function addSampleData() {
    var sampleReels = [
        {
            title: 'Amazing Hindi Comedy Reel',
            status: 'processed',
            views: 1250,
            likes: 89,
            comments: 12,
            date: '2024-01-15'
        },
        {
            title: 'Viral Dance Challenge',
            status: 'processing',
            views: 890,
            likes: 67,
            comments: 8,
            date: '2024-01-14'
        },
        {
            title: 'Cooking Tips in Hindi',
            status: 'processed',
            views: 2100,
            likes: 156,
            comments: 23,
            date: '2024-01-13'
        }
    ];

    var $table = $('#reelsTable');
    sampleReels.forEach(function(reel) {
        var row = $(`
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <img src="/static/images/default-thumbnail.jpg" 
                             class="rounded me-2" style="width: 40px; height: 40px; object-fit: cover;">
                        <div>
                            <div class="fw-bold">${reel.title}</div>
                            <small class="text-muted">instagram.com/sample...</small>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="badge bg-${reel.status === 'processed' ? 'success' : 'warning'}">
                        ${reel.status}
                    </span>
                </td>
                <td>${reel.views}</td>
                <td>${reel.likes}</td>
                <td>${reel.comments}</td>
                <td>${reel.date}</td>
            </tr>
        `);
        $table.append(row);
    });
}