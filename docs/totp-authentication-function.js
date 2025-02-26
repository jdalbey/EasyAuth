// Import the otpauth library via CDN script in your HTML:
// <script src="https://cdn.jsdelivr.net/npm/otpauth/dist/otpauth.umd.min.js"></script>

/**
 * Validates a TOTP code against a secret key
 * @param {string} code - The 6-digit code entered by the user
 * @param {string} secretKey - The secret key (without spaces)
 * @param {number} window - The time window to check (default: 1)
 * @returns {boolean} - Whether the code is valid
 */
function validateTOTP(code, secretKey, window = 1) {
  try {
    // Remove spaces from the secret key
    const cleanSecretKey = secretKey.replace(/\s+/g, '');
    
    // Create a new TOTP object
    const totp = new OTPAuth.TOTP({
      issuer: 'PayPal',
      label: 'someone@goodmail.com',
      algorithm: 'SHA1',
      digits: 6,
      period: 30,
      secret: OTPAuth.Secret.fromBase32(cleanSecretKey)
    });
    
    // Validate the token with a time window
    const delta = totp.validate({ token: code, window: window });
    
    // If delta is null, the token is invalid
    // Otherwise it returns the time step difference
    return delta !== null;
  } catch (error) {
    console.error('TOTP validation error:', error);
    return false;
  }
}

/**
 * Authenticates the user based on the 6-digit code entered in the form
 * @returns {boolean} - Whether authentication was successful
 */
function authenticateUser() {
  // Get all digit inputs
  const inputs = document.querySelectorAll('.digit');
  
  // Combine the values into a single code
  const code = Array.from(inputs).map(input => input.value).join('');
  
  // The secret key provided
  const secretKey = 'LQNV5JKCMWY2TROB';
  
  // Check if code is a valid 6-digit number
  if (!/^\d{6}$/.test(code)) {
    showAlert('Please enter a valid 6-digit code');
    return false;
  }
  
  // Show authenticating state
  const submitButton = document.getElementById('submit-button');
  const authButton = document.getElementById('auth-button');
  if (submitButton && authButton) {
    submitButton.style.display = 'none';
    authButton.style.display = 'block';
  }
  
  // Validate the TOTP code
  const isValid = validateTOTP(code, secretKey);

  if (isValid) {
    // Authentication successful
    window.location.href = nextPage; //'Setup2FA_5_LoginACK.html';
    return true;
  } else {
    // Authentication failed
    showAlert(code + ' is not the correct authentication code for someone@goodmail.com. Please try again.');
    

    // Reset the form
    inputs.forEach(input => {
      input.value = '';
    });
    inputs[0].focus();
    
    // Show the submit button again
    if (submitButton && authButton) {
      submitButton.style.display = 'block';
      authButton.style.display = 'none';
    }
    
    return false;
  }
}

/* Reset the input fields and submit button */
function resetForm() {
}
/**
 * Shows an alert message to the user
 * @param {string} message - The message to display
 */
function showAlert(message) {
  const alertBox = document.getElementById('alertBox');
  if (alertBox) {
    alertBox.textContent = message;
    alertBox.style.display = 'block';
    setTimeout(() => {
      alertBox.style.display = 'none';
    }, 4000);
  }
}

// Update the event listener to use the new authentication function
document.addEventListener('DOMContentLoaded', (event) => {
  const inputs = document.querySelectorAll('.digit');
  const submitButton = document.getElementById('submit-button');
  const timeout = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  inputs.forEach((input, index) => {
    input.addEventListener('input', (e) => {
      if (input.value.length === 1 && index < inputs.length - 1) {
        inputs[index + 1].focus();
      }
      if (index === inputs.length - 1 && input.value.length === 1) {
      timeout(500).then(() => {
            console.log('500ms has passed');
            authenticateUser();
        });
      }
    });

    input.addEventListener('paste', (e) => {
      const paste = (e.clipboardData || window.clipboardData).getData('text');
      if (paste.length === 6) {
        inputs.forEach((input, i) => {
          input.value = paste[i];
        });
      timeout(500).then(() => {
            console.log('500ms has passed');
            authenticateUser();
        });
      }
      e.preventDefault();
    });
  });

  if (submitButton) {
    submitButton.addEventListener('click', (e) => {
      e.preventDefault();
      authenticateUser();
    });
  }
});
