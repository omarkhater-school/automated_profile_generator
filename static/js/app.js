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

    // Profile Upgrade Form
    const profileUpgradeForm = document.getElementById("profile-upgrade-form");
    const outputSection = document.getElementById("output-section");
    const elevatorPitchContent = document.getElementById("elevator-pitch-content");
    const aboutMeContent = document.getElementById("project-descriptions-content");
    const reasonContainer = document.getElementById("reason-section"); // Updated variable name
    const reasonContent = document.getElementById("reason-content"); // Inner content of the reason section
    const showReasonButton = document.getElementById("show-reason-button");
    const retrievedKeywordsSection = document.getElementById("retrieved-keywords-section");
    const retrievedKeywordsContent = document.getElementById("retrieved-keywords-content");
    const toggleKeywordsButton = document.getElementById("toggle-keywords-button");

    if (profileUpgradeForm) {
        profileUpgradeForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            // Collect input data
            const profession = document.getElementById("profession").value;
            const experienceLevel = document.getElementById("experience-level").value;
            const keywords = document.getElementById("keywords").value.split(",").map((kw) => kw.trim());
            const background = document.getElementById("background").value;

            try {
                // Call the API
                const response = await fetch("/api/generate-profile", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        profession,
                        experience_level: experienceLevel,
                        keywords,
                        background,
                    }),
                });

                const data = await response.json();
                console.log("Response data: ", data);

                if (response.ok && data.profile) {
                    // Display output section
                    outputSection.style.display = "block";

                    // Populate Elevator Pitch
                    elevatorPitchContent.innerHTML = data.profile.elevator_pitch || "No elevator pitch generated.";

                    // Populate About Me
                    aboutMeContent.innerHTML = data.profile["About Me"] || "No About Me section generated.";

                    // Populate Retrieved Keywords
                    if (data.profile.retrieved_keywords && Array.isArray(data.profile.retrieved_keywords)) {
                        retrievedKeywordsSection.style.display = "block";
                        retrievedKeywordsContent.querySelector("p").innerText = data.profile.retrieved_keywords.join(", ");
                    } else {
                        retrievedKeywordsSection.style.display = "none";
                    }

                    // Populate Reason (optional)
                    if (data.profile.reason) {
                        reasonContainer.style.display = "block"; // Show the reason container
                        reasonContent.querySelector("p").innerText = data.profile.reason;
                        reasonContent.style.display = "none"; // Keep content initially hidden for toggle
                    } else {
                        reasonContainer.style.display = "none"; // Hide the entire container if no reason is provided
                    }
                } else {
                    console.error("API response error: ", data);
                    alert(`Error: ${data.error || "Unexpected response from the server."}`);
                }
            } catch (error) {
                console.error("Error generating profile: ", error);
                alert("An unexpected error occurred. Please try again later.");
            }
        });
    }

    // Handle Keywords Toggle
    if (toggleKeywordsButton) {
        toggleKeywordsButton.addEventListener("click", () => {
            const isVisible = retrievedKeywordsContent.style.display === "block";
            retrievedKeywordsContent.style.display = isVisible ? "none" : "block";
            toggleKeywordsButton.textContent = isVisible ? "Show Retrieved Keywords" : "Hide Retrieved Keywords";
        });
    } else {
        console.warn("Toggle keywords button not found in the DOM.");
    }

    // Handle Reason Toggle
    if (showReasonButton) {
        showReasonButton.addEventListener("click", () => {
            const isVisible = reasonContent.style.display === "block";
            reasonContent.style.display = isVisible ? "none" : "block";
            showReasonButton.textContent = isVisible ? "Show Reason" : "Hide Reason";
        });
    } else {
        console.warn("Show reason button not found in the DOM.");
    }


    // Add toggle functionality for collapsible sections
    document.addEventListener("click", (event) => {
        if (event.target.classList.contains("collapsible-button")) {
            const content = event.target.nextElementSibling;
            content.style.display = content.style.display === "block" ? "none" : "block";
        }
    });

    // Accordion Toggle
    document.querySelectorAll(".accordion-button").forEach((button) => {
        button.addEventListener("click", () => {
            const accordionItem = button.parentElement;
            accordionItem.classList.toggle("active");
        });
    });
});
