function toggleLeaderboard(activityId) {
  const table = document.getElementById(activityId);
  const isVisible = table.style.display === "block";

  // Hide all tables first
  document.querySelectorAll(".activity-table").forEach((el) => {
    el.style.display = "none";
  });

  // Toggle the clicked table
  if (!isVisible) {
    table.style.display = "block";
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const images = document.querySelectorAll(".carousel-images img");
  const totalImages = images.length;
  const carouselImages = document.querySelector(".carousel-images");
  const dotsContainer = document.querySelector(".carousel-dots");
  let currentIndex = 0;

  // Create dots dynamically
  for (let i = 0; i < totalImages; i++) {
    const dot = document.createElement("span");
    dot.classList.add("dot");
    if (i === 0) dot.classList.add("active");
    dotsContainer.appendChild(dot);

    // Add click event to each dot
    dot.addEventListener("click", () => {
      currentIndex = i;
      updateCarousel();
    });
  }

  const dots = document.querySelectorAll(".carousel-dots .dot");

  function updateCarousel() {
    const carouselWidth = document.querySelector(".carousel").clientWidth;
    const offset = -carouselWidth * currentIndex;
    carouselImages.style.transform = `translateX(${offset}px)`;

    // Update active dot
    dots.forEach((dot) => dot.classList.remove("active"));
    dots[currentIndex].classList.add("active");
  }

  // Auto-play functionality
  function autoPlay() {
    currentIndex = (currentIndex + 1) % totalImages;
    updateCarousel();
  }

  let autoPlayInterval = setInterval(autoPlay, 2000);

  // Add event listeners for navigation buttons
  document.querySelector(".carousel-btn.prev").addEventListener("click", () => {
    clearInterval(autoPlayInterval); // Reset autoplay
    currentIndex = (currentIndex - 1 + totalImages) % totalImages;
    updateCarousel();
    autoPlayInterval = setInterval(autoPlay, 2000);
  });

  document.querySelector(".carousel-btn.next").addEventListener("click", () => {
    clearInterval(autoPlayInterval); // Reset autoplay
    currentIndex = (currentIndex + 1) % totalImages;
    updateCarousel();
    autoPlayInterval = setInterval(autoPlay, 2000);
  });
});

// theme toggle

const themeToggle = document.getElementById("theme-toggle");
const themeLink = document.getElementById("theme-link"); // This is the link tag that controls the theme CSS
const videoBackground = document.getElementById("background-video"); // Video background element
const themeIcon = document.getElementById("theme-icon"); // Theme icon element

// Check for the user's last saved theme preference in localStorage
if (localStorage.getItem("theme") === "dark") {
  themeLink.setAttribute("href", "static/css/style-light.css"); // Set dark theme by default
  videoBackground.style.display = "block"; // Show the video in dark theme
  themeIcon.setAttribute("src", "static/image/dark.png"); // Set dark theme icon
} else {
  themeLink.setAttribute("href", "static/css/style.css"); // Set light theme by default
  videoBackground.style.display = "none"; // Hide the video in light theme
  themeIcon.setAttribute("src", "static/image/light.png"); // Set light theme icon
}

// Toggle theme when button is clicked
themeToggle.addEventListener("click", () => {
  const currentTheme = themeLink.getAttribute("href");

  // Toggle between light and dark themes
  if (currentTheme === "static/css/style.css") {
    themeLink.setAttribute("href", "static/css/style-light.css");
    localStorage.setItem("theme", "dark"); // Save user's preference
    videoBackground.style.display = "block"; // Show video in dark theme
    themeIcon.setAttribute("src", "static/image/dark.png"); // Set dark theme icon
  } else {
    themeLink.setAttribute("href", "static/css/style.css");
    localStorage.setItem("theme", "light"); // Save user's preference
    videoBackground.style.display = "none"; // Hide video in light theme
    themeIcon.setAttribute("src", "static/image/light.png"); // Set light theme icon
  }
});
