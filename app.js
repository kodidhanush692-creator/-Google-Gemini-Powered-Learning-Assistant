let currentAction = "qna";

const tabs = document.querySelectorAll(".tab-btn");
const promptInput = document.getElementById("promptInput");
const activeEngineText = document.getElementById("activeEngineText");
const interactionForm = document.getElementById("interactionForm");
const generateBtn = document.getElementById("generateBtn");
const outputCanvas = document.getElementById("outputCanvas");

const uploadForm = document.getElementById("uploadForm");
const pdfFileInput = document.getElementById("pdfFileInput");
const uploadStatus = document.getElementById("uploadStatus");

// Tab Navigation
tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    currentAction = tab.getAttribute("data-action");
    promptInput.placeholder = tab.getAttribute("data-placeholder");

    if (currentAction === "explain") {
      activeEngineText.textContent = "Engine: LaMini-Flan-T5-783M (Local CPU)";
    } else if (currentAction === "doc_qa") {
      activeEngineText.textContent = "Engine: Gemini 1.5 Pro + FAISS Vector RAG";
    } else {
      activeEngineText.textContent = "Engine: Gemini 1.5 Pro (Cloud API)";
    }
  });
});

// Handle PDF Upload
uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!pdfFileInput.files || pdfFileInput.files.length === 0) return;

  const file = pdfFileInput.files[0];
  const formData = new FormData();
  formData.append("file", file);

  uploadStatus.innerHTML = `<span style="color:#1a73e8;">Uploading & indexing in FAISS...</span>`;

  try {
    const res = await fetch("/api/upload_pdf", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    if (res.ok) {
      uploadStatus.innerHTML = `<span style="color:#188038; font-weight:600;">✅ ${data.message}</span>`;
      // Switch to Document Q&A tab
      const docTab = document.querySelector('[data-action="doc_qa"]');
      if (docTab) docTab.click();
    } else {
      uploadStatus.innerHTML = `<span style="color:#d93025;">❌ ${data.error || "Upload failed."}</span>`;
    }
  } catch (err) {
    uploadStatus.innerHTML = `<span style="color:#d93025;">❌ ${err.message}</span>`;
  }
});

// Handle Form Submission
interactionForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = promptInput.value.trim();
  if (!text) return;

  generateBtn.disabled = true;
  outputCanvas.innerHTML = `<div class="loading-indicator">✨ EduGenie is synthesizing with AI...</div>`;

  try {
    if (currentAction === "doc_qa") {
      // Document Q&A via FAISS RAG
      const formData = new FormData();
      formData.append("question", text);
      formData.append("top_k", 3);

      const res = await fetch("/api/ask_doc", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (res.ok) {
        let citationsHtml = "";
        if (data.sources && data.sources.length > 0) {
          citationsHtml = `<div style="margin-top: 1.5rem;"><h4 style="color:#5f6368; font-size:0.9rem;">📚 Referenced Document Sources:</h4>`;
          data.sources.forEach((src) => {
            citationsHtml += `
              <div class="citation-card">
                <strong>Page ${src.page}</strong> (Relevance: ${src.score})
                <p style="color:#5f6368; margin-top:0.25rem;">"${src.chunk}"</p>
              </div>
            `;
          });
          citationsHtml += `</div>`;
        }
        outputCanvas.innerHTML = marked.parse(data.answer) + citationsHtml;
      } else {
        outputCanvas.innerHTML = `<div style="color:#d93025;"><strong>Error:</strong> ${data.error || "Failed to query document."}</div>`;
      }

    } else {
      // General Actions (Explain, Q&A, Quiz, Summary, Learning Path)
      const res = await fetch("/api/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: currentAction, input_text: text }),
      });
      const result = await res.json();

      if (res.ok) {
        if (result.type === "quiz" && result.data && result.data.questions) {
          renderQuiz(result.data);
        } else {
          outputCanvas.innerHTML = marked.parse(result.data);
        }
      } else {
        outputCanvas.innerHTML = `<div style="color:#d93025;"><strong>Error:</strong> ${result.error || "Processing failed."}</div>`;
      }
    }
  } catch (err) {
    outputCanvas.innerHTML = `<div style="color:#d93025;"><strong>Network Error:</strong> ${err.message}</div>`;
  } finally {
    generateBtn.disabled = false;
  }
});

function renderQuiz(quiz) {
  let html = `<h3>🎯 Quiz: ${quiz.topic || "Practice Test"}</h3>`;
  quiz.questions.forEach((q, qIndex) => {
    html += `
      <div class="quiz-box" id="quiz-${qIndex}">
        <p><strong>Q${qIndex + 1}. ${q.question}</strong></p>
        ${q.options.map((opt) => `
          <button type="button" class="quiz-opt" onclick="evalQuizAnswer(${qIndex}, '${opt.id}', '${q.correct_option_id}', '${encodeURIComponent(q.explanation)}')">
            <strong>${opt.id})</strong> ${opt.text}
          </button>
        `).join("")}
        <div id="quiz-fb-${qIndex}" class="quiz-feedback" style="display:none;"></div>
      </div>
    `;
  });
  outputCanvas.innerHTML = html;
}

window.evalQuizAnswer = function (qIndex, selectedId, correctId, encExp) {
  const fb = document.getElementById(`quiz-fb-${qIndex}`);
  const explanation = decodeURIComponent(encExp);
  fb.style.display = "block";
  if (selectedId === correctId) {
    fb.innerHTML = `<span style="color:#188038;">✅ Correct!</span> ${explanation}`;
  } else {
    fb.innerHTML = `<span style="color:#d93025;">❌ Incorrect. Correct answer is ${correctId}.</span> ${explanation}`;
  }
};
