// frontend/js/app.js

const API = "http://127.0.0.1:8000";

let cards = [];
let current = 0;

document.getElementById("loadBtn").addEventListener("click", async () => {
  const tag = document.getElementById("tagFilter").value.trim();
  const url = new URL(`${API}/cards`);
  url.searchParams.set("tags", tag);
  url.searchParams.set("mode", "any");
  //--not yet--|url.searchParams.set("due_only", "true");
  url.searchParams.set("due_only", "false");


  const res = await fetch(url);
  cards = await res.json();
  current = 0;
  renderCard();
});

function renderCard() {
  const container = document.getElementById("cardContainer");
  container.innerHTML = "";

  if (current >= cards.length) {
    container.innerHTML = `<p class="text-center text-xl">No more cards due!</p>`;
    return;
  }

  const card = cards[current];
  // Build front view
  const front = document.createElement("div");
  front.className = "bg-white p-6 rounded shadow text-center text-2xl cursor-pointer";
  front.id = "flashcard-front";
  front.textContent = ""; // will append asset
  renderSide(card.sides.find(s => s.position === "front"), front);

  // Build back + ratings
  const back = document.createElement("div");
  back.className = "hidden bg-white p-6 rounded shadow text-center space-y-4";
  back.id = "flashcard-back";

  renderSide(card.sides.find(s => s.position === "back"), back);

  // Rating buttons
  const ratingDiv = document.createElement("div");
  ratingDiv.className = "flex justify-center space-x-2 mt-4";
  for (let i = 0; i <= 5; i++) {
    const btn = document.createElement("button");
    btn.textContent = i;
    btn.className = "px-3 py-1 border rounded";
    btn.onclick = () => submitReview(card.id, i);
    ratingDiv.appendChild(btn);
  }
  back.appendChild(ratingDiv);

  // Toggle flip
  front.onclick = () => {
    front.classList.add("hidden");
    back.classList.remove("hidden");
  };
  back.onclick = () => {
    front.classList.remove("hidden");
    back.classList.add("hidden");
  };

  container.appendChild(front);
  container.appendChild(back);
}

async function submitReview(cardId, rating) {
  await fetch(`${API}/reviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ card_id: cardId, rating })
  });
  current++;
  renderCard();
}

function renderSide(side, el) {
  // Fetch asset details
  fetch(`${API}/assets/${side.asset_id}`)
    .then(r => r.json())
    .then(asset => {
      if (asset.type === "text") {
        el.textContent = asset.text;
      } else if (asset.type === "image") {
        const img = document.createElement("img");
        img.src = asset.path;
        img.className = "mx-auto max-h-64";
        el.appendChild(img);
      } else if (asset.type === "audio") {
        const audio = document.createElement("audio");
        audio.controls = true;
        audio.src = asset.path;
        el.appendChild(audio);
      }
    });
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

  // 1. Upload front text asset
  const frontForm = new FormData();
  frontForm.append("type", "text");
  frontForm.append("file", new Blob([frontText], { type: "text/plain" }), "front.txt");
  const frontRes = await fetch(`${API}/assets`, {
    method: "POST",
    body: frontForm
  });
  const frontAsset = await frontRes.json();

  // 2. Upload back text asset
  const backForm = new FormData();
  backForm.append("type", "text");
  backForm.append("file", new Blob([backText], { type: "text/plain" }), "back.txt");
  const backRes = await fetch(`${API}/assets`, {
    method: "POST",
    body: backForm
  });
  const backAsset = await backRes.json();

  // 3. Create the card
  const tags = tagsRaw
    .split(",")
    .map(tag => tag.trim())
    .filter(tag => tag.length > 0);

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
    setTimeout(() => {
      document.getElementById("createMsg").classList.add("hidden");
    }, 3000);
  } else {
    alert("Something went wrong creating the card.");
  }
});
