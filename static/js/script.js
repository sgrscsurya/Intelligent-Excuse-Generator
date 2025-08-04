document.getElementById("excuseForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const situation = document.getElementById("situation").value;

    const response = await fetch("/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ situation })
    });

    const data = await response.json();
    document.getElementById("result").innerText = data.excuse;
});
