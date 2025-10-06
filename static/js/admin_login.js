function sendOTP() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  if (!email.endsWith("@railtelindia.com")) {
    alert("Please enter a valid RailTel India email ID.");
    return;
  }

  // Send login form data to the Flask server
  fetch("/admin-login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      email: email,
      password: password,
    }),
  })
    .then((response) => response.text())
    .then((html) => {
      if (html.includes("OTP sent to your email address.")) {
        alert("OTP sent to your email address.");
        document.getElementById("loginForm").style.display = "none";
        document.getElementById("otpForm").style.display = "block";
      } else {
        alert("Invalid credentials. Please try again.");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function validateOTP() {
  const otp = document.getElementById("otp").value;

  fetch("/verify-admin-otp", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      otp: otp,
    }),
  })
    .then((response) => response.text())
    .then((html) => {
      if (html.includes("Admin login successful!")) {
        alert("Admin login successful!");
        window.location.href = "/admin";
      } else {
        alert("Invalid OTP. Please try again.");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
