// Password validation function
function validatePassword(password) {
    const hasMinLength = password.length >= 8;
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    
    return {
        valid: hasMinLength && hasUpper && hasLower && hasNumber && hasSpecial,
        hasMinLength,
        hasUpper,
        hasLower,
        hasNumber,
        hasSpecial
    };
}

// Password input event listeners
function setupPasswordValidation() {
    const passwordInput = document.getElementById('password');
    const confirmInput = document.getElementById('confirm_password');
    
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const validation = validatePassword(this.value);
            
            // Update requirement indicators
            document.getElementById('req-length').className = validation.hasMinLength ? 'valid' : '';
            document.getElementById('req-upper').className = validation.hasUpper ? 'valid' : '';
            document.getElementById('req-lower').className = validation.hasLower ? 'valid' : '';
            document.getElementById('req-number').className = validation.hasNumber ? 'valid' : '';
            document.getElementById('req-special').className = validation.hasSpecial ? 'valid' : '';
            
            // Check password match if confirm has value
            if (confirmInput.value) {
                checkPasswordMatch();
            }
        });
    }
    
    if (confirmInput) {
        confirmInput.addEventListener('input', checkPasswordMatch);
    }
}

function checkPasswordMatch() {
    const password = document.getElementById('password').value;
    const confirm = document.getElementById('confirm_password').value;
    const matchIndicator = document.getElementById('password-match');
    
    if (password && confirm) {
        if (password === confirm) {
            matchIndicator.textContent = 'Passwords match';
            matchIndicator.className = 'hint valid';
        } else {
            matchIndicator.textContent = 'Passwords do not match';
            matchIndicator.className = 'hint error';
        }
    }
}

// Update notification function to use existing element
function showNotification(message, type) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification show ${type}`;
    
    setTimeout(() => {
        notification.classList.remove("show");
    }, 5000);
}

document.addEventListener("DOMContentLoaded", function() {
    const provinceSelect = document.getElementById("province");
    const municipalSelect = document.getElementById("municipal");
    const barangaySelect = document.getElementById("barangay");
    const registrationForm = document.getElementById("registrationForm");

    // Create hidden inputs for form submission
    const hiddenProvince = document.createElement("input");
    hiddenProvince.type = "hidden";
    hiddenProvince.name = "province";
    hiddenProvince.id = "hidden_province";
    registrationForm.appendChild(hiddenProvince);

    const hiddenMunicipal = document.createElement("input");
    hiddenMunicipal.type = "hidden";
    hiddenMunicipal.name = "municipal";
    hiddenMunicipal.id = "hidden_municipal";
    registrationForm.appendChild(hiddenMunicipal);

    const hiddenBarangay = document.createElement("input");
    hiddenBarangay.type = "hidden";
    hiddenBarangay.name = "barangay";
    hiddenBarangay.id = "hidden_barangay";
    registrationForm.appendChild(hiddenBarangay);

    // Helper functions
    function clearOptions(selectElement, placeholder) {
        selectElement.innerHTML = `<option value="">${placeholder}</option>`;
        selectElement.disabled = selectElement.id === "province" ? false : true;
    }

    function showLoading(selectElement) {
        const loadingOption = document.createElement("option");
        loadingOption.text = "Loading...";
        loadingOption.disabled = true;
        selectElement.appendChild(loadingOption);
        selectElement.disabled = true;
    }

    function showError(selectElement, message) {
        clearOptions(selectElement, message);
        selectElement.disabled = false;
    }

    function sortByName(a, b) {
        return a.name.localeCompare(b.name);
    }

    // Initialize
    municipalSelect.disabled = true;
    barangaySelect.disabled = true;

    // API Endpoints with fallbacks
    const API_ENDPOINTS = {
        provinces: [
            "https://psgc.gitlab.io/api/provinces/",
            "https://ph-locations-api.buonzz.com/v1/provinces",
            "https://api.lguplus.com.ph/psgc/provinces"
        ],
        municipalities: (code) => [
            `https://psgc.gitlab.io/api/provinces/${code}/cities-municipalities/`,
            `https://ph-locations-api.buonzz.com/v1/provinces/${code}/cities`,
            `https://api.lguplus.com.ph/psgc/provinces/${code}/cities`
        ],
        barangays: (code) => [
            `https://psgc.gitlab.io/api/cities-municipalities/${code}/barangays/`,
            `https://ph-locations-api.buonzz.com/v1/cities/${code}/barangays`,
            `https://api.lguplus.com.ph/psgc/cities/${code}/barangays`
        ],
        ncrCities: "https://psgc.gitlab.io/api/regions/130000000/cities-municipalities/"
    };

    // Load data from multiple API endpoints
    async function fetchWithFallbacks(urls, transformData) {
        for (const url of urls) {
            try {
                const response = await fetch(url);
                if (!response.ok) continue;
                const data = await response.json();
                return transformData ? transformData(data) : data;
            } catch (error) {
                console.error(`Failed to fetch ${url}:`, error);
                continue;
            }
        }
        throw new Error("All API endpoints failed");
    }

    // Load provinces including NCR
    async function loadProvinces() {
        showLoading(provinceSelect);
        
        try {
            // First try PSGC API
            const provinces = await fetchWithFallbacks(API_ENDPOINTS.provinces, data => {
                // Check if NCR is included
                const hasNCR = data.some(p => p.name.includes("National Capital Region"));
                if (!hasNCR) {
                    // Add NCR if missing
                    data.push({
                        code: "130000000",
                        name: "Metro Manila (NCR)",
                        isRegion: true
                    });
                }
                return data;
            });

            clearOptions(provinceSelect, "Select Province");
            provinces.sort(sortByName).forEach(province => {
                const option = document.createElement("option");
                option.value = JSON.stringify({
                    code: province.code || province.id,
                    name: province.name,
                    isRegion: province.isRegion || province.name.includes("NCR")
                });
                option.text = province.name;
                provinceSelect.appendChild(option);
            });
            
            provinceSelect.disabled = false;
        } catch (error) {
            showError(provinceSelect, "Error loading provinces");
            console.error("Failed to load provinces:", error);
        }
    }

    // Load municipalities/cities
    async function loadMunicipalities(provinceData) {
        showLoading(municipalSelect);
        
        try {
            let municipalities;
            
            if (provinceData.isRegion) {
                // Special handling for NCR
                municipalities = await fetch(API_ENDPOINTS.ncrCities)
                    .then(res => res.ok ? res.json() : Promise.reject());
            } else {
                // Regular provinces
                const endpoints = API_ENDPOINTS.municipalities(provinceData.code);
                municipalities = await fetchWithFallbacks(endpoints);
            }

            clearOptions(municipalSelect, "Select City/Municipality");
            municipalities.sort(sortByName).forEach(municipality => {
                const option = document.createElement("option");
                option.value = JSON.stringify({
                    code: municipality.code || municipality.id,
                    name: municipality.name
                });
                option.text = municipality.name;
                municipalSelect.appendChild(option);
            });
            
            municipalSelect.disabled = false;
        } catch (error) {
            showError(municipalSelect, "Error loading cities");
            console.error("Failed to load municipalities:", error);
        }
    }

    // Load barangays
    async function loadBarangays(cityCode) {
        showLoading(barangaySelect);
        
        try {
            const endpoints = API_ENDPOINTS.barangays(cityCode);
            const barangays = await fetchWithFallbacks(endpoints);
            
            clearOptions(barangaySelect, "Select Barangay");
            barangays.sort(sortByName).forEach(barangay => {
                const option = document.createElement("option");
                option.value = barangay.name || barangay.brgy_name;
                option.text = barangay.name || barangay.brgy_name;
                barangaySelect.appendChild(option);
            });
            
            barangaySelect.disabled = false;
        } catch (error) {
            showError(barangaySelect, "Error loading barangays");
            console.error("Failed to load barangays:", error);
        }
    }

    // Event listeners
    provinceSelect.addEventListener("change", function() {
        const selectedValue = this.value;
        clearOptions(municipalSelect, "Select City/Municipality");
        clearOptions(barangaySelect, "Select Barangay");
        
        if (!selectedValue) {
            hiddenProvince.value = "";
            hiddenMunicipal.value = "";
            hiddenBarangay.value = "";
            return;
        }

        const provinceData = JSON.parse(selectedValue);
        hiddenProvince.value = provinceData.name;
        loadMunicipalities(provinceData);
    });

    municipalSelect.addEventListener("change", function() {
        const selectedValue = this.value;
        clearOptions(barangaySelect, "Select Barangay");
        
        if (!selectedValue) {
            hiddenMunicipal.value = "";
            hiddenBarangay.value = "";
            return;
        }

        const cityData = JSON.parse(selectedValue);
        hiddenMunicipal.value = cityData.name;
        loadBarangays(cityData.code);
    });

    barangaySelect.addEventListener("change", function() {
        hiddenBarangay.value = this.value || "";
    });

    // Form submission with notification system
    registrationForm.addEventListener("submit", async function(e) {
        e.preventDefault();
        
        // Location validation
        if (!provinceSelect.value || !municipalSelect.value || !barangaySelect.value) {
            showNotification("Please select complete location information", "error");
            return;
        }

        // Password validation
        const password = document.getElementById("password");
        const confirm_password = document.getElementById("confirm_password");
        
        if (password && confirm_password && password.value !== confirm_password.value) {
            showNotification("Passwords do not match", "error");
            return;
        }

        // Submit form via fetch
        const formData = new FormData(registrationForm);
        
        try {
            const response = await fetch(registrationForm.action, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            showNotification(data.message, data.status);
            
            // If successful, optionally reset form
            if (data.status === 'success') {
                registrationForm.reset();
                clearOptions(provinceSelect, "Select Province");
                clearOptions(municipalSelect, "Select City/Municipality");
                clearOptions(barangaySelect, "Select Barangay");
                municipalSelect.disabled = true;
                barangaySelect.disabled = true;
                loadProvinces();
            }
        } catch (error) {
            showNotification('An error occurred. Please try again.', 'error');
            console.error("Form submission error:", error);
        }
    });

    // Notification function
    function showNotification(message, type) {
        const notification = document.createElement("div");
        notification.className = `notification show ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.remove("show");
            setTimeout(() => {
                notification.remove();
            }, 500);
        }, 5000);
    }

    // Initial load
    loadProvinces();
});