// Main JavaScript for Information Theory Project
// Handles animations, interactions, and dynamic content

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initScrollAnimations();
    initHuffmanPreview();
    initParticleBackground();
    initSmoothScrolling();
});

// Scroll-triggered animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                
                anime({
                    targets: element,
                    opacity: [0, 1],
                    translateY: [30, 0],
                    duration: 800,
                    easing: 'easeOutCubic',
                    delay: anime.stagger(100)
                });
                
                observer.unobserve(element);
            }
        });
    }, observerOptions);

    // Observe all slide-in elements
    document.querySelectorAll('.slide-in').forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
}

// Huffman tree preview visualization
function initHuffmanPreview() {
    const container = document.getElementById('huffman-preview');
    if (!container) return;

    // Sample Huffman tree data for demonstration
    const sampleData = {
        nodes: [
            { id: 'root', name: 'Root', value: 1.0, x: 400, y: 50 },
            { id: 'a', name: 'A', value: 0.4, x: 200, y: 150 },
            { id: 'b', name: 'B', value: 0.3, x: 600, y: 150 },
            { id: 'c', name: 'C', value: 0.2, x: 100, y: 250 },
            { id: 'd', name: 'D', value: 0.1, x: 300, y: 250 }
        ],
        links: [
            { source: 'root', target: 'a', code: '0' },
            { source: 'root', target: 'b', code: '1' },
            { source: 'a', target: 'c', code: '0' },
            { source: 'a', target: 'd', code: '1' }
        ]
    };

    // Create SVG visualization
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');
    svg.setAttribute('viewBox', '0 0 800 300');
    container.appendChild(svg);

    // Draw connections
    sampleData.links.forEach(link => {
        const sourceNode = sampleData.nodes.find(n => n.id === link.source);
        const targetNode = sampleData.nodes.find(n => n.id === link.target);
        
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', sourceNode.x);
        line.setAttribute('y1', sourceNode.y);
        line.setAttribute('x2', targetNode.x);
        line.setAttribute('y2', targetNode.y);
        line.setAttribute('stroke', '#38bdf8');
        line.setAttribute('stroke-width', '2');
        line.setAttribute('opacity', '0.7');
        svg.appendChild(line);

        // Add code labels
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        const midX = (sourceNode.x + targetNode.x) / 2;
        const midY = (sourceNode.y + targetNode.y) / 2;
        text.setAttribute('x', midX);
        text.setAttribute('y', midY - 5);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('fill', '#a855f7');
        text.setAttribute('font-size', '14');
        text.setAttribute('font-weight', 'bold');
        text.textContent = link.code;
        svg.appendChild(text);
    });

    // Draw nodes
    sampleData.nodes.forEach(node => {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', node.x);
        circle.setAttribute('cy', node.y);
        circle.setAttribute('r', node.id === 'root' ? 20 : 15);
        circle.setAttribute('fill', node.id === 'root' ? '#a855f7' : '#38bdf8');
        circle.setAttribute('opacity', '0.8');
        svg.appendChild(circle);

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', node.x);
        text.setAttribute('y', node.y + 5);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('fill', 'white');
        text.setAttribute('font-size', '12');
        text.setAttribute('font-weight', 'bold');
        text.textContent = node.name;
        svg.appendChild(text);

        // Add value labels for leaf nodes
        if (node.id !== 'root') {
            const valueText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            valueText.setAttribute('x', node.x);
            valueText.setAttribute('y', node.y + 25);
            valueText.setAttribute('text-anchor', 'middle');
            valueText.setAttribute('fill', '#9ca3af');
            valueText.setAttribute('font-size', '10');
            valueText.textContent = node.value.toFixed(1);
            svg.appendChild(valueText);
        }
    });

    // Animate the tree
    anime({
        targets: svg.querySelectorAll('circle'),
        scale: [0, 1],
        opacity: [0, 0.8],
        duration: 1000,
        delay: anime.stagger(200),
        easing: 'easeOutElastic(1, .8)'
    });

    anime({
        targets: svg.querySelectorAll('line'),
        strokeDashoffset: [100, 0],
        duration: 1500,
        delay: 500,
        easing: 'easeInOutQuad'
    });
}

// Particle background effect
function initParticleBackground() {
    const canvas = document.createElement('canvas');
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '-1';
    canvas.style.opacity = '0.3';
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    let particles = [];

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    function createParticles() {
        particles = [];
        const particleCount = Math.floor((canvas.width * canvas.height) / 15000);
        
        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 2 + 1,
                opacity: Math.random() * 0.5 + 0.2
            });
        }
    }

    function updateParticles() {
        particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;

            if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
            if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;
        });
    }

    function drawParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(56, 189, 248, ${particle.opacity})`;
            ctx.fill();
        });

        // Draw connections
        particles.forEach((particle, i) => {
            particles.slice(i + 1).forEach(otherParticle => {
                const dx = particle.x - otherParticle.x;
                const dy = particle.y - otherParticle.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 100) {
                    ctx.beginPath();
                    ctx.moveTo(particle.x, particle.y);
                    ctx.lineTo(otherParticle.x, otherParticle.y);
                    ctx.strokeStyle = `rgba(56, 189, 248, ${0.1 * (1 - distance / 100)})`;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            });
        });
    }

    function animate() {
        updateParticles();
        drawParticles();
        requestAnimationFrame(animate);
    }

    resizeCanvas();
    createParticles();
    animate();

    window.addEventListener('resize', () => {
        resizeCanvas();
        createParticles();
    });
}

// Smooth scrolling for navigation links
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Navigation scroll effect
window.addEventListener('scroll', () => {
    const nav = document.querySelector('nav');
    if (window.scrollY > 50) {
        nav.classList.add('shadow-lg');
    } else {
        nav.classList.remove('shadow-lg');
    }
});

// Button hover effects
document.querySelectorAll('.hover-lift').forEach(element => {
    element.addEventListener('mouseenter', () => {
        anime({
            targets: element,
            scale: 1.02,
            duration: 300,
            easing: 'easeOutCubic'
        });
    });

    element.addEventListener('mouseleave', () => {
        anime({
            targets: element,
            scale: 1,
            duration: 300,
            easing: 'easeOutCubic'
        });
    });
});

// Gradient text animation
function animateGradientText() {
    const gradientTexts = document.querySelectorAll('.gradient-text');
    
    gradientTexts.forEach(text => {
        anime({
            targets: text,
            backgroundPosition: ['0% 50%', '100% 50%'],
            duration: 3000,
            loop: true,
            direction: 'alternate',
            easing: 'easeInOutSine'
        });
    });
}

// Initialize gradient animation after page load
setTimeout(animateGradientText, 1000);