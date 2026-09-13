const RESOURCE_ICON = {
  video: "▶", article: "📄", pdf: "📕", practice_set: "✎", course: "🎓",
};

function renderRecommendations(recs) {
  const container = document.getElementById("rec-list");
  container.innerHTML = "";

  if (!recs.length) {
    container.innerHTML = `
      <div class="empty-state">
        <strong>You're on top of everything</strong>
        No weak areas detected right now — keep it up.
      </div>`;
    return;
  }

  recs.forEach((topic) => {
    const block = document.createElement("div");
    block.className = "rec-topic";
    block.innerHTML = `
      <div class="rec-topic-head">
        <div>
          <h3>${topic.topic_name} <span class="tag tag-${topic.classification}">${topic.classification}</span></h3>
          <div class="rec-topic-meta">${topic.subject_name} · currently averaging ${topic.average_percentage}%</div>
        </div>
      </div>
      <div class="resource-list"></div>
    `;
    const list = block.querySelector(".resource-list");

    topic.resources.forEach((r) => {
      const row = document.createElement("div");
      row.className = "resource-row";
      row.innerHTML = `
        <div class="rtype">${RESOURCE_ICON[r.resource_type] || "•"}</div>
        <div class="rinfo">
          <div class="rtitle">${r.title}</div>
          <div class="rmeta">${r.resource_type.replace("_", " ")} · ${r.difficulty} · ~${r.est_minutes} min</div>
        </div>
        <a class="btn-go" href="${r.url}" target="_blank" rel="noopener">Start</a>
      `;
      list.appendChild(row);
    });

    container.appendChild(block);
  });
}

(async function init() {
  const student = getCurrentStudent();
  document.getElementById("greeting").textContent = "Recommended for you";
  document.getElementById("meta").textContent = `Resources chosen for ${student.full_name.split(" ")[0]}'s weakest topics first`;

  const data = await fetchRecommendations(student.student_id);
  renderRecommendations(data.recommendations || []);
})();