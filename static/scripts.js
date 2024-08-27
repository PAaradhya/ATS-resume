document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the form from submitting the traditional way

    let formData = new FormData(this); // Create a FormData object to hold form data

    // Send an AJAX request to the server with the form data
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json()) // Parse the response as JSON
    .then(data => {
        let resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `
            <h2>Resume Analysis Results</h2>
            <p><strong>Match Percentage:</strong> ${data.match_percentage.toFixed(2)}%</p>
            <p><strong>Matched Keywords:</strong> ${data.matched_keywords.join(', ')}</p>
            <p><strong>Missing Keywords:</strong> ${data.missing_keywords.join(', ')}</p>
        `;
    })
    .catch(error => {
        console.error('Error:', error);
        let resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `<p>Error processing the resume. Please try again later.</p>`;
    });
});
