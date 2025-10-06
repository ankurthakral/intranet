window.onload = function () {
  // Start the confetti animation when the page loads
  startConfetti();

  // Show the text after the confetti starts popping (2 seconds delay)
  setTimeout(() => {
    const text = document.getElementById("confettiText");
    if (text) text.style.opacity = "1";
  }, 500);

  // Stop the confetti animation and hide the text after 5 seconds
  setTimeout(() => {
    stopConfetti();

    // Fade out both the canvas and the text
    const canvas = document.getElementById("confettiCanvas");
    const text = document.getElementById("confettiText");
    if (canvas) canvas.style.opacity = "0";
    if (text) text.style.opacity = "0";
  }, 3000);
};

const confettiCanvas = document.getElementById("confettiCanvas");
const ctx = confettiCanvas.getContext("2d");

// Resize the canvas to match the viewport size
function resizeCanvas() {
  confettiCanvas.width = window.innerWidth;
  confettiCanvas.height = window.innerHeight;
}

resizeCanvas();
window.addEventListener("resize", resizeCanvas);

const confettiParticles = [];
const colors = [
  "#FF5733",
  "#FFC300",
  "#DAF7A6",
  "#581845",
  "#C70039",
  "#900C3F",
  "#6C3483",
  "#3498DB",
];

class Confetti {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.color = colors[Math.floor(Math.random() * colors.length)];
    this.size = Math.random() * 10 + 5;
    this.speedY = Math.random() * 3 + 2;
    this.speedX = Math.random() * 2 - 1;
    this.gravity = 0.05;
  }

  update() {
    this.y += this.speedY + this.gravity;
    this.x += this.speedX;
    this.gravity += 0.01;
  }

  draw() {
    ctx.fillStyle = this.color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fill();
  }
}

function createConfetti() {
  for (let i = 0; i < 200; i++) {
    const x = Math.random() * confettiCanvas.width;
    const y = (Math.random() * confettiCanvas.height) / 2;
    confettiParticles.push(new Confetti(x, y));
  }
}

function animateConfetti() {
  ctx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
  confettiParticles.forEach((particle, index) => {
    particle.update();
    particle.draw();
    if (particle.y > confettiCanvas.height) {
      confettiParticles.splice(index, 1);
    }
  });
  if (confettiParticles.length > 0) {
    requestAnimationFrame(animateConfetti);
  }
}

window.addEventListener("load", () => {
  setTimeout(() => {
    createConfetti();
    animateConfetti();
  }, 1000); // Wait for popper animation to finish
});
