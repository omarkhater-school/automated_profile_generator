document.getElementById("profile-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const profession = document.getElementById("profession").value;
    const experienceLevel = document.getElementById("experience-level").value;
    const keywords = document.getElementById("keywords").value.split(",").map(kw => kw.trim());

    const response = await fetch("/api/generate-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profession, experience_level: experienceLevel, keywords }),
    });

    const data = await response.json();
    if (data.profile) {
        document.getElementById("elevator-pitch").textContent = data.profile.elevator_pitch;
        document.getElementById("project-descriptions").textContent = data.profile.project_descriptions;
        document.getElementById("output").style.display = "block";
    } else {
        alert("Error generating profile: " + (data.error || "Unknown error"));
    }
});
