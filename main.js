// Game state
let scene, camera, renderer, composer;
let player, hearts = [], obstacles = [];
let score = 0, bestScore = 0;
let isGameActive = false;
let jumpForce = 0;
const GRAVITY = 0.005;
const JUMP_POWER = 0.3;
const FLOAT_POWER = 0.1;

// Initialize Three.js scene
function init() {
    // Scene setup
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('game-container').appendChild(renderer.domElement);

    // Post-processing for bloom effect
    const renderScene = new THREE.RenderPass(scene, camera);
    composer = new THREE.EffectComposer(renderer);
    composer.addPass(renderScene);

    const bloomPass = new THREE.UnrealBloomPass(
        new THREE.Vector2(window.innerWidth, window.innerHeight),
        1.5, // strength
        0.4, // radius
        0.85 // threshold
    );
    composer.addPass(bloomPass);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(0, 10, 10);
    scene.add(directionalLight);

    // Create player (glowing orb)
    createPlayer();

    // Set camera position
    camera.position.z = 5;

    // Event listeners
    window.addEventListener('resize', onWindowResize, false);
    document.addEventListener('keydown', onKeyDown);
    document.addEventListener('keyup', onKeyUp);
    document.addEventListener('touchstart', onTouchStart);
    document.addEventListener('touchend', onTouchEnd);

    // UI event listeners
    document.getElementById('start-btn').addEventListener('click', startGame);
    document.getElementById('restart-btn').addEventListener('click', restartGame);
}

function createPlayer() {
    const geometry = new THREE.SphereGeometry(0.2, 32, 32);
    const material = new THREE.MeshPhongMaterial({
        color: 0xff69b4,
        emissive: 0xff1493,
        emissiveIntensity: 0.5,
        shininess: 100
    });
    player = new THREE.Mesh(geometry, material);
    player.position.set(0, 0, 0);
    scene.add(player);
}

function createHeart() {
    const heartShape = new THREE.Shape();
    // Heart shape path
    heartShape.moveTo(0, 0);
    heartShape.bezierCurveTo(-0.1, 0.1, -0.2, 0, -0.1, -0.1);
    heartShape.bezierCurveTo(0, -0.2, 0.1, -0.1, 0.1, 0);
    heartShape.bezierCurveTo(0.2, 0, 0.1, 0.1, 0, 0);

    const geometry = new THREE.ShapeGeometry(heartShape);
    const material = new THREE.MeshPhongMaterial({
        color: 0xff69b4,
        emissive: 0xff1493,
        side: THREE.DoubleSide
    });
    const heart = new THREE.Mesh(geometry, material);
    heart.position.x = Math.random() * 10 - 5;
    heart.position.y = Math.random() * 6 - 3;
    heart.position.z = -10;
    scene.add(heart);
    hearts.push(heart);
}

function createObstacle() {
    const geometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
    const material = new THREE.MeshPhongMaterial({
        color: 0x333333,
        emissive: 0x000000
    });
    const obstacle = new THREE.Mesh(geometry, material);
    obstacle.position.x = Math.random() * 10 - 5;
    obstacle.position.y = Math.random() * 6 - 3;
    obstacle.position.z = -10;
    scene.add(obstacle);
    obstacles.push(obstacle);
}

function updateGame() {
    if (!isGameActive) return;

    // Apply gravity and jump force
    jumpForce -= GRAVITY;
    player.position.y += jumpForce;

    // Keep player in bounds
    if (player.position.y < -3) {
        player.position.y = -3;
        jumpForce = 0;
    }
    if (player.position.y > 3) {
        player.position.y = 3;
        jumpForce = 0;
    }

    // Move and check hearts
    hearts.forEach((heart, index) => {
        heart.position.z += 0.1;
        heart.rotation.z += 0.02;

        // Check collision with player
        if (heart.position.distanceTo(player.position) < 0.5) {
            collectHeart(index);
        }

        // Remove if passed camera
        if (heart.position.z > 5) {
            scene.remove(heart);
            hearts.splice(index, 1);
        }
    });

    // Move and check obstacles
    obstacles.forEach((obstacle, index) => {
        obstacle.position.z += 0.1;
        obstacle.rotation.x += 0.02;
        obstacle.rotation.y += 0.02;

        // Check collision with player
        if (obstacle.position.distanceTo(player.position) < 0.5) {
            gameOver();
        }

        // Remove if passed camera
        if (obstacle.position.z > 5) {
            scene.remove(obstacle);
            obstacles.splice(index, 1);
        }
    });

    // Spawn new hearts and obstacles
    if (Math.random() < 0.02) createHeart();
    if (Math.random() < 0.01) createObstacle();

    // Update score display
    document.getElementById('hearts-collected').textContent = score;
}

function collectHeart(index) {
    scene.remove(hearts[index]);
    hearts.splice(index, 1);
    score++;
    
    // Play collect sound
    document.getElementById('collect-sound').play();

    // Check for secret message reveal
    if (score > bestScore) {
        bestScore = score;
        document.getElementById('best-score').textContent = bestScore;
        if (score >= 10) {
            revealSecretMessage();
        }
    }
}

function revealSecretMessage() {
    const message = document.getElementById('secret-message');
    message.classList.remove('hidden');
    message.innerHTML = `
        <p class="love-message">💌 I love you more than all the stars in the sky...</p>
    `;
}

function startGame() {
    isGameActive = true;
    score = 0;
    document.getElementById('start-screen').classList.add('hidden');
    document.getElementById('game-hud').classList.remove('hidden');
    document.getElementById('background-music').play();
}

function gameOver() {
    isGameActive = false;
    document.getElementById('game-over-screen').classList.remove('hidden');
    document.getElementById('final-score').textContent = score;
    document.getElementById('background-music').pause();
}

function restartGame() {
    // Clear hearts and obstacles
    hearts.forEach(heart => scene.remove(heart));
    obstacles.forEach(obstacle => scene.remove(obstacle));
    hearts = [];
    obstacles = [];

    // Reset player position
    player.position.set(0, 0, 0);
    jumpForce = 0;

    // Hide game over screen
    document.getElementById('game-over-screen').classList.add('hidden');
    document.getElementById('game-hud').classList.remove('hidden');

    // Start game
    isGameActive = true;
    score = 0;
    document.getElementById('background-music').play();
}

function onKeyDown(event) {
    if (event.code === 'Space' && isGameActive) {
        jumpForce = JUMP_POWER;
    }
}

function onKeyUp(event) {
    if (event.code === 'Space' && isGameActive) {
        if (jumpForce > 0) jumpForce = FLOAT_POWER;
    }
}

function onTouchStart() {
    if (isGameActive) {
        jumpForce = JUMP_POWER;
    }
}

function onTouchEnd() {
    if (isGameActive && jumpForce > 0) {
        jumpForce = FLOAT_POWER;
    }
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    composer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
    requestAnimationFrame(animate);
    updateGame();
    composer.render();
}

// Start the game
init();
animate();
