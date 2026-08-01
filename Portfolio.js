const themeToggle = document.getElementById("themeToggle");
const body = document.body;
themeToggle.addEventListener("click", () => {
  const current = body.getAttribute("data-theme");
  const next = current === "light" ? "dark" : "light";
  body.setAttribute("data-theme", next);
  themeToggle.textContent = next === "light" ? "🌙" : "☀️";
});

const navToggleBtn = document.getElementById("navToggleBtn");
const navLinks = document.getElementById("navLinks");
navToggleBtn.addEventListener("click", () => {
  const isOpen = navLinks.classList.toggle("open");
  navToggleBtn.textContent = isOpen ? "✕" : "☰";
});
navLinks.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    navLinks.classList.remove("open");
    navToggleBtn.textContent = "☰";
  });
});

const revealEls = document.querySelectorAll(".reveal");
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.15 },
);
revealEls.forEach((el) => observer.observe(el));

document.getElementById("year").textContent = new Date().getFullYear();

// Premium PDF Viewer Logic
let pdfjsLib = window["pdfjs-dist/build/pdf"];
if (pdfjsLib) {
  pdfjsLib.GlobalWorkerOptions.workerSrc =
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js";
}

let pdfDoc = null;
let pageNum = 1;
let pageRendering = false;
let pageNumPending = null;
let scale = 1.5;

const modal = document.getElementById("pdfModal");
const spinner = document.getElementById("pdfSpinner");
const canvasWrapper = document.getElementById("pdfCanvasWrapper");
const titleEl = document.getElementById("pdfModalTitle");
const pageNumEl = document.getElementById("pdfPageNum");
const pageCountEl = document.getElementById("pdfPageCount");
const zoomScaleEl = document.getElementById("pdfZoomScale");

// Prevent right-click and keyboard copying/printing (Read-only restriction)
function preventSavePrint(e) {
  if (e.ctrlKey || e.metaKey) {
    if (e.key === "s" || e.key === "p" || e.key === "c" || e.key === "a") {
      e.preventDefault();
      alert(
        "Saving, printing, and copying are disabled for this read-only certification document.",
      );
    }
  }
}

function showPdf(fileUrl) {
  // Determine friendly title from filename
  let friendlyName = fileUrl
    .split("/")
    .pop()
    .replace(/\.pdf$/i, "");
  titleEl.textContent = friendlyName;

  // Reset state
  pageNum = 1;
  scale = 1.5;
  pdfDoc = null;
  pageRendering = false;
  pageNumPending = null;

  // Show toolbar
  document.querySelector(".pdf-modal-toolbar").style.display = "flex";

  // Open modal
  modal.classList.add("open");
  modal.setAttribute("aria-hidden", "false");
  spinner.style.display = "flex";
  canvasWrapper.style.display = "none";
  canvasWrapper.innerHTML = '<canvas id="pdfCanvas"></canvas>';

  // Add keyboard restrictions
  window.addEventListener("keydown", preventSavePrint);

  // Try loading with PDF.js
  if (typeof pdfjsLib !== "undefined") {
    pdfjsLib
      .getDocument(fileUrl)
      .promise.then((pdf) => {
        pdfDoc = pdf;
        pageCountEl.textContent = pdf.numPages;

        const pageControls = document.querySelector(".pdf-toolbar-pages");
        if (pdf.numPages <= 1) {
          pageControls.style.opacity = "0.5";
          document.getElementById("pdfPrevPage").disabled = true;
          document.getElementById("pdfNextPage").disabled = true;
        } else {
          pageControls.style.opacity = "1";
          document.getElementById("pdfPrevPage").disabled = false;
          document.getElementById("pdfNextPage").disabled = false;
        }

        renderPage(1);
      })
      .catch((err) => {
        console.warn("PDF.js load error, falling back to iframe:", err);
        loadFallbackIframe(fileUrl);
      });
  } else {
    console.warn("PDF.js library not loaded, falling back to iframe");
    loadFallbackIframe(fileUrl);
  }
}

function renderPage(num) {
  pageRendering = true;
  const canvas = document.getElementById("pdfCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  pdfDoc
    .getPage(num)
    .then((page) => {
      const viewport = page.getViewport({ scale: scale });
      canvas.height = viewport.height;
      canvas.width = viewport.width;

      const renderContext = {
        canvasContext: ctx,
        viewport: viewport,
      };

      const renderTask = page.render(renderContext);
      renderTask.promise.then(() => {
        pageRendering = false;
        spinner.style.display = "none";
        canvasWrapper.style.display = "block";
        pageNumEl.textContent = num;

        document.getElementById("pdfPrevPage").disabled = num <= 1;
        document.getElementById("pdfNextPage").disabled =
          num >= pdfDoc.numPages;
        zoomScaleEl.textContent = `${Math.round(scale * 100)}%`;

        if (pageNumPending !== null) {
          renderPage(pageNumPending);
          pageNumPending = null;
        }
      });
    })
    .catch((err) => {
      console.error("Error rendering PDF page:", err);
      pageRendering = false;
      spinner.style.display = "none";
    });
}

function queueRenderPage(num) {
  if (pageRendering) {
    pageNumPending = num;
  } else {
    renderPage(num);
  }
}

function changeZoom(amount) {
  if (!pdfDoc || pageRendering) return;
  const newScale = scale + amount;
  if (newScale >= 0.5 && newScale <= 3.0) {
    scale = newScale;
    renderPage(pageNum);
  }
}

function loadFallbackIframe(fileUrl) {
  canvasWrapper.innerHTML = `
      <iframe src="${fileUrl}#toolbar=0&navpanes=0" 
              style="width: 100%; height: 70vh; border: none;"
              id="pdfIframe">
      </iframe>
    `;
  canvasWrapper.style.display = "block";
  document.querySelector(".pdf-modal-toolbar").style.display = "none";

  setTimeout(() => {
    spinner.style.display = "none";
  }, 600);
}

function closePdfModal() {
  modal.classList.remove("open");
  modal.setAttribute("aria-hidden", "true");

  const iframe = document.getElementById("pdfIframe");
  if (iframe) iframe.src = "about:blank";

  canvasWrapper.innerHTML = '<canvas id="pdfCanvas"></canvas>';
  window.removeEventListener("keydown", preventSavePrint);
  pdfDoc = null;
}

// Event Listeners
document.querySelectorAll(".cert-view-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const file = btn.getAttribute("data-file");
    if (file) showPdf(file);
  });
});

document
  .getElementById("closePdfModal")
  .addEventListener("click", closePdfModal);
document
  .querySelector(".pdf-modal-overlay")
  .addEventListener("click", closePdfModal);

document.getElementById("pdfPrevPage").addEventListener("click", () => {
  if (pageNum <= 1 || pageRendering) return;
  pageNum--;
  queueRenderPage(pageNum);
});
document.getElementById("pdfNextPage").addEventListener("click", () => {
  if (!pdfDoc || pageNum >= pdfDoc.numPages || pageRendering) return;
  pageNum++;
  queueRenderPage(pageNum);
});
document
  .getElementById("pdfZoomIn")
  .addEventListener("click", () => changeZoom(0.25));
document
  .getElementById("pdfZoomOut")
  .addEventListener("click", () => changeZoom(-0.25));

document
  .getElementById("pdfModalBody")
  .addEventListener("contextmenu", (e) => e.preventDefault());
