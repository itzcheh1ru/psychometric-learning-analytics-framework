/**
 * GenAI-Assisted Cognitive Engagement, Recall, and Learning Retention Evaluation
 * Frontend Application Controller & Fixed-Sequence Manager
 */

// Immediate route & registration guard check to prevent flash of protected content
let sequenceGuardExecuted = false;
enforceExperimentalSequenceGuard();

document.addEventListener("DOMContentLoaded", () => {
  enforceExperimentalSequenceGuard();
  initDashboardParticipant();
  checkCurrentPageNav();
  setupRegistrationIdGenerator();
  renderGlobalProgressIndicator();
});

const phaseCompletionKeys = new Set([
  "brain_only_completed",
  "phase1_completed",
  "genai_assisted_completed",
  "phase2_completed",
  "delayed_recall_completed",
  "phase3_completed"
]);

window.addEventListener("storage", event => {
  const currentPath = window.location.pathname.split("/").pop() || "index.html";
  if (currentPath === "dashboard.html" && phaseCompletionKeys.has(event.key)) {
    window.location.reload();
  }
});

window.addEventListener("pageshow", event => {
  const currentPath = window.location.pathname.split("/").pop() || "index.html";
  if (event.persisted && currentPath === "dashboard.html") {
    initDashboardParticipant();
    renderGlobalProgressIndicator();
  }
});

/**
 * Automatically sets the active class on the current navigation item
 */
function checkCurrentPageNav() {
  const currentPath = window.location.pathname.split("/").pop() || "index.html";
  const navLinks = document.querySelectorAll(".site-nav .nav-link");
  
  navLinks.forEach(link => {
    const linkHref = link.getAttribute("href");
    if (linkHref === currentPath) {
      navLinks.forEach(l => l.classList.remove("active"));
      link.classList.add("active");
    }
  });
}

const UNIVERSITY_ID_PREFIXES = {
  "University of Colombo": "UOC",
  "University of Peradeniya": "UOP",
  "University of Sri Jayewardenepura": "USJ",
  "University of Kelaniya": "UOK",
  "University of Moratuwa": "UOM",
  "University of Jaffna": "UOJ",
  "University of Ruhuna": "UOR",
  "Eastern University, Sri Lanka": "EUSL",
  "South Eastern University of Sri Lanka": "SEUSL",
  "Rajarata University of Sri Lanka": "RUSL",
  "Sabaragamuwa University of Sri Lanka": "SUSL",
  "Wayamba University of Sri Lanka": "WAY",
  "Uva Wellassa University of Sri Lanka": "UWU",
  "The Open University of Sri Lanka": "OUSL",
  "University of the Visual and Performing Arts": "UVPA",
  "Gampaha Wickramarachchi University of Indigenous Medicine": "GWUIM",
  "University of Vavuniya": "UOV",
  "SLIIT": "SLIIT",
  "NSBM Green University": "NSBM",
  "CINEC Campus": "CINEC",
  "IIT": "IIT"
};

function generateParticipantId(universityName) {
  const universityCode = UNIVERSITY_ID_PREFIXES[universityName] || "UNI";
  const randomValues = new Uint32Array(1);
  window.crypto.getRandomValues(randomValues);
  const numericSuffix = String(randomValues[0] % 100000000).padStart(8, "0");
  return `${universityCode}-${numericSuffix}`;
}

/**
 * Legacy no-op kept for compatibility with the registration page lifecycle.
 */
function setupRegistrationIdGenerator() {
  return;
}

function isExperimentPhaseComplete(...keys) {
  return keys.some(key => sessionStorage.getItem(key) === "true" || localStorage.getItem(key) === "true");
}

function markExperimentPhaseComplete(...keys) {
  keys.forEach(key => {
    sessionStorage.setItem(key, "true");
    localStorage.setItem(key, "true");
  });
}

async function syncPendingPhase3Result(participantId) {
  if (!participantId) return;
  const storageKey = `phase3_pending_result_${participantId}`;
  const pendingPayload = localStorage.getItem(storageKey);
  if (!pendingPayload) return;

  try {
    const response = await fetch("/api/delayed-recall-result", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: pendingPayload
    });
    if (!response.ok) throw new Error("Phase 3 sync was rejected by the server.");

    localStorage.removeItem(storageKey);
    const statusEl = document.getElementById("displayProtocolStatus");
    if (statusEl?.textContent.includes("Sync Pending")) {
      statusEl.textContent = "Protocol Completed";
    }
  } catch (error) {
    console.warn("Phase 3 results remain saved locally and will retry on the next dashboard visit:", error);
  }
}

/**
 * Handles Participant Registration Form Submission
 * Validates registration fields and assigns the fixed experimental sequence
 */
async function handleRegistration(event) {
  event.preventDefault();

  const motherCode = "";
  const birthYear = "";
  const birthMonth = "";
  const schoolCode = "";

  const universityName = document.getElementById("universityName")?.value;
  const genaiExperience = document.querySelector('input[name="genaiExperienceDuration"]:checked')?.value;
  const consentGiven = document.getElementById("consentCheckbox")?.checked;

  if (!universityName) {
    alert("Please select your university or institution.");
    document.getElementById("universityName")?.focus();
    return false;
  }

  const participantId = generateParticipantId(universityName);

  if (!genaiExperience) {
    alert("Please select how long you have used Generative AI tools.");
    return false;
  }

  if (!consentGiven) {
    alert("Please confirm the informed research consent checkbox to participate.");
    return false;
  }

  const experimentGroup = "A";
  const assignedSequence = "brain_only_first";

  // Clear previous session & local metrics to avoid data contamination between trials
  sessionStorage.removeItem("registration_completed");
  sessionStorage.removeItem("participant_id");
  sessionStorage.removeItem("currentParticipant");
  sessionStorage.removeItem("brain_only_completed");
  sessionStorage.removeItem("genai_assisted_completed");
  sessionStorage.removeItem("delayed_recall_completed");
  sessionStorage.removeItem("phase1_completed");
  sessionStorage.removeItem("phase2_completed");
  sessionStorage.removeItem("phase3_completed");
  sessionStorage.removeItem("phase1_score");
  sessionStorage.removeItem("phase2_score");
  sessionStorage.removeItem("phase1_duration");
  sessionStorage.removeItem("phase2_duration");
  sessionStorage.removeItem("brain_retention");
  sessionStorage.removeItem("genai_retention");
  sessionStorage.removeItem("retention_diff");

  localStorage.removeItem("registration_completed");
  localStorage.removeItem("participant_id");
  localStorage.removeItem("experiment_group");
  localStorage.removeItem("assigned_sequence");
  [
    "brain_only_completed",
    "genai_assisted_completed",
    "delayed_recall_completed",
    "phase1_completed",
    "phase2_completed",
    "phase3_completed"
  ].forEach(key => localStorage.removeItem(key));

  const participantData = {
    participantId,
    motherCode,
    birthYear,
    birthMonth,
    schoolCode,
    universityName,
    genaiExperience,
    consentGiven: 1,
    experimentGroup,
    assignedSequence,
    registeredAt: new Date().toISOString()
  };

  // Ingest into backend database
  try {
    const response = await fetch("/api/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        participant_id: participantId,
        mother_code: motherCode,
        birth_year: birthYear,
        birth_month: birthMonth,
        school_code: schoolCode,
        university_name: universityName,
        genai_experience: genaiExperience,
        consent_given: 1,
        experiment_group: experimentGroup,
        assigned_sequence: assignedSequence
      })
    });
    if (response.ok) {
      const respData = await response.json().catch(() => ({}));
      const finalPid = respData.participant_id || participantId;
      const finalGroup = respData.experiment_group || experimentGroup;
      const finalSequence = respData.assigned_sequence || assignedSequence;

      participantData.participantId = finalPid;
      participantData.experimentGroup = finalGroup;
      participantData.assignedSequence = finalSequence;

      // Store verified registration completion state in sessionStorage & localStorage
      sessionStorage.setItem("participant_id", finalPid);
      sessionStorage.setItem("experiment_group", finalGroup);
      sessionStorage.setItem("assigned_sequence", finalSequence);
      sessionStorage.setItem("registration_completed", "true");
      sessionStorage.setItem("currentParticipant", JSON.stringify(participantData));

      localStorage.setItem("participant_id", finalPid);
      localStorage.setItem("experiment_group", finalGroup);
      localStorage.setItem("assigned_sequence", finalSequence);
      localStorage.setItem("registration_completed", "true");

      console.log(`Registered ${finalPid} successfully with group ${finalGroup}.`);
      window.location.href = "brain_only.html";
      return false;
    } else {
      const errData = await response.json().catch(() => ({}));
      alert(errData.error || "Please complete all required fields before continuing.");
      return false;
    }
  } catch (err) {
    console.warn("Backend API offline; stored participant details in browser session cache:", err);
    // Offline resilience fallback
    sessionStorage.setItem("participant_id", participantId);
    sessionStorage.setItem("experiment_group", experimentGroup);
    sessionStorage.setItem("assigned_sequence", assignedSequence);
    sessionStorage.setItem("registration_completed", "true");
    sessionStorage.setItem("currentParticipant", JSON.stringify(participantData));

    localStorage.setItem("participant_id", participantId);
    localStorage.setItem("experiment_group", experimentGroup);
    localStorage.setItem("assigned_sequence", assignedSequence);
    localStorage.setItem("registration_completed", "true");

    window.location.href = "brain_only.html";
    return false;
  }
}

/**
 * Standardized Global Experiment Progress Stepper
 * Renders into #globalProgressContainer on all participant pages
 */
function renderGlobalProgressIndicator() {
  const container = document.getElementById("globalProgressContainer");
  if (!container) return;

  const currentPath = window.location.pathname.split("/").pop() || "index.html";
  const storedParticipant = sessionStorage.getItem("currentParticipant");
  let group = sessionStorage.getItem("experiment_group") || "A";
  if (storedParticipant) {
    try {
      group = JSON.parse(storedParticipant).experimentGroup || group;
    } catch (e) {}
  }

  const isRegistered = (sessionStorage.getItem("registration_completed") === "true" || localStorage.getItem("registration_completed") === "true") && Boolean(sessionStorage.getItem("currentParticipant") || sessionStorage.getItem("participant_id") || localStorage.getItem("participant_id"));
  const isBrainDone = isExperimentPhaseComplete("brain_only_completed", "phase1_completed");
  const isGenAiDone = isExperimentPhaseComplete("genai_assisted_completed", "phase2_completed");
  const isRecallDone = isExperimentPhaseComplete("delayed_recall_completed", "phase3_completed");

  const step1Name = "Brain-Only";
  const step2Name = "GenAI-Assisted";
  const isStep1Done = isBrainDone;
  const isStep2Done = isGenAiDone;

  const isRegActive = currentPath === "register.html";
  const isStep1Active = currentPath === "brain_only.html";
  const isStep2Active = currentPath === "genai_assisted.html";
  const isRecallActive = currentPath === "delayed_recall.html";

  container.innerHTML = `
    <div class="global-stepper-wrap">
      <div class="global-stepper-label">
        <span>Current Experiment Progress</span>
        <span>Sequence: Brain-Only \u2192 GenAI-Assisted \u2192 Delayed Recall</span>
      </div>
      <div class="global-stepper-track">
        <div class="stepper-pill ${isRegistered && !isRegActive ? 'completed' : (isRegActive ? 'active' : '')}">
          <span>${isRegistered && !isRegActive ? '&#10003;' : (isRegActive ? '&rarr;' : '1')}</span>
          <span>Registration</span>
        </div>
        <span class="stepper-arrow">&rarr;</span>
        <div class="stepper-pill ${isStep1Done ? 'completed' : (isStep1Active ? 'active' : '')}">
          <span>${isStep1Done ? '&#10003;' : (isStep1Active ? '&rarr;' : '2')}</span>
          <span>Step 1: ${step1Name}</span>
        </div>
        <span class="stepper-arrow">&rarr;</span>
        <div class="stepper-pill ${isStep2Done ? 'completed' : (isStep2Active ? 'active' : '')}">
          <span>${isStep2Done ? '&#10003;' : (isStep2Active ? '&rarr;' : '3')}</span>
          <span>Step 2: ${step2Name}</span>
        </div>
        <span class="stepper-arrow">&rarr;</span>
        <div class="stepper-pill ${isRecallDone ? 'completed' : (isRecallActive ? 'active' : '')}">
          <span>${isRecallDone ? '&#10003;' : (isRecallActive ? '&rarr;' : '4')}</span>
          <span>Step 3: Delayed Recall</span>
        </div>
      </div>
    </div>
  `;
}

/**
 * Initializes Dashboard with fixed sequence order and status tracking
 */
function initDashboardParticipant() {
  const currentPath = window.location.pathname.split("/").pop() || "index.html";
  if (currentPath !== "dashboard.html") return;

  const isRegistered = (sessionStorage.getItem("registration_completed") === "true" || localStorage.getItem("registration_completed") === "true");
  const storedParticipant = sessionStorage.getItem("currentParticipant");
  const pid = sessionStorage.getItem("participant_id") || localStorage.getItem("participant_id");

  if (!isRegistered || (!storedParticipant && !pid)) {
    alert("Please complete participant registration before starting the experiment.");
    window.location.href = "register.html";
    return;
  }

  const displayIdEl = document.getElementById("displayParticipantId");
  if (!displayIdEl) return;

  // Retrieve participant data
  let participantData = null;
  if (storedParticipant) {
    try {
      participantData = JSON.parse(storedParticipant);
    } catch (e) {
      console.error("Error parsing stored participant data:", e);
    }
  }

  const group = sessionStorage.getItem("experiment_group") || (participantData && participantData.experimentGroup) || localStorage.getItem("experiment_group") || "A";
  const sequence = "brain_only_first";
  const participantId = (participantData && participantData.participantId) || pid || "";
  syncPendingPhase3Result(participantId);

  // Check completion states
  const isBrainDone = isExperimentPhaseComplete("brain_only_completed", "phase1_completed");
  const isGenAiDone = isExperimentPhaseComplete("genai_assisted_completed", "phase2_completed");
  const isRecallDone = isExperimentPhaseComplete("delayed_recall_completed", "phase3_completed");

  const brainScore = sessionStorage.getItem("phase1_score") || "8";
  const genaiScore = sessionStorage.getItem("phase2_score") || "9";

  // 1. Update Status Bar
  displayIdEl.textContent = participantId;

  const displayGroupEl = document.getElementById("displayGroup");
  if (displayGroupEl) {
    displayGroupEl.innerHTML = `<span class="group-badge ${group === 'A' ? 'group-a' : 'group-b'}">Group ${group}</span>`;
  }

  const displaySequenceEl = document.getElementById("displaySequence");
  if (displaySequenceEl) {
    displaySequenceEl.innerHTML = `<strong>Fixed:</strong> Brain-Only &rarr; GenAI &rarr; Recall`;
  }

  const displayStatusEl = document.getElementById("displayProtocolStatus");
  if (displayStatusEl) {
    if (isRecallDone) {
      displayStatusEl.textContent = localStorage.getItem(`phase3_pending_result_${participantId}`)
        ? "Protocol Completed (Sync Pending)"
        : "Protocol Completed";
      displayStatusEl.style.color = "var(--secondary-color)";
    } else if (isBrainDone && isGenAiDone) {
      displayStatusEl.textContent = "In Progress (Step 3: Recall Ready)";
      displayStatusEl.style.color = "var(--accent-color)";
    } else if (isBrainDone) {
      displayStatusEl.textContent = "In Progress (Step 2 Ready)";
      displayStatusEl.style.color = "var(--accent-color)";
    } else {
      displayStatusEl.textContent = "In Progress (Step 1 Ready)";
      displayStatusEl.style.color = "var(--primary-color)";
    }
  }

  // 2. Render Sequence Flow Banner
  renderSequenceFlowBanner(isBrainDone, isGenAiDone, isRecallDone);

  // 3. Render Completion Percentage Widget
  renderCompletionPercentageWidget(isBrainDone, isGenAiDone, isRecallDone);

  // 4. Render Phase Cards dynamically according to assigned sequence
  renderPhaseCards(isBrainDone, isGenAiDone, isRecallDone, brainScore, genaiScore);
}

/**
 * Renders the Experiment Completion Percentage Widget on the Dashboard
 * Visualizes: Registration ✓, Brain-Only 33%, GenAI-Assisted 66%, Delayed Recall 100%
 */
function renderCompletionPercentageWidget(isBrainDone, isGenAiDone, isRecallDone) {
  const barFill = document.getElementById("completionBarFill");
  const overallBadge = document.getElementById("completionOverallBadge");
  if (!barFill || !overallBadge) return;

  const isStep1Done = isBrainDone;
  const isStep2Done = isGenAiDone;

  let completionPct = 0;
  if (isRecallDone) {
    completionPct = 100;
  } else if (isStep1Done && isStep2Done) {
    completionPct = 66;
  } else if (isStep1Done) {
    completionPct = 33;
  } else {
    completionPct = 0;
  }

  barFill.style.width = `${completionPct}%`;

  if (completionPct === 100) {
    overallBadge.textContent = "100% Complete \u2022 Research Protocol Finished \u2713";
    overallBadge.classList.add("complete");
  } else if (completionPct === 66) {
    overallBadge.textContent = "66% Complete \u2022 Delayed Recall Ready";
    overallBadge.classList.remove("complete");
  } else if (completionPct === 33) {
    overallBadge.textContent = "33% Complete \u2022 Step 1 Finished";
    overallBadge.classList.remove("complete");
  } else {
    overallBadge.textContent = "0% Complete \u2022 Registration \u2713 (Ready to Start)";
    overallBadge.classList.remove("complete");
  }

  // Update Brain-Only Milestone
  const brainItem = document.getElementById("milestoneBrain");
  const brainTarget = document.getElementById("milestoneBrainTarget");
  const brainStatus = document.getElementById("milestoneBrainStatus");
  const brainPctLabel = "33%";
  const isBrainActive = !isBrainDone;

  if (brainItem && brainTarget && brainStatus) {
    if (isBrainDone) {
      brainItem.className = "milestone-item done";
      brainTarget.textContent = `\u2713 (${brainPctLabel})`;
      brainStatus.textContent = "Completed";
    } else if (isBrainActive) {
      brainItem.className = "milestone-item active";
      brainTarget.textContent = brainPctLabel;
      brainStatus.textContent = "In Progress";
    } else {
      brainItem.className = "milestone-item";
      brainTarget.textContent = brainPctLabel;
      brainStatus.textContent = "Pending";
    }
  }

  // Update GenAI Milestone
  const genaiItem = document.getElementById("milestoneGenAi");
  const genaiTarget = document.getElementById("milestoneGenAiTarget");
  const genaiStatus = document.getElementById("milestoneGenAiStatus");
  const genaiPctLabel = "66%";
  const isGenAiActive = isBrainDone && !isGenAiDone;

  if (genaiItem && genaiTarget && genaiStatus) {
    if (isGenAiDone) {
      genaiItem.className = "milestone-item done";
      genaiTarget.textContent = `\u2713 (${genaiPctLabel})`;
      genaiStatus.textContent = "Completed";
    } else if (isGenAiActive) {
      genaiItem.className = "milestone-item active";
      genaiTarget.textContent = genaiPctLabel;
      genaiStatus.textContent = "In Progress";
    } else {
      genaiItem.className = "milestone-item";
      genaiTarget.textContent = genaiPctLabel;
      genaiStatus.textContent = "Pending";
    }
  }

  // Update Delayed Recall Milestone
  const recallItem = document.getElementById("milestoneRecall");
  const recallTarget = document.getElementById("milestoneRecallTarget");
  const recallStatus = document.getElementById("milestoneRecallStatus");
  const isRecallActive = isBrainDone && isGenAiDone && !isRecallDone;

  if (recallItem && recallTarget && recallStatus) {
    if (isRecallDone) {
      recallItem.className = "milestone-item done";
      recallTarget.textContent = "\u2713 (100%)";
      recallStatus.textContent = "Completed";
    } else if (isRecallActive) {
      recallItem.className = "milestone-item active";
      recallTarget.textContent = "100%";
      recallStatus.textContent = "Ready to Begin";
    } else {
      recallItem.className = "milestone-item";
      recallTarget.textContent = "100%";
      recallStatus.textContent = "Pending";
    }
  }
}

/**
 * Renders the visual step-by-step fixed sequence tracker banner
 */
function renderSequenceFlowBanner(isBrainDone, isGenAiDone, isRecallDone) {
  const bannerGroupTitle = document.getElementById("bannerGroupTitle");
  const trackContainer = document.getElementById("sequenceStepsTrack");
  if (!trackContainer) return;

  if (bannerGroupTitle) {
    bannerGroupTitle.textContent = "Fixed Protocol: Brain-Only First";
  }

  const step1Name = "Brain-Only Learning";
  const step2Name = "GenAI-Assisted Learning";
  const step1Done = isBrainDone;
  const step2Done = isGenAiDone;
  const step1Active = !isBrainDone;
  const step2Active = isBrainDone && !isGenAiDone;
  const step3Active = isBrainDone && isGenAiDone && !isRecallDone;

  trackContainer.innerHTML = `
    <div class="sequence-step-item ${step1Done ? 'completed' : (step1Active ? 'active' : '')}">
      <span class="sequence-step-num">${step1Done ? '&#10003;' : '1'}</span>
      <span>Step 1: ${step1Name}</span>
    </div>
    <span class="sequence-step-arrow">&rarr;</span>
    <div class="sequence-step-item ${step2Done ? 'completed' : (step2Active ? 'active' : '')}">
      <span class="sequence-step-num">${step2Done ? '&#10003;' : '2'}</span>
      <span>Step 2: ${step2Name}</span>
    </div>
    <span class="sequence-step-arrow">&rarr;</span>
    <div class="sequence-step-item ${isRecallDone ? 'completed' : (step3Active ? 'active' : '')}">
      <span class="sequence-step-num">${isRecallDone ? '&#10003;' : '3'}</span>
      <span>Step 3: Delayed Recall Test</span>
    </div>
  `;
}

/**
 * Dynamically renders the experimental phase cards in exact assigned sequence order
 */
function renderPhaseCards(isBrainDone, isGenAiDone, isRecallDone, brainScore, genaiScore) {
  const container = document.getElementById("phaseGridContainer");
  if (!container) return;

  const brainCardHtml = (stepNumber, isCompleted) => `
    <div class="phase-card">
      <div>
        <div class="phase-header">
          <span class="phase-number">Step 0${stepNumber}</span>
          ${isCompleted
            ? '<span class="phase-badge completed">Condition Completed</span>'
            : '<span class="phase-badge ready">Ready to Begin</span>'}
        </div>
        <h3 class="phase-name">Brain-only Learning Condition</h3>
        <p class="phase-description">
          Autonomous cognitive synthesis stage. The participant engages with complex technical reading material without access to AI tools, calculators, or external search. Evaluates organic cognitive encoding.
        </p>
        
        <div class="phase-meta">
          <div class="phase-meta-item">
            <span>Modality:</span>
            <strong>Human-Only (Self-Directed)</strong>
          </div>
          <div class="phase-meta-item">
            <span>Estimated Time:</span>
            <strong>15 Minutes</strong>
          </div>
          <div class="phase-meta-item">
            <span>Telemetry:</span>
            <strong>Time-on-task, Reading speed</strong>
          </div>
        </div>
      </div>

      <div>
          ${isCompleted
           ? `<a href="brain_only.html" class="btn btn-secondary" style="width: 100%;">Review Brain-Only (Score: ${brainScore}/10) &rarr;</a>
             <p style="font-size: 0.75rem; color: var(--text-muted); text-align: center; margin-top: 0.5rem;">Trial completed & data saved in research.db</p>`
           : `<a href="brain_only.html" class="btn btn-primary" style="width: 100%;">Start Phase 1 (Brain-Only) &rarr;</a>
             <p style="font-size: 0.75rem; color: var(--text-muted); text-align: center; margin-top: 0.5rem;">Autonomous study & assessment condition</p>`}
      </div>
    </div>
  `;

  const genaiCardHtml = (stepNumber, isCompleted) => `
    <div class="phase-card">
      <div>
        <div class="phase-header">
          <span class="phase-number">Step 0${stepNumber}</span>
          ${isCompleted
            ? '<span class="phase-badge completed">Condition Completed</span>'
            : '<span class="phase-badge ready">Ready to Begin</span>'}
        </div>
        <h3 class="phase-name">GenAI-Assisted Learning Condition</h3>
        <p class="phase-description">
          AI-augmented cognitive stage. The participant studies an equivalent conceptual topic with an embedded conversational GenAI assistant. Evaluates prompt formulation patterns, query frequency, and AI reliance.
        </p>

        <div class="phase-meta">
          <div class="phase-meta-item">
            <span>Modality:</span>
            <strong>GenAI Co-Pilot (Interactive)</strong>
          </div>
          <div class="phase-meta-item">
            <span>Estimated Time:</span>
            <strong>15 Minutes</strong>
          </div>
          <div class="phase-meta-item">
            <span>Telemetry:</span>
            <strong>Prompts, Response times, Tokens</strong>
          </div>
        </div>
      </div>

      <div>
          ${isCompleted
           ? `<a href="genai_assisted.html" class="btn btn-secondary" style="width: 100%;">Review GenAI-Assisted (Score: ${genaiScore}/10) &rarr;</a>
             <p style="font-size: 0.75rem; color: var(--text-muted); text-align: center; margin-top: 0.5rem;">Trial completed & data saved in research.db</p>`
           : `<a href="genai_assisted.html" class="btn btn-primary" style="width: 100%;">Continue Phase 2 (GenAI-Assisted) &rarr;</a>
             <p style="font-size: 0.75rem; color: var(--text-muted); text-align: center; margin-top: 0.5rem;">AI tools permitted (ChatGPT, Gemini, Copilot)</p>`}
      </div>
    </div>
  `;

  const delayedRecallCardHtml = (stepNumber, isCompleted) => {
    const brainRet = sessionStorage.getItem("brain_retention") || "87.5";
    const genAiRet = sessionStorage.getItem("genai_retention") || "Not assessed";
    const retentionSummary = genAiRet === "Not assessed"
      ? `Brain retention: ${brainRet}% (GenAI recall not assessed)`
      : `Retention: Brain ${brainRet}% vs AI ${genAiRet}%`;
    return `
    <div class="phase-card">
      <div>
        <div class="phase-header">
          <span class="phase-number">Step 0${stepNumber}</span>
          ${isCompleted
            ? '<span class="phase-badge completed">Evaluation Completed</span>'
            : '<span class="phase-badge ready">Ready to Begin</span>'}
        </div>
        <h3 class="phase-name">Delayed Recall Test</h3>
        <p class="phase-description">
          Post-intervention retention evaluation. A standardized assessment combining multiple-choice recall questions and short-answer conceptual transfer questions administered without AI assistance.
        </p>

        <div class="phase-meta">
          <div class="phase-meta-item">
            <span>Modality:</span>
            <strong>Objective Knowledge Assessment</strong>
          </div>
          <div class="phase-meta-item">
            <span>Estimated Time:</span>
            <strong>10 Minutes</strong>
          </div>
          <div class="phase-meta-item">
            <span>Metrics:</span>
            <strong>Accuracy, Confidence score, Retention rate</strong>
          </div>
        </div>
      </div>

      <div>
          ${isCompleted
            ? `<a href="delayed_recall.html" class="btn btn-secondary" style="width: 100%;">${retentionSummary} &rarr;</a>
             <p style="font-size: 0.75rem; color: var(--text-muted); text-align: center; margin-top: 0.5rem;">Full experimental evaluation completed & recorded.</p>`
           : `<a href="delayed_recall.html" class="btn btn-primary" style="width: 100%;">Start Step 3 (Delayed Recall) &rarr;</a>
             <p style="font-size: 0.75rem; color: var(--text-muted); text-align: center; margin-top: 0.5rem;">Assesses long-term retention without AI</p>`}
      </div>
    </div>
  `;
  };

  const card1 = brainCardHtml(1, isBrainDone);
  const card2 = genaiCardHtml(2, isGenAiDone);
  const card3 = delayedRecallCardHtml(3, isRecallDone);
  container.innerHTML = card1 + card2 + card3;
}

/**
 * Route guard to enforce the fixed Brain-Only -> GenAI -> Delayed Recall sequence
 * Protects dashboard.html, brain_only.html, genai_assisted.html, delayed_recall.html
 */
function enforceExperimentalSequenceGuard() {
  if (sequenceGuardExecuted) return;

  const currentPath = window.location.pathname.split("/").pop() || "index.html";
  const protectedPages = ["dashboard.html", "brain_only.html", "genai_assisted.html", "delayed_recall.html"];

  if (!protectedPages.includes(currentPath)) {
    return;
  }

  const regCompletedSession = sessionStorage.getItem("registration_completed");
  const regCompletedLocal = localStorage.getItem("registration_completed");
  const participantId = sessionStorage.getItem("participant_id") || localStorage.getItem("participant_id");
  let storedParticipant = sessionStorage.getItem("currentParticipant");

  const isRegistered = (regCompletedSession === "true" || regCompletedLocal === "true") && (participantId || storedParticipant);

  if (!isRegistered) {
    sequenceGuardExecuted = true;
    alert("Please complete participant registration before starting the experiment.");
    window.location.href = "register.html";
    return;
  }

  // Restore session data from localStorage if session storage was cleared across tabs
  if (!storedParticipant && participantId) {
    const group = sessionStorage.getItem("experiment_group") || localStorage.getItem("experiment_group") || "A";
    const seq = "brain_only_first";
    sessionStorage.setItem("participant_id", participantId);
    sessionStorage.setItem("experiment_group", group);
    sessionStorage.setItem("assigned_sequence", seq);
    sessionStorage.setItem("registration_completed", "true");
    storedParticipant = JSON.stringify({
      participantId: participantId,
      experimentGroup: group,
      assignedSequence: seq
    });
    sessionStorage.setItem("currentParticipant", storedParticipant);
  }

  sequenceGuardExecuted = true;

}

/**
 * Placeholder handler for launching experimental conditions
 */
function handlePhaseLaunch(phaseName) {
  alert(
    `[Experimental Protocol Notice]\n\n` +
    `${phaseName} selected.\n` +
    `Please proceed through Brain-Only, GenAI-Assisted, and Delayed Recall in order.`
  );
}

/**
 * Data loss prevention: warns participants before leaving page during active timers or assessments
 */
let _unloadWarningActive = false;
function setupUnloadWarning(msg = "Warning: Navigating away or refreshing will discard your ongoing experimental trial. Are you sure you want to leave?") {
  if (_unloadWarningActive) return;
  _unloadWarningActive = true;
  window.onbeforeunload = (e) => {
    e.preventDefault();
    e.returnValue = msg;
    return msg;
  };
}

function clearUnloadWarning() {
  _unloadWarningActive = false;
  window.onbeforeunload = null;
}

/**
 * Real-time quiz question counter and progress bar tracker
 */
function initQuizProgressTracker({ formId, totalQuestions, prefix, progressBarId, counterTextId, pillsWrapId }) {
  const form = document.getElementById(formId);
  if (!form) return;

  const updateProgress = () => {
    let answered = 0;
    for (let i = 1; i <= totalQuestions; i++) {
      const qKey = prefix ? `${prefix}_${i}` : `mcq_${i}`;
      const checked = form.querySelector(`input[name="${qKey}"]:checked`);
      const pill = document.getElementById(`pill_${qKey}`);
      if (checked) {
        answered++;
        if (pill) pill.classList.add("answered");
      } else {
        if (pill) pill.classList.remove("answered");
      }
    }

    const pct = Math.round((answered / totalQuestions) * 100);
    const bar = document.getElementById(progressBarId);
    if (bar) bar.style.width = `${pct}%`;

    const text = document.getElementById(counterTextId);
    if (text) {
      text.textContent = `Progress: ${answered} of ${totalQuestions} answered (${pct}%)`;
    }
  };

  form.addEventListener("change", updateProgress);
  updateProgress();
}

