document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    const navbar = document.getElementById('navbar');
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    // Shrink navbar on scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            navbar.style.padding = '0.5rem 0';
        } else {
            navbar.style.padding = '1rem 0';
        }
    });

    // Mobile menu toggle
    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        hamburger.classList.toggle('active');
    });

    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
                // Close mobile menu if open
                navLinks.classList.remove('active');
                hamburger.classList.remove('active');
            }
        });
    });

    // Paw prints animation
    const pawPrints = document.querySelector('.paw-prints');
    const pawImages = [];
    
    // Create more paw prints (10 pairs of left and right)
    for (let i = 0; i < 10; i++) {
        pawImages.push(createPawPrint('left'));
        pawImages.push(createPawPrint('right'));
    }

    // Initial paw prints animation
    function createInitialPawPrints() {
        const numInitialPaws = 8;
        for (let i = 0; i < numInitialPaws; i++) {
            setTimeout(() => {
                const paw = pawImages[i];
                const xPos = (i * (window.innerWidth / numInitialPaws)) + (Math.random() * 100 - 50);
                const yPos = Math.random() * window.innerHeight;
                
                paw.style.left = `${xPos}px`;
                paw.style.top = `${yPos}px`;
                paw.style.opacity = '1';
                
                setTimeout(() => {
                    paw.style.opacity = '0';
                }, 3000);
            }, i * 200);
        }
    }

    // Run initial animation
    createInitialPawPrints();
    setInterval(createInitialPawPrints, 10000); // Repeat every 10 seconds

    let lastScrollY = window.scrollY;
    let pawIndex = 8; // Start after initial paws

    window.addEventListener('scroll', () => {
        const currentScroll = window.scrollY;
        if (Math.abs(currentScroll - lastScrollY) > 30) { // Reduced threshold for more frequent appearance
            const paw = pawImages[pawIndex];
            const xPos = Math.random() * (window.innerWidth - 50);
            
            paw.style.left = `${xPos}px`;
            paw.style.top = `${currentScroll + Math.random() * window.innerHeight}px`;
            paw.style.opacity = '1';
            
            setTimeout(() => {
                paw.style.opacity = '0';
            }, 2000);

            pawIndex = (pawIndex + 1) % pawImages.length;
            lastScrollY = currentScroll;
        }
    });

    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements with fade-in animation
    document.querySelectorAll('.step-card, .sample-image img').forEach(el => {
        observer.observe(el);
    });

    // Testimonials Carousel
    const testimonials = document.querySelectorAll('.testimonial');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    let currentIndex = 0;

    function showTestimonial(index) {
        testimonials.forEach(testimonial => {
            testimonial.classList.remove('active');
            testimonial.style.transform = 'translateX(100%)';
        });

        testimonials[index].classList.add('active');
        testimonials[index].style.transform = 'translateX(0)';

        // Update button states
        prevBtn.style.opacity = index === 0 ? '0.5' : '1';
        nextBtn.style.opacity = index === testimonials.length - 1 ? '0.5' : '1';
    }

    function nextTestimonial() {
        if (currentIndex < testimonials.length - 1) {
            currentIndex++;
            showTestimonial(currentIndex);
        }
    }

    function prevTestimonial() {
        if (currentIndex > 0) {
            currentIndex--;
            showTestimonial(currentIndex);
        }
    }

    // Event listeners
    nextBtn.addEventListener('click', nextTestimonial);
    prevBtn.addEventListener('click', prevTestimonial);

    // Auto-advance every 5 seconds
    let autoAdvance = setInterval(function() {
        if (currentIndex === testimonials.length - 1) {
            currentIndex = -1;
        }
        nextTestimonial();
    }, 5000);

    // Pause auto-advance on hover
    const carousel = document.querySelector('.testimonials-carousel');
    carousel.addEventListener('mouseenter', () => clearInterval(autoAdvance));
    carousel.addEventListener('mouseleave', () => {
        autoAdvance = setInterval(function() {
            if (currentIndex === testimonials.length - 1) {
                currentIndex = -1;
            }
            nextTestimonial();
        }, 5000);
    });

    // Initialize
    showTestimonial(currentIndex);
});

// Helper function to create paw prints
function createPawPrint(side) {
    const paw = document.createElement('div');
    paw.className = `paw-print ${side}`;
    paw.style.cssText = `
        position: absolute;
        width: 30px;
        height: 30px;
        background: rgba(74, 44, 42, 0.2);
        border-radius: 50%;
        transform: rotate(${side === 'left' ? '-20deg' : '20deg'});
        transition: all 0.5s ease;
        opacity: 0;
    `;
    
    // Add toe beans
    for (let i = 0; i < 4; i++) {
        const bean = document.createElement('div');
        bean.style.cssText = `
            position: absolute;
            width: 12px;
            height: 12px;
            background: rgba(74, 44, 42, 0.2);
            border-radius: 50%;
            top: ${i < 2 ? '-8px' : '0'};
            left: ${i % 2 === 0 ? '-8px' : '26px'};
        `;
        paw.appendChild(bean);
    }

    document.querySelector('.paw-prints').appendChild(paw);
    return paw;
} 