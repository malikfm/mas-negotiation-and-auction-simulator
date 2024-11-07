document.addEventListener("DOMContentLoaded", () => {
    const hotelSelect = document.getElementById("hotel-select");
    const tagSelect = document.getElementById("tag-select");
    const generateBtn = document.getElementById("generate-btn");
    const resultDiv = document.getElementById("result");

    // Fetch hotels and populate select
    fetch("/hotels")
        .then(response => response.json())
        .then(hotels => {
            hotels.forEach(hotel => {
                const option = document.createElement("option");
                option.value = hotel.id;
                option.textContent = hotel.name;
                hotelSelect.appendChild(option);
            });
        });

    // Fetch tags and populate select
    fetch("/tags")
        .then(response => response.json())
        .then(tags => {
            tags.forEach(tag => {
                const option = document.createElement("option");
                option.value = tag.name;
                option.textContent = tag.name;
                tagSelect.appendChild(option);
            });
        });

    generateBtn.addEventListener("click", () => {
        const hotelId = hotelSelect.value;
        const tag = tagSelect.value;

        if (!hotelId || !tag) {
            resultDiv.textContent = "Please select both a hotel and a category.";
            return;
        }

        fetch("/plan_trip", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ hotel_id: parseInt(hotelId), tag }),
        })
            .then(response => response.json())
            .then(plan => {
                let resultHTML = "<h2>Trip Plan</h2>";
                let total_places = plan.destinations.length;

                plan.destinations.forEach((item, index) => {
                    if (index == 0)
                        resultHTML += `<p style="color: #000000;"><b>${index + 1}. ${item}</b></p><blockquote>Next destination ${plan.distances[index + 1].toFixed(2)} km</blockquote>`;
                    else if (index == total_places - 1)
                        resultHTML += `<p style="color: #000000;"><b>${index + 1}. ${item}</b></p>`;
                    else
                        resultHTML += `<p style="color: #000000;">${index + 1}. ${item}</p><blockquote>Next destination ${plan.distances[index + 1].toFixed(2)} km</blockquote>`;
                });
                resultHTML += `<hr><p><strong>Total distance:</strong> ${plan.total_distance.toFixed(2)} km</p>`;
                resultDiv.innerHTML = resultHTML;
            })
            .catch(error => {
                resultDiv.textContent = "An error occurred while generating the trip plan.";
                console.error("Error:", error);
            });
    });
});
