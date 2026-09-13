/* Installability and offline shell. iOS Safari exposes installation through Share > Add to Home Screen. */
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register((window.LPE_BASE||"/")+"service-worker.js", {scope: window.LPE_BASE||"/"}).catch(() => {}));
}
