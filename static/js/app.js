import { Card } from "./components/Card.js";

const API = "http://127.0.0.1:8000";

let cards = [];
let current = 0;

document.getElementById("loadBtn").addEventListener("click", async () => {
  const tag = document.getElementById("tagFilter").value.trim();
  const url = new URL(`${API}/cards`);
  url.searchParams.set("tags", tag);
  url.searchParams.set("mode", "any");
  url.searchParams.set("due_only", "false"); // change to true later for actual review sessions

  try {
    const res = await fetch(url);
    cards = await res.json();
    current = 0;
    renderCard();
  } catch (err) {
    console.error("Failed to load cards", err);
    document.getElementById("cardContainer").innerHTML = `<p class="text-red-600">Failed to load cards.</p>`;
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

  Promise.all([
    fetch(`${API}/assets/${card.sides.find(s => s.position === "front").asset_id}`).then(r => r.json()),
    fetch(`${API}/assets/${card.sides.find(s => s.position === "back").asset_id}`).then(r => r.json())
  ]).then(([frontAsset, backAsset]) => {
    const frontHTML = renderAssetContent(frontAsset);
    const backHTML  = renderAssetContent(backAsset);
    const cardElement = Card(frontHTML, backHTML);

    const controls = document.createElement("div");
    controls.className = "mt-6 flex gap-4 justify-center";
    for (let i = 0; i <= 5; i++) {
      const btn = document.createElement("button");
      btn.textContent = i;
      btn.className = "px-4 py-2 rounded text-white " + (i >= 3 ? "bg-green-500" : "bg-red-500");
      btn.onclick = () => submitReview(card.id, i);
      controls.appendChild(btn);
    }

    container.replaceChildren(cardElement, controls);
  }).catch(err => {
    console.error("Failed to fetch asset data", err);
    container.innerHTML = `<p class="text-red-600">Error loading card.</p>`;
  });
}

function renderAssetContent(asset) {
  if (asset.type === "text") {
    return `<span>${asset.text}</span>`;
  } else if (asset.type === "image") {
    return `<img src="${asset.path}" class="max-h-60 rounded-xl mx-auto" />`;
  } else if (asset.type === "audio") {
    return `<audio controls class="mx-auto"><source src="${asset.path}"/></audio>`;
  } else {
    return `<em>Unsupported asset type</em>`;
  }
}

async function submitReview(cardId, rating) {
  try {
    await fetch(`${API}/reviews`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ card_id: cardId, rating })
    });
    current++;
    renderCard();
  } catch (err) {
    alert("Failed to record review.");
    console.error(err);
  }
}

document.getElementById("createCardForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const frontText = document.getElementById("frontText").value.trim();
  const backText = document.getElementById("backText").value.trim();
  const tagsRaw = document.getElementById("tagsInput").value.trim();

  if (!frontText || !backText) {
    alert("Front and back text are required.");
    return;
  }

  try {
    // Upload front text
    const frontForm = new FormData();
    frontForm.append("type", "text");
    frontForm.append("file", new Blob([frontText], { type: "text/plain" }), "front.txt");
    const frontRes = await fetch(`${API}/assets`, { method: "POST", body: frontForm });
    const frontAsset = await frontRes.json();

    // Upload back text
    const backForm = new FormData();
    backForm.append("type", "text");
    backForm.append("file", new Blob([backText], { type: "text/plain" }), "back.txt");
    const backRes = await fetch(`${API}/assets`, { method: "POST", body: backForm });
    const backAsset = await backRes.json();

    // Create card
    const tags = tagsRaw.split(",").map(tag => tag.trim()).filter(tag => tag.length > 0);
    const cardPayload = {
      front_asset_id: frontAsset.id,
      back_asset_id: backAsset.id,
      tags
    };

    const cardRes = await fetch(`${API}/cards`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cardPayload)
    });

    if (cardRes.ok) {
      document.getElementById("createCardForm").reset();
      document.getElementById("createMsg").classList.remove("hidden");
      setTimeout(() => document.getElementById("createMsg").classList.add("hidden"), 3000);
    } else {
      alert("Something went wrong creating the card.");
    }
  } catch (err) {
    console.error("Error during card creation", err);
    alert("Something went wrong uploading assets or creating the card.");
  }
});
