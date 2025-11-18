console.log("MoazTech script loaded");

// ============================
// Admin Credentials
// ============================
const ADMIN_EMAIL = "admin@moaztec.com";
const ADMIN_PASSWORD = "admin123";

// ============================
// Get Logged-in User
// ============================
let currentUser = JSON.parse(localStorage.getItem("currentUser")) || null;

// ============================
// LOGIN FUNCTION
// ============================
function loginUser(email, password) {
    let isAdmin = false;
    if (email === ADMIN_EMAIL && password === ADMIN_PASSWORD) {
        isAdmin = true;
    }

    currentUser = {
        email: email,
        isAdmin: isAdmin
    };
    localStorage.setItem("currentUser", JSON.stringify(currentUser));
}

// ============================
// LOGOUT FUNCTION
// ============================
function logoutUser() {
    localStorage.removeItem("currentUser");
    window.location.href = "/";
}

// ============================
// ADMIN LINK CHECK
// ============================
document.addEventListener("DOMContentLoaded", function () {
    const adminLink = document.getElementById("adminLink");
    if (!adminLink) return;

    if (!currentUser || currentUser.isAdmin !== true) {
        // If not admin, prevent default and show message box
        adminLink.addEventListener("click", function (e) {
            e.preventDefault();
            openMessageBox();
        });
    } else {
        adminLink.style.display = "block";
    }
});

// ============================
// MESSAGE BOX FUNCTIONS
// ============================
function openMessageBox() {
    const box = document.getElementById("messageFormContainer");
    if (box) box.style.display = "flex";
}

function closeMessageBox() {
    const box = document.getElementById("messageFormContainer");
    if (box) box.style.display = "none";
}

// ============================
// MESSAGE SEND BUTTON
// ============================
document.addEventListener("DOMContentLoaded", function () {
    const msgForm = document.getElementById("sendMessageForm");
    if (msgForm) {
        msgForm.addEventListener("submit", function (e) {
            e.preventDefault();
            let text = document.getElementById("userMessage").value.trim();
            if (text.length < 5) {
                alert("Please type a detailed message.");
                return;
            }
            alert("Your message has been sent to Admin successfully.");
            closeMessageBox();
            msgForm.reset();
        });
    }
});
