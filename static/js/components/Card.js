export function Card(frontHTML, backHTML) {
  const wrapper = document.createElement("div");
  wrapper.className = "perspective w-full max-w-xl mx-auto";

  wrapper.innerHTML = `
    <div id="flip"
         class="relative w-full h-80 transition-transform duration-500 preserve-3d">

      <!-- FRONT (question) -->
      <div class="absolute w-full h-full backface-hidden flex items-center justify-center
                  text-center text-xl bg-blue-50 rounded-2xl shadow-lg p-6">
        ${frontHTML}
      </div>

      <!-- BACK (answer) -->
      <div class="absolute w-full h-full -rotate-y-180 backface-hidden flex items-center justify-center
                  text-center text-xl bg-green-50 rounded-2xl shadow-lg p-6">
        ${backHTML}
      </div>
    </div>`;

  const flip = wrapper.querySelector("#flip");

  // mouse / touch toggle
  wrapper.addEventListener("click", () => flip.classList.toggle("rotate-y-180"));
  // keyboard (space bar)
  document.addEventListener("keydown", (e) => {
    if (e.code === "Space") flip.classList.toggle("rotate-y-180");
  });

  return wrapper;
}
