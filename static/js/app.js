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
});
