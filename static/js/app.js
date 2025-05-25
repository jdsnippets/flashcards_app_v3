// frontend/js/app.js

const API = "http://127.0.0.1:8000";

let cards = [];
let current = 0;

document.getElementById("loadBtn").addEventListener("click", async () => {
  const tag = document.getElementById("tagFilter").value.trim();
  const url = new URL(`${API}/cards`);
  url.searchParams.set("tags", tag);
  url.searchParams.set("mode", "any");
  url.searchParams.set("due_only", "true");

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
