/* ==========================================================
   admin.js — populates the Add Marks dropdowns from the
   backend and submits new marks / new exams.
   No demo-mode fallback here on purpose: this page only makes
   sense once the real backend + MySQL are running.
   ========================================================== */

let allTopics = [];
let allExams = [];

function fillSelect(select, items, valueKey, labelFn, placeholder) {
  select.innerHTML = `<option value="">${placeholder}</option>` +
    items.map((item) => `<option value="${item[valueKey]}">${labelFn(item)}</option>`).join("");
}

async function loadDropdowns() {
  const [students, subjects, topics, exams] = await Promise.all([
    apiGet("/students"),
    apiGet("/subjects"),
    apiGet("/topics"),
    apiGet("/exams"),
  ]);

  allTopics = topics;
  allExams = exams;

  fillSelect(document.getElementById("f-student"), students, "student_id",
    (s) => `${s.full_name} (${s.class_grade})`, "Select a student");

  fillSelect(document.getElementById("f-subject"), subjects, "subject_id",
    (s) => s.subject_name, "Select a subject");

  fillSelect(document.getElementById("e-subject"), subjects, "subject_id",
    (s) => s.subject_name, "Select a subject");

  updateTopicOptions();
  updateExamOptions();
}

function updateTopicOptions() {
  const subjectId = document.getElementById("f-subject").value;
  const filtered = subjectId ? allTopics.filter((t) => String(t.subject_id) === subjectId) : allTopics;
  fillSelect(document.getElementById("f-topic"), filtered, "topic_id", (t) => t.topic_name, "Select a topic");
}

function updateExamOptions() {
  const subjectId = document.getElementById("f-subject").value;
  const filtered = subjectId ? allExams.filter((e) => String(e.subject_id) === subjectId) : allExams;
  fillSelect(
    document.getElementById("f-exam"), filtered, "exam_id",
    (e) => `${e.exam_name} — ${e.exam_date}`, "Select an exam"
  );
}

document.getElementById("f-subject").addEventListener("change", () => {
  updateTopicOptions();
  updateExamOptions();
});

document.getElementById("mark-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const successBox = document.getElementById("mark-success");
  const errorBox = document.getElementById("mark-error");
  successBox.style.display = "none";
  errorBox.style.display = "none";

  const payload = {
    student_id: Number(document.getElementById("f-student").value),
    topic_id: Number(document.getElementById("f-topic").value),
    exam_id: Number(document.getElementById("f-exam").value),
    marks_obtained: Number(document.getElementById("f-obtained").value),
    max_marks: Number(document.getElementById("f-max").value),
  };

  try {
    await apiPost("/marks", payload);
    successBox.textContent = "Mark saved. You can add another below.";
    successBox.style.display = "block";
    document.getElementById("f-obtained").value = "";
  } catch (err) {
    errorBox.textContent = err.message || "Could not save this mark.";
    errorBox.style.display = "block";
  }
});

document.getElementById("exam-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const successBox = document.getElementById("exam-success");
  const errorBox = document.getElementById("exam-error");
  successBox.style.display = "none";
  errorBox.style.display = "none";

  const payload = {
    exam_name: document.getElementById("e-name").value.trim(),
    subject_id: Number(document.getElementById("e-subject").value),
    exam_date: document.getElementById("e-date").value,
  };

  try {
    await apiPost("/exams", payload);
    successBox.textContent = "Exam created — refreshing exam list.";
    successBox.style.display = "block";
    document.getElementById("e-name").value = "";
    await loadDropdowns();
  } catch (err) {
    errorBox.textContent = err.message || "Could not create this exam.";
    errorBox.style.display = "block";
  }
});

loadDropdowns().catch(() => {
  document.getElementById("mark-error").textContent =
    "Couldn't load the form data. Make sure the backend server is running.";
  document.getElementById("mark-error").style.display = "block";
});