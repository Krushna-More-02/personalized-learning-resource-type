const CLASS_BY_LEVEL = {
  critical: "crit", weak: "weak", moderate: "mod", good: "good", strong: "strong",
};

function renderLedger(topics) {
  const bySubject = {};
  topics.forEach((t) => {
    bySubject[t.subject_name] = bySubject[t.subject_name] || [];
    bySubject[t.subject_name].push(t);
  });

  const container = document.getElementById("ledger");
  container.innerHTML = "";

  Object.entries(bySubject).forEach(([subject, rows]) => {
    const group = document.createElement("div");
    group.className = "subject-group";

    const heading = document.createElement("h3");
    heading.textContent = subject;
    group.appendChild(heading);

    rows.forEach((row) => {
      const div = document.createElement("div");
      div.className = "ledger-row";
      div.innerHTML = `
        <div class="flag flag-${row.classification}"></div>
        <div class="topic-name">${row.topic_name}</div>
        <div class="meter"><div class="meter-fill ${CLASS_BY_LEVEL[row.classification]}" style="width:${row.average_percentage}%"></div></div>
        <div class="pct">${row.average_percentage}%</div>
        <div class="tag tag-${row.classification}">${row.classification}</div>
      `;
      group.appendChild(div);
    });

    container.appendChild(group);
  });
}

function renderStats(topics) {
  const overall = Math.round(topics.reduce((s, t) => s + t.average_percentage, 0) / topics.length);
  const weakCount = topics.filter((t) => ["critical", "weak", "moderate"].includes(t.classification)).length;
  const strongCount = topics.filter((t) => t.classification === "strong").length;

  document.getElementById("stat-overall").textContent = `${overall}%`;
  document.getElementById("stat-weak").textContent = weakCount;
  document.getElementById("stat-strong").textContent = strongCount;
}

(async function init() {
  const student = getCurrentStudent();
  document.getElementById("greeting").textContent = `Good to see you, ${student.full_name.split(" ")[0]}`;
  document.getElementById("meta").textContent = `Class ${student.class_grade} · Performance ledger across all subjects`;

  const data = await fetchWeaknesses(student.student_id);
  const topics = data.topics || [];

  if (!topics.length) {
    document.getElementById("ledger").innerHTML = `
      <div class="empty-state">
        <strong>No marks recorded yet</strong>
        Once a test is added, your weak areas will show up here automatically.
      </div>`;
    return;
  }

  renderStats(topics);
  renderLedger(topics);
})();