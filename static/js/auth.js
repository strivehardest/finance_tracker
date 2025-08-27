// Save JWT token after login
function saveToken(token) {
    localStorage.setItem("access_token", token);
}

// Get JWT token
function getToken() {
    return localStorage.getItem("access_token");
}

// Logout function
function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/login/"; // Redirect to login page
}
