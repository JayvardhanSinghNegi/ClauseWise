const form = document.getElementById("uploadForm");
const fileInput = document.getElementById("fileInput");
const resultDiv = document.getElementById("result");
const summaryText = document.getElementById("summaryText");
const confidenceScore = document.getElementById("confidenceScore");
const shareBtn = document.getElementById("shareBtn");
const shareMsg = document.getElementById("shareMsg");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (!fileInput.files.length) {
    alert("Please upload a file.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  summaryText.textContent = "Processing...";
  confidenceScore.textContent = "";
  shareMsg.textContent = "";
  resultDiv.style.display = "block";

  try {
    const res = await fetch("/explain", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Server error: ${text}`);
    }

    const data = await res.json();
    summaryText.textContent = data.summary;
    confidenceScore.textContent = data.confidence_score || "N/A";

    shareBtn.onclick = () => {
      navigator.clipboard.writeText(window.location.origin + data.share_link);
      shareMsg.textContent = "Shareable link copied to clipboard!";
    };
  } catch (err) {
    summaryText.textContent = "Error: " + err.message;
  }
});
