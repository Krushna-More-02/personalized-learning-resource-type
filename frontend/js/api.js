/* ==========================================================
   api.js — thin wrapper around the Flask backend.
   If the backend isn't running (e.g. you're previewing the
   frontend alone), each call falls back to realistic demo
   data so the UI is never empty during development.
   ========================================================== */

const API_BASE = "/api";

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`, { credentials: "include" });
  if (!res.ok) throw new Error("Request failed");
  return res.json();
}

/* ---------- DEMO DATA (mirrors database/schema.sql seed) ---------- */

const DEMO_STUDENT = { student_id: 1, full_name: "Aarav Sharma", class_grade: "10th" };

const DEMO_WEAKNESSES = {
  topics: [
    { topic_id: 1, topic_name: "Quadratic Equations", subject_name: "Mathematics", average_percentage: 44, attempts: 2, trend: -8, classification: "critical" },
    { topic_id: 5, topic_name: "Optics", subject_name: "Physics", average_percentage: 36, attempts: 1, trend: null, classification: "weak" },
    { topic_id: 7, topic_name: "Essay Writing", subject_name: "English", average_percentage: 52, attempts: 1, trend: null, classification: "moderate" },
    { topic_id: 3, topic_name: "Probability", subject_name: "Mathematics", average_percentage: 60, attempts: 1, trend: null, classification: "moderate" },
    { topic_id: 6, topic_name: "Grammar Fundamentals", subject_name: "English", average_percentage: 72, attempts: 1, trend: null, classification: "good" },
    { topic_id: 2, topic_name: "Trigonometry", subject_name: "Mathematics", average_percentage: 80, attempts: 1, trend: null, classification: "good" },
    { topic_id: 4, topic_name: "Newtons Laws of Motion", subject_name: "Physics", average_percentage: 88, attempts: 1, trend: null, classification: "strong" },
  ],
};

const DEMO_RECOMMENDATIONS = {
  recommendations: [
    {
      topic_id: 1, topic_name: "Quadratic Equations", subject_name: "Mathematics",
      classification: "critical", average_percentage: 44,
      resources: [
        { resource_id: 1, title: "Quadratic Equations — Visual Introduction", resource_type: "video", url: "https://example.com/quad-intro", difficulty: "beginner", est_minutes: 12 },
        { resource_id: 2, title: "Solving Quadratics by Factoring — Practice Set", resource_type: "practice_set", url: "https://example.com/quad-practice", difficulty: "beginner", est_minutes: 25 },
      ],
    },
    {
      topic_id: 5, topic_name: "Optics", subject_name: "Physics",
      classification: "weak", average_percentage: 36,
      resources: [
        { resource_id: 6, title: "Optics 101 — Reflection & Refraction", resource_type: "video", url: "https://example.com/optics-101", difficulty: "beginner", est_minutes: 14 },
        { resource_id: 7, title: "Ray Diagrams Walkthrough", resource_type: "article", url: "https://example.com/ray-diagrams", difficulty: "beginner", est_minutes: 10 },
      ],
    },
    {
      topic_id: 7, topic_name: "Essay Writing", subject_name: "English",
      classification: "moderate", average_percentage: 52,
      resources: [
        { resource_id: 9, title: "Essay Writing Practice Prompts", resource_type: "practice_set", url: "https://example.com/essay-prompts", difficulty: "intermediate", est_minutes: 20 },
        { resource_id: 8, title: "Essay Writing Structure Guide", resource_type: "article", url: "https://example.com/essay-structure", difficulty: "beginner", est_minutes: 12 },
      ],
    },
    {
      topic_id: 3, topic_name: "Probability", subject_name: "Mathematics",
      classification: "moderate", average_percentage: 60,
      resources: [
        { resource_id: 5, title: "Probability Practice Problems", resource_type: "practice_set", url: "https://example.com/prob-practice", difficulty: "intermediate", est_minutes: 20 },
      ],
    },
  ],
};

/* ---------- public functions used by the pages ---------- */

async function loginRequest(email, password) {
  try {
    return await apiPost("/auth/login", { email, password });
  } catch (e) {
    if (email === "demo@student.com" && password === "password123") {
      sessionStorage.setItem("plr_demo_mode", "1");
      return { student: DEMO_STUDENT };
    }
    throw e;
  }
}

async function registerRequest(payload) {
  return apiPost("/auth/register", payload);
}

function isDemoMode() {
  return sessionStorage.getItem("plr_demo_mode") === "1";
}

async function fetchWeaknesses(studentId) {
  if (isDemoMode()) return DEMO_WEAKNESSES;
  try {
    return await apiGet(`/students/${studentId}/weaknesses`);
  } catch {
    return DEMO_WEAKNESSES;
  }
}

async function fetchRecommendations(studentId) {
  if (isDemoMode()) return DEMO_RECOMMENDATIONS;
  try {
    return await apiGet(`/students/${studentId}/recommendations`);
  } catch {
    return DEMO_RECOMMENDATIONS;
  }
}

function getCurrentStudent() {
  const raw = sessionStorage.getItem("plr_student");
  return raw ? JSON.parse(raw) : DEMO_STUDENT;
}

function setCurrentStudent(student) {
  sessionStorage.setItem("plr_student", JSON.stringify(student));
}