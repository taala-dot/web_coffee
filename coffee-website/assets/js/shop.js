const searchField = document.getElementById('searchField');
const productCards = document.querySelectorAll('.product-card');
const separators = document.querySelectorAll('.hb');
const noResultsMessage = document.getElementById('no-results');
searchField.addEventListener('input', () => {
    const searchTerm = searchField.value.toLowerCase();
    let resultsFound = false;

    productCards.forEach((card, index) => {
        const cardTitle = card.querySelector('h3').textContent.toLowerCase();
        const cardSubtitle = card.querySelector('h4').textContent.toLowerCase();
        if (cardTitle.includes(searchTerm) || cardSubtitle.includes(searchTerm)) {
            card.style.display = 'block';
            if (separators[index]) separators[index].style.display = 'block';
            resultsFound = true;
        }else{
            card.style.display = 'none';
            if (separators[index]) separators[index].style.display = 'none';
        }
    });
    if (!resultsFound) {
        noResultsMessage.style.display = 'block';
    } else {
        noResultsMessage.style.display = 'none';
    }
});

