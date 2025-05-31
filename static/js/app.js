// static/js/app.js
import { Card } from "./components/Card.js";

const API = "http://127.0.0.1:8000";

let cards = [];
let current = 0;

// ---------------------------
// 1) LOAD / REVIEW LOGIC
// ---------------------------

document.getElementById("loadBtn").addEventListener("click", async () => {
  const tag = document.getElementById("tagFilter").value.trim();
  const dueOnly = document.getElementById("dueOnlyCheckbox").checked;

  const url = new URL(`${API}/cards`);
  if (tag) {
    url.searchParams.set("tags", tag);
    url.searchParams.set("mode", "any");
  }
  url.searchParams.set("due_only", dueOnly ? "true" : "false");

  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Status ${res.status}`);
    cards = await res.json();
    current = 0;
    renderCard();
  } catch (err) {
    console.error("Failed to load cards", err);
    document.getElementById("cardContainer").innerHTML = `
      <p class="text-red-600">Failed to load cards. Check console for details.</p>
    `;
  }
});


function renderCard() {
  const container = document.getElementById("cardContainer");
  container.innerHTML = "";

  if (current >= cards.length) {
    container.innerHTML = `<p class="text-center text-xl">No more cards due!</p>`;
    return;
  }

  const card = cards[current];
  const frontSide = card.sides.find((s) => s.position === "front");
  const backSide  = card.sides.find((s) => s.position === "back");

  // Fetch both assets, then build the flipped card component
  Promise.all([
    fetch(`${API}/assets/${frontSide.asset_id}`).then((r) => r.json()),
    fetch(`${API}/assets/${backSide.asset_id}`).then((r) => r.json()),
  ])
    .then(([frontAsset, backAsset]) => {
      const frontHTML = renderAssetContent(frontAsset);
      const backHTML  = renderAssetContent(backAsset);
      const cardElement = Card(frontHTML, backHTML);

      // Build the rating buttons (0–5)
      const controls = document.createElement("div");
      controls.className = "mt-6 flex gap-4 justify-center";
      for (let rating = 0; rating <= 5; rating++) {
        const btn = document.createElement("button");
        btn.textContent = rating;
        btn.className =
          "w-12 h-12 flex items-center justify-center text-xl font-medium text-white rounded " +
          (rating >= 3
            ? "bg-green-500 hover:bg-green-600"
            : "bg-red-500 hover:bg-red-600");
        btn.onclick = () => submitReview(card.id, rating);
        controls.appendChild(btn);
      }

      // === THE IMPORTANT BIT: STACK CARD + BUTTONS VERTICALLY ===
      const wrapper = document.createElement("div");
      // flex-col makes them stack; items-center centers them horizontally. 
      // space-y-6 adds some vertical gap.
      wrapper.className = "flex flex-col items-center space-y-6";
      wrapper.appendChild(cardElement);
      wrapper.appendChild(controls);

      container.innerHTML = "";
      container.appendChild(wrapper);
    })
    .catch((err) => {
      console.error("Failed to fetch asset data", err);
      container.innerHTML = `<p class="text-red-600">Error loading card.</p>`;
    });
}

function renderAssetContent(asset) {
  if (asset.type === "text") {
    // Show plain text inside a <span>
    return `<span class="px-4">${asset.text}</span>`;
  } else if (asset.type === "image") {
    // Show an <img>
    return `<img src="/static/${asset.path}" class="mx-auto max-h-64 rounded-lg" alt="Flashcard image"/>`;
  } else if (asset.type === "audio") {
    // Show an <audio> player
    return `<audio controls class="mx-auto">
              <source src="/static/${asset.path}" />
            </audio>`;
  } else {
    return `<em>Unsupported asset type</em>`;
  }
}

async function submitReview(cardId, rating) {
  try {
    const res = await fetch(`${API}/reviews`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ card_id: cardId, rating }),
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    current++;
    renderCard();
  } catch (err) {
    console.error("Failed to record review", err);
    alert("Failed to record review. Check console for details.");
  }
}

// ---------------------------
// 2) CREATE CARD FORM LOGIC
// ---------------------------

// Whenever the user toggles “Front Type” or “Back Type,” show/hide the proper field:
const frontTypeRadios = document.getElementsByName("frontType");
const backTypeRadios  = document.getElementsByName("backType");
const frontTextElem   = document.getElementById("frontText");
const frontFileElem   = document.getElementById("frontFile");
const backTextElem    = document.getElementById("backText");
const backFileElem    = document.getElementById("backFile");

function updateFrontInputs() {
  const chosen = Array.from(frontTypeRadios).find((r) => r.checked).value;
  if (chosen === "text") {
    frontTextElem.classList.remove("hidden");
    frontFileElem.classList.add("hidden");
    frontFileElem.value = ""; // clear previous
  } else {
    frontTextElem.classList.add("hidden");
    frontFileElem.classList.remove("hidden");
    frontTextElem.value = "";
  }
}

function updateBackInputs() {
  const chosen = Array.from(backTypeRadios).find((r) => r.checked).value;
  if (chosen === "text") {
    backTextElem.classList.remove("hidden");
    backFileElem.classList.add("hidden");
    backFileElem.value = "";
  } else {
    backTextElem.classList.add("hidden");
    backFileElem.classList.remove("hidden");
    backTextElem.value = "";
  }
}

// Attach listeners
frontTypeRadios.forEach((r) => r.addEventListener("change", updateFrontInputs));
backTypeRadios.forEach((r) => r.addEventListener("change", updateBackInputs));

// Run once on page load to set initial state
updateFrontInputs();
updateBackInputs();


// Handle form submission
document.getElementById("createCardForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  // 1) Gather front side data
  const frontType = Array.from(frontTypeRadios).find((r) => r.checked).value;
  let frontAsset, backAsset;

  try {
    // Upload front asset
    if (frontType === "text") {
      const text = frontTextElem.value.trim();
      if (!text) {
        alert("Front text cannot be empty.");
        return;
      }
      const frontForm = new FormData();
      frontForm.append("type", "text");
      frontForm.append("file", new Blob([text], { type: "text/plain" }), "front.txt");

      const frontRes = await fetch(`${API}/assets`, {
        method: "POST",
        body: frontForm,
      });
      if (!frontRes.ok) {
        throw new Error(`Front asset upload failed: ${frontRes.status}`);
      }
      frontAsset = await frontRes.json();
    } else {
      // image or audio
      const chosenFile = frontFileElem.files[0];
      if (!chosenFile) {
        alert("Please choose a file for the front side.");
        return;
      }
      const frontForm = new FormData();
      frontForm.append("type", frontType); // "image" or "audio"
      frontForm.append("file", chosenFile, chosenFile.name);

      const frontRes = await fetch(`${API}/assets`, {
        method: "POST",
        body: frontForm,
      });
      if (!frontRes.ok) {
        throw new Error(`Front asset upload failed: ${frontRes.status}`);
      }
      frontAsset = await frontRes.json();
    }

    // 2) Gather back side data
    const backType = Array.from(backTypeRadios).find((r) => r.checked).value;
    if (backType === "text") {
      const text = backTextElem.value.trim();
      if (!text) {
        alert("Back text cannot be empty.");
        return;
      }
      const backForm = new FormData();
      backForm.append("type", "text");
      backForm.append("file", new Blob([text], { type: "text/plain" }), "back.txt");

      const backRes = await fetch(`${API}/assets`, {
        method: "POST",
        body: backForm,
      });
      if (!backRes.ok) {
        throw new Error(`Back asset upload failed: ${backRes.status}`);
      }
      backAsset = await backRes.json();
    } else {
      // image or audio
      const chosenFile = backFileElem.files[0];
      if (!chosenFile) {
        alert("Please choose a file for the back side.");
        return;
      }
      const backForm = new FormData();
      backForm.append("type", backType); // "image" or "audio"
      backForm.append("file", chosenFile, chosenFile.name);

      const backRes = await fetch(`${API}/assets`, {
        method: "POST",
        body: backForm,
      });
      if (!backRes.ok) {
        throw new Error(`Back asset upload failed: ${backRes.status}`);
      }
      backAsset = await backRes.json();
    }

    // 3) Tags (comma-separated)
    const tagsRaw = document.getElementById("tagsInput").value.trim();
    const tags = tagsRaw
      .split(",")
      .map((t) => t.trim())
      .filter((t) => t.length);

    // 4) Finally, create the card
    const payload = {
      front_asset_id: frontAsset.id,
      back_asset_id: backAsset.id,
      tags,
    };
    const cardRes = await fetch(`${API}/cards`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!cardRes.ok) {
      throw new Error(`Card creation failed: ${cardRes.status}`);
    }

    // Success: clear form & show message
    document.getElementById("createCardForm").reset();
    updateFrontInputs();
    updateBackInputs();
    const msg = document.getElementById("createMsg");
    msg.classList.remove("hidden");
    setTimeout(() => msg.classList.add("hidden"), 3000);
  } catch (err) {
    console.error("Error during card creation:", err);
    alert("Something went wrong creating the card. See console for details.");
  }
});
