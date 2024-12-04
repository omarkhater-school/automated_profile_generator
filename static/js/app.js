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
    const formData = {
        target_goal: document.getElementById("target-goal").value,
        profession: document.getElementById("profession").value,
        experience_level: document.getElementById("experience-level").value,
        keywords: document.getElementById("keywords").value.split(",").map(kw => kw.trim()),
    };

    // Update status
    updateStatus("Generating profile...");

    try {
        const response = await fetch("/api/generate-profile", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData),
        });

        const data = await response.json();

        if (response.ok && data.profile) {
            updateStatus("Profile generated successfully!");

            // Populate selector with available profile elements
            const selector = document.getElementById("profile-element-selector");
            const profileContent = document.getElementById("profile-content");

            selector.innerHTML = ""; // Clear previous options
            profileContent.innerHTML = ""; // Clear previous content

            Object.entries(data.profile).forEach(([key, value]) => {
                // Add an option for each profile element
                const option = document.createElement("option");
                option.value = key;
                option.textContent = key.replace(/_/g, " "); // Make it human-readable
                selector.appendChild(option);
            });

            // Display the first profile element by default
            selector.addEventListener("change", () => {
                const selectedKey = selector.value;
                profileContent.textContent = data.profile[selectedKey] || "No content available.";
            });

            // Trigger change to display first item
            selector.dispatchEvent(new Event("change"));

            // Show the output section
            document.getElementById("output").style.display = "block";
        } else {
            updateStatus("Error: Unable to generate profile.");
        }
    } catch (error) {
        updateStatus(`Error: ${error.message}`);
    }
});



document.getElementById("check-health").addEventListener("click", async function () {
    const healthIndicators = document.getElementById("health-indicators");
    healthIndicators.innerHTML = "<li>Checking system health...</li>";

    try {
        const response = await fetch("/api/health-check");
        if (response.ok) {
            const data = await response.json();
            healthIndicators.innerHTML = "";

            Object.entries(data.health).forEach(([key, value]) => {
                const statusColor = value.status === "healthy" ? "green" : "red";
                const li = document.createElement("li");
                li.innerHTML = `<strong style="color: ${statusColor};">${key.toUpperCase()}:</strong> ${value.message}`;
                healthIndicators.appendChild(li);
            });
        } else {
            healthIndicators.innerHTML = "<li style='color: red;'>Health check failed. Please try again later.</li>";
        }
    } catch (error) {
        healthIndicators.innerHTML = `<li style='color: red;'>Error: ${error.message}</li>`;
    }
});
