function updateSubcategoryOptions() {
    var categoryId = document.getElementById("category").value;
    var subcategoryDropdown = document.getElementById("subcategory");

    // Clear existing options
    subcategoryDropdown.innerHTML = '<option value="">Select Subcategory</option>';

    if (categoryId) {
        // Request subcategories from the server
        fetch(`/pekerjaan_jasa/get-subcategories/${categoryId}/`)
            .then(response => response.json())
            .then(data => {
                // Add subcategories to the dropdown
                data.forEach(function(subcategory) {
                    var option = document.createElement("option");
                    option.value = subcategory.id;
                    option.textContent = subcategory.name;
                    subcategoryDropdown.appendChild(option);
                });
            })
            .catch(error => {
                console.error("Error fetching subcategories:", error);
            });
    }
}
