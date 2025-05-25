// Handle OTP request form submission
document.getElementById('forgot-password-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const button = document.getElementById('request-otp-button');
    
    // Show loading state
    button.querySelector('.button-text').style.display = 'none';
    button.querySelector('.spinner').style.display = 'inline-block';
    button.disabled = true;
    
    // Clear previous messages
    hideMessages();

    fetch('/request_otp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message);
            document.getElementById('email-display').textContent = email;
            showStep(2); // Show OTP step
        } else {
            showErrorMessage(data.message);
        }
    })
    .catch(error => {
        showErrorMessage('An error occurred, please try again.');
    })
    .finally(() => {
        // Reset button state
        button.querySelector('.button-text').style.display = 'inline-block';
        button.querySelector('.spinner').style.display = 'none';
        button.disabled = false;
    });
});

// Handle OTP verification
document.getElementById('verify-otp-button').addEventListener('click', function() {
    const email = document.getElementById('email').value;
    const otp = document.getElementById('otp').value;
    const button = document.getElementById('verify-otp-button');
    
    if (otp.length !== 6) {
        showErrorMessage('Please enter a valid 6-digit code.');
        return;
    }
    
    // Show loading state
    button.querySelector('.button-text').style.display = 'none';
    button.querySelector('.spinner').style.display = 'inline-block';
    button.disabled = true;
    
    // Clear previous messages
    hideMessages();

    fetch('/verify_otp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email, otp: otp })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message);
            showStep(3); // Show password reset step
        } else {
            showErrorMessage(data.message);
        }
    })
    .catch(error => {
        showErrorMessage('An error occurred, please try again.');
    })
    .finally(() => {
        // Reset button state
        button.querySelector('.button-text').style.display = 'inline-block';
        button.querySelector('.spinner').style.display = 'none';
        button.disabled = false;
    });
});

// Handle password reset
document.getElementById('reset-password-button').addEventListener('click', function() {
    const email = document.getElementById('email').value;
    const otp = document.getElementById('otp').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const button = document.getElementById('reset-password-button');
    
    if (newPassword.length < 8) {
        showErrorMessage('Password must be at least 8 characters long.');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showErrorMessage('Passwords do not match.');
        return;
    }
    
    // Show loading state
    button.querySelector('.button-text').style.display = 'none';
    button.querySelector('.spinner').style.display = 'inline-block';
    button.disabled = true;
    
    // Clear previous messages
    hideMessages();

    fetch('/reset_password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email, otp: otp, new_password: newPassword })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStep(4); // Show success step
        } else {
            showErrorMessage(data.message);
        }
    })
    .catch(error => {
        showErrorMessage('An error occurred, please try again.');
    })
    .finally(() => {
        // Reset button state
        button.querySelector('.button-text').style.display = 'inline-block';
        button.querySelector('.spinner').style.display = 'none';
        button.disabled = false;
    });
});

// Handle OTP resend
document.getElementById('resend-otp').addEventListener('click', function(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    
    fetch('/request_otp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage('A new OTP has been sent to your email.');
        } else {
            showErrorMessage(data.message);
        }
    })
    .catch(error => {
        showErrorMessage('An error occurred, please try again.');
    });
});

// Password strength indicator
document.getElementById('new-password').addEventListener('input', function() {
    updatePasswordStrength(this.value);
    checkPasswordMatch();
});

// Password match checker
document.getElementById('confirm-password').addEventListener('input', checkPasswordMatch);

function checkPasswordMatch() {
    const password = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const matchElement = document.getElementById('password-match');
    
    if (password && confirmPassword) {
        if (password === confirmPassword) {
            matchElement.style.display = 'flex';
            matchElement.style.color = '#4CAF50';
        } else {
            matchElement.style.display = 'flex';
            matchElement.style.color = '#f44336';
            matchElement.innerHTML = '<i class="fas fa-times"></i> Passwords do not match';
        }
    } else {
        matchElement.style.display = 'none';
    }
}

// Helper functions
function showStep(stepNumber) {
    // Hide all steps
    document.querySelectorAll('.form-step').forEach(step => {
        step.classList.remove('active');
    });
    
    // Update progress steps
    document.querySelectorAll('.step').forEach((step, index) => {
        if (index < stepNumber) {
            step.classList.add('completed');
            step.classList.add('active');
        } else if (index === stepNumber - 1) {
            step.classList.add('active');
            step.classList.remove('completed');
        } else {
            step.classList.remove('active');
            step.classList.remove('completed');
        }
    });
    
    // Show the current step
    const steps = [
        null, // No step 0
        'email-step',
        'otp-step',
        'password-step',
        'success-step'
    ];
    
    if (steps[stepNumber]) {
        document.getElementById(steps[stepNumber]).classList.add('active');
    }
}

function showSuccessMessage(message) {
    const element = document.getElementById('success-message');
    element.textContent = message;
    element.style.display = 'block';
    document.getElementById('error-message').style.display = 'none';
}

function showErrorMessage(message) {
    const element = document.getElementById('error-message');
    element.textContent = message;
    element.style.display = 'block';
    document.getElementById('success-message').style.display = 'none';
}

function hideMessages() {
    document.getElementById('error-message').style.display = 'none';
    document.getElementById('success-message').style.display = 'none';
}

function updatePasswordStrength(password) {
    const strengthBar = document.querySelector('.strength-bar');
    const strengthText = document.querySelector('.strength-text span');
    
    // Calculate strength
    let strength = 0;
    if (password.length > 0) strength += 1;
    if (password.length >= 8) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    
    // Update UI
    const width = (strength / 5) * 100;
    strengthBar.style.width = `${width}%`;
    
    // Update color and text
    if (password.length === 0) {
        strengthBar.style.backgroundColor = 'transparent';
        strengthText.textContent = '';
    } else if (strength <= 2) {
        strengthBar.style.backgroundColor = '#ff4d4d';
        strengthText.textContent = 'Weak';
    } else if (strength <= 3) {
        strengthBar.style.backgroundColor = '#ffa500';
        strengthText.textContent = 'Medium';
    } else {
        strengthBar.style.backgroundColor = '#4CAF50';
        strengthText.textContent = 'Strong';
    }
}