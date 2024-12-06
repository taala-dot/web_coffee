
const scrollHeader = () => {
    const header = document.getElementById('header')

    this.scrollY >= 50 ? header.classList.add('scroll-header')
        : header.classList.remove('scroll-header')
}

window.addEventListener('scroll', scrollHeader)

const scrollUp = () => {
    const scrollUp = document.getElementById('scroll-up')

    this.scrollY >= 350 ? scrollUp.classList.add('show-scroll')
        : scrollUp.classList.remove('show-scroll')
}

window.addEventListener('scroll', scrollUp)

const section = document.querySelectorAll('section[id]')

const scrollActive = () => {
    const scrollY = window.pageYOffset

    section.forEach(current => {
        const sectionHeight = current.offsetHeight,
            sectionTop = current.offsetTop - 58,
            sectionId = current.getAttribute('id'),
            sectionClass = document.querySelector('.nav__menu a[href*=' + sectionId + ']')

        if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
            sectionClass.classList.add('active-link')
        } else {
            sectionClass.classList.remove('active-link')
        }
    })
}

window.addEventListener('scroll', scrollActive)

const sr = ScrollReveal({
    origin: 'top',
    distance: '60px',
    duration: 2500,
    delay: 400,
    reset: true
})

sr.reveal(`.home__data, .products__data, .steps__content`)
sr.reveal(`.home__img`, {origin: 'bottom'})
sr.reveal(`.products__card`, {interval: 100})
sr.reveal(`.about__img, .testimonial__img`, {origin: 'right'})
sr.reveal(`.about__data, .testimonial__data`, {origin: 'left'})

function fetchProducts() {
    fetch('http://127.0.0.1:8000/api/products/')  // Замените на ваш URL
        .then(response => response.json())
        .then(data => {
            const productsContainer = document.querySelector('.products__content');
            data.products.forEach(product => {
                const productCard = `
                    <article class="products__card">
                        <img src="assets/type of coffee/product-coffee-1.png" alt="products image" class="products__img">
                        <h3 class="products__name">${product.name}</h3>
                        <span class="products__price">$${product.price}</span>
                        <button onclick="purchaseProduct(${product.id})">Buy</button>
                    </article>
                `;
                productsContainer.innerHTML += productCard;
            });
        })
        .catch(error => console.error('Error fetching products:', error));
}

fetchProducts();

function purchaseProduct(productId) {
    fetch('http://127.0.0.1:8000/api/purchase/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer <your_token_here>',  // Авторизация через токен или куки
        },
        body: JSON.stringify({product_id: productId}),
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert('Product purchased successfully!');
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => console.error('Error purchasing product:', error));
}
