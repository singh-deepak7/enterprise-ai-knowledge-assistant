const menuButton = document.getElementById("menuButton");
const navLinks = document.getElementById("navLinks");

menuButton?.addEventListener("click", () => {
  const isOpen = navLinks.classList.toggle("open");
  menuButton.setAttribute("aria-expanded", String(isOpen));
});

navLinks?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    navLinks.classList.remove("open");
    menuButton?.setAttribute("aria-expanded", "false");
  });
});

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12 }
);

document.querySelectorAll(".reveal").forEach((element) => {
  revealObserver.observe(element);
});

const modal = document.getElementById("imageModal");
const modalImage = document.getElementById("modalImage");
const modalTitle = document.getElementById("modalTitle");
const modalClose = document.getElementById("modalClose");

document.querySelectorAll(".zoom-button").forEach((button) => {
  button.addEventListener("click", () => {
    modalImage.src = button.dataset.image;
    modalImage.alt = button.dataset.title || "Architecture diagram";
    modalTitle.textContent = button.dataset.title || "Architecture diagram";
    modal.showModal();
    document.body.classList.add("modal-open");
  });
});

function closeModal() {
  if (modal?.open) modal.close();
  document.body.classList.remove("modal-open");
}

modalClose?.addEventListener("click", closeModal);

modal?.addEventListener("click", (event) => {
  const rect = modal.getBoundingClientRect();
  const outside =
    event.clientX < rect.left ||
    event.clientX > rect.right ||
    event.clientY < rect.top ||
    event.clientY > rect.bottom;

  if (outside) closeModal();
});

modal?.addEventListener("close", () => {
  document.body.classList.remove("modal-open");
});
