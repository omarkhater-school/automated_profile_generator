document.addEventListener("DOMContentLoaded", () => {
    // System Health Check
    const healthButton = document.getElementById("check-health");
    const healthIndicators = document.getElementById("health-indicators");

    if (healthButton) {
        healthButton.addEventListener("click", async () => {
            healthIndicators.innerHTML = "<li>Checking system health...</li>";

            try {
                const response = await fetch("/api/health-check");
                const data = await response.json();

                healthIndicators.innerHTML = "";

                if (data.health) {
                    Object.entries(data.health).forEach(([key, value]) => {
                        const statusColor = value.status === "healthy" ? "green" : "red";
                        const listItem = document.createElement("li");
                        listItem.innerHTML = `
                            <strong style="color: ${statusColor};">${key.toUpperCase()}:</strong> ${value.message}
                        `;
                        healthIndicators.appendChild(listItem);
                    });
                } else {
                    healthIndicators.innerHTML = "<li style='color: red;'>Error: Unable to retrieve health data.</li>";
                }
            } catch (error) {
                healthIndicators.innerHTML = `<li style='color: red;'>Error: ${error.message}</li>`;
            }
        });
    }

    // Feedback Submission
    const feedbackForm = document.getElementById("feedback-form");

    if (feedbackForm) {
        feedbackForm.addEventListener("submit", async (e) => {
            e.preventDefault(); // Prevent the default form submission

            // Get form data
            const formData = new FormData(feedbackForm);
            const stars = formData.get("stars");
            const comments = formData.get("comments");

            try {
                // Send feedback to the server
                const response = await fetch("/submit-feedback", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ stars, comments }),
                });

                const data = await response.json();

                if (response.ok) {
                    alert(data.message); // Notify user of success
                    feedbackForm.reset(); // Clear the form after submission
                } else {
                    alert(`Error: ${data.error}`);
                }
            } catch (error) {
                console.error("Error submitting feedback:", error);
                alert("An unexpected error occurred. Please try again later.");
            }
        });
    }

    // Profile Upgrade Form Submission
    const profileUpgradeForm = document.getElementById("profile-upgrade-form");
    const outputSection = document.getElementById("output-section");
    const elevatorPitchContent = document.getElementById("elevator-pitch-content");
    const projectDescriptionsContent = document.getElementById("project-descriptions-content");

    if (profileUpgradeForm) {
        profileUpgradeForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            // Collect input data
            const profession = document.getElementById("profession").value;
            const experienceLevel = document.getElementById("experience-level").value;
            const keywords = document.getElementById("keywords").value;

            try {
                // Call the API to generate the profile
                const response = await fetch("/api/generate-profile", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ profession, experience_level: experienceLevel, keywords: keywords.split(",") }),
                });

                const data = await response.json();

                if (response.ok) {
                    // Display the generated profile
                    outputSection.style.display = "block";
                    elevatorPitchContent.innerHTML = data.profile.elevator_pitch;
                    projectDescriptionsContent.innerHTML = data.profile.project_descriptions;
                } else {
                    alert(`Error: ${data.error}`);
                }
            } catch (error) {
                console.error("Error generating profile:", error);
                alert("An unexpected error occurred. Please try again later.");
            }
        });
    }

    // Accordion Toggle
    document.querySelectorAll(".accordion-button").forEach((button) => {
        button.addEventListener("click", () => {
            const accordionItem = button.parentElement;
            accordionItem.classList.toggle("active");
        });
    });
});
