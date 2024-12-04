document.getElementById("profile-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    // Collect Form Data
    const targetGoal = document.getElementById("target-goal").value;
    const profession = document.getElementById("profession").value;
    const experienceLevel = document.getElementById("experience-level").value;
    const keywords = document.getElementById("keywords").value.split(",").map(kw => kw.trim());
    const resume = document.getElementById("resume").value;

    // Create Request Payload
    const requestData = {
        target_goal: targetGoal,
        profession: profession,
        experience_level: experienceLevel,
        keywords: keywords,
        resume: resume
    };

    // Fetch API Call
    const response = await fetch("/api/generate-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
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

// Tab Switching Logic
const tabButtons = document.querySelectorAll(".tab-button");
const tabContents = document.querySelectorAll(".tab-content");

tabButtons.forEach(button => {
    button.addEventListener("click", () => {
        // Deactivate All Tabs
        tabButtons.forEach(btn => btn.classList.remove("active"));
        tabContents.forEach(content => content.style.display = "none");

        // Activate Selected Tab
        button.classList.add("active");
        const tabId = button.dataset.tab;
        document.getElementById(`tab-${tabId}`).style.display = "block";
    });
});

const statusMessage = document.getElementById("status-message");

function updateStatus(message, isError = false) {
    statusMessage.textContent = message;
    statusMessage.style.color = isError ? "red" : "black";
}

document.getElementById("profile-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    // Collect form data
    const profession = document.getElementById("profession").value;
    const experienceLevel = document.getElementById("experience-level").value;
    const keywords = document.getElementById("keywords").value.split(",").map(kw => kw.trim());

    const requestData = {
        profession: profession,
        experience_level: experienceLevel,
        keywords: keywords,
    };

    try {
        // Update status
        updateStatus("Generating profile...");

        // Call the API
        const response = await fetch("/api/generate-profile", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestData),
        });

        // Handle the response
        if (response.ok) {
            const data = await response.json();
            if (data.profile) {
                // Update status to success
                updateStatus("Profile successfully generated!");

                // Populate results in the UI
                document.getElementById("elevator-pitch").textContent = data.profile.elevator_pitch;
                document.getElementById("project-descriptions").textContent = data.profile.project_descriptions;
                document.getElementById("output").style.display = "block";
            } else {
                // Handle unexpected API response
                updateStatus("Error: Profile generation failed. Try again later.", true);
            }
        } else {
            // Handle non-200 HTTP responses
            const errorData = await response.json();
            updateStatus(`Error: ${errorData.error || "Unexpected error occurred."}`, true);
        }
    } catch (error) {
        // Handle network or other unexpected errors
        updateStatus(`Error: ${error.message}`, true);
    }
});

