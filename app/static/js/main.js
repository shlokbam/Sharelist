document.addEventListener('DOMContentLoaded', function() {
    // Close alert messages
    const closeButtons = document.querySelectorAll('.close-btn');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });

    // Auto-dismiss alert messages after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 500);
        });
    }, 5000);

    // Toggle password visibility
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        const toggleIcon = document.createElement('span');
        toggleIcon.innerHTML = '<i class="fas fa-eye"></i>';
        toggleIcon.className = 'password-toggle';
        toggleIcon.style.position = 'absolute';
        toggleIcon.style.right = '10px';
        toggleIcon.style.top = '50%';
        toggleIcon.style.transform = 'translateY(-50%)';
        toggleIcon.style.cursor = 'pointer';
        
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        wrapper.appendChild(toggleIcon);
        
        toggleIcon.addEventListener('click', function() {
            if (input.type === 'password') {
                input.type = 'text';
                toggleIcon.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                input.type = 'password';
                toggleIcon.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    });

    // Check URL validity in add link form
    const urlInput = document.querySelector('input[name="url"]');
    if (urlInput) {
        urlInput.addEventListener('blur', function() {
            const url = this.value.trim();
            if (url && !url.match(/^(http|https):\/\//)) {
                this.value = 'https://' + url;
            }
        });
    }

    // Enhance form labels to show required fields
    const requiredInputs = document.querySelectorAll('input[required], textarea[required]');
    requiredInputs.forEach(input => {
        const label = input.previousElementSibling;
        if (label && label.tagName === 'LABEL') {
            label.innerHTML += ' <span style="color: #e53e3e;">*</span>';
        }
    });

    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                document.querySelector(targetId).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Mystery Link Button animation
    const mysteryButtons = document.querySelectorAll('.mystery-btn, .mystery-button');
    mysteryButtons.forEach(button => {
        button.addEventListener('mouseover', function() {
            this.style.transform = 'rotate(5deg) scale(1.05)';
            this.style.transition = 'transform 0.3s ease';
            this.style.backgroundColor = '#6A1B9A'; // Darker purple on hover
        });
        
        button.addEventListener('mouseout', function() {
            this.style.transform = 'rotate(0) scale(1)';
            this.style.backgroundColor = '#8A2BE2'; // Back to normal purple
        });
        
        button.addEventListener('click', function() {
            // Add a loading spinner to indicate loading
            const originalContent = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Surprise coming...';
            
            // The actual redirection will happen via the server,
            // this is just to show a loading state before that happens
            setTimeout(() => {
                this.innerHTML = originalContent;
            }, 3000);
        });
    });

    // Handle all external links to open in Chrome Incognito mode
    // This will add a data attribute to all links that will be read by our browser extension
    // The actual opening in incognito requires either:
    // 1. A browser extension installed by the user
    // 2. A custom URL protocol handler
    
    // Add indicator to all external links for incognito mode
    const externalLinks = document.querySelectorAll('a[href^="http"], a[href^="https"]');
    externalLinks.forEach(link => {
        // Skip links that are navigation within the app
        if (link.getAttribute('href').includes(window.location.hostname)) {
            return;
        }
        
        // Add data attribute for incognito mode
        link.setAttribute('data-incognito', 'true');
        
        // Prevent default link behavior
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.getAttribute('href');
            
            // Method 1: Try to use a custom protocol (requires setup)
            // location.href = 'chrome-incognito://' + encodeURIComponent(url);
            
            // Method 2: Open a popup that instructs the user
            const incognitoInstructions = document.createElement('div');
            incognitoInstructions.style.position = 'fixed';
            incognitoInstructions.style.top = '50%';
            incognitoInstructions.style.left = '50%';
            incognitoInstructions.style.transform = 'translate(-50%, -50%)';
            incognitoInstructions.style.backgroundColor = '#121212';
            incognitoInstructions.style.border = '2px solid #8A2BE2';
            incognitoInstructions.style.borderRadius = '8px';
            incognitoInstructions.style.padding = '20px';
            incognitoInstructions.style.zIndex = '9999';
            incognitoInstructions.style.maxWidth = '400px';
            incognitoInstructions.style.boxShadow = '0 0 20px rgba(0,0,0,0.5)';
            
            incognitoInstructions.innerHTML = `
                <h3 style="color: #8A2BE2; margin-bottom: 15px;">Opening in Incognito Mode</h3>
                <p style="margin-bottom: 15px;">Please copy the link and paste it in Chrome's incognito window:</p>
                <input type="text" value="${url}" style="width: 100%; padding: 8px; margin-bottom: 15px; background: #333; color: #fff; border: 1px solid #8A2BE2; border-radius: 4px;" readonly onclick="this.select()">
                <div style="display: flex; gap: 10px; justify-content: center;">
                    <button id="copyLinkBtn" style="background: #8A2BE2; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer;">Copy Link</button>
                    <button id="openLinkBtn" style="background: #333; color: white; border: 1px solid #8A2BE2; padding: 8px 15px; border-radius: 4px; cursor: pointer;">Normal Open</button>
                    <button id="closeDialogBtn" style="background: #444; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer;">Close</button>
                </div>
                <p style="margin-top: 15px; font-size: 12px; color: #888;">Tip: You can open Chrome incognito with Ctrl+Shift+N (or Cmd+Shift+N on Mac)</p>
            `;
            
            document.body.appendChild(incognitoInstructions);
            
            // Add overlay
            const overlay = document.createElement('div');
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(0,0,0,0.7)';
            overlay.style.zIndex = '9998';
            document.body.appendChild(overlay);
            
            // Handle the copy button
            document.getElementById('copyLinkBtn').addEventListener('click', function() {
                const input = incognitoInstructions.querySelector('input');
                input.select();
                document.execCommand('copy');
                this.textContent = 'Copied!';
                setTimeout(() => {
                    this.textContent = 'Copy Link';
                }, 2000);
            });
            
            // Handle regular open button
            document.getElementById('openLinkBtn').addEventListener('click', function() {
                window.open(url, '_blank');
                document.body.removeChild(incognitoInstructions);
                document.body.removeChild(overlay);
            });
            
            // Handle close button
            document.getElementById('closeDialogBtn').addEventListener('click', function() {
                document.body.removeChild(incognitoInstructions);
                document.body.removeChild(overlay);
            });
            
            // Close on overlay click
            overlay.addEventListener('click', function() {
                document.body.removeChild(incognitoInstructions);
                document.body.removeChild(overlay);
            });
        });
        
        // Add incognito indicator to the link
        const linkText = link.textContent;
        const incognitoIcon = document.createElement('i');
        incognitoIcon.className = 'fas fa-user-secret';
        incognitoIcon.style.marginLeft = '5px';
        incognitoIcon.style.fontSize = '0.8em';
        incognitoIcon.style.color = '#8A2BE2';
        link.appendChild(incognitoIcon);
        
        // Add tooltip
        link.setAttribute('title', 'Opens in incognito mode');
    });
});