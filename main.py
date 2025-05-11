from js import document, console, window, THREE
from pyodide.ffi import create_proxy, to_js

# Global variables
scene = None
camera = None
renderer = None
player = None
obstacles = []
score = 0
current_level = 1
is_paused = True
keys_pressed = {}

# Game settings
PLAYER_SPEED = 0.1
OBSTACLE_COUNT = 5
OBSTACLE_SPEED = 0.02

def init_game():
    try:
        global scene, camera, renderer
        
        # Scene setup
        scene = THREE.Scene.new()
        scene.background = THREE.Color.new(0x000000)
        
        # Camera setup with perspective for better depth
        camera = THREE.PerspectiveCamera.new(75, window.innerWidth / window.innerHeight, 0.1, 1000)
        camera.position.z = 5
        
        # Renderer setup
        renderer = THREE.WebGLRenderer.new({"antialias": True})
        renderer.setSize(window.innerWidth, window.innerHeight)
        
        # Add renderer to DOM
        game_container = document.getElementById("game-container")
        game_container.appendChild(renderer.domElement)
        
        # Lighting
        ambient_light = THREE.AmbientLight.new(0xffffff, 0.5)
        scene.add(ambient_light)
        
        directional_light = THREE.DirectionalLight.new(0xffffff, 1)
        directional_light.position.set(5, 5, 5)
        scene.add(directional_light)
        
        # Create game objects
        create_player()
        create_obstacles()
        
        # Setup event listeners
        setup_controls()
        setup_game_buttons()
        
        # Start animation loop
        animate()
        
    except Exception as e:
        console.error("Error initializing game:", str(e))

def create_player():
    global player
    try:
        # Create player geometry
        geometry = THREE.BoxGeometry.new(0.5, 0.5, 0.5)
        material = THREE.MeshPhongMaterial.new({
            "color": 0x00ff88,
            "emissive": 0x00ff88,
            "emissiveIntensity": 0.5,
            "shininess": 100
        })
        
        player = THREE.Mesh.new(geometry, material)
        player.position.set(0, 0, 0)
        scene.add(player)
        
    except Exception as e:
        console.error("Error creating player:", str(e))

def create_obstacles():
    try:
        geometry = THREE.BoxGeometry.new(0.8, 0.8, 0.8)
        material = THREE.MeshPhongMaterial.new({
            "color": 0xff0044,
            "emissive": 0x330011,
            "transparent": True,
            "opacity": 0.8
        })
        
        for i in range(OBSTACLE_COUNT):
            obstacle = THREE.Mesh.new(geometry, material)
            reposition_obstacle(obstacle)
            obstacles.append(obstacle)
            scene.add(obstacle)
            
    except Exception as e:
        console.error("Error creating obstacles:", str(e))

def reposition_obstacle(obstacle):
    try:
        # Random position within bounds
        obstacle.position.x = (window.Math.random() * 8) - 4
        obstacle.position.y = (window.Math.random() * 6) - 3
        obstacle.position.z = 0
        
        # Set random velocity
        if not hasattr(obstacle, "velocity"):
            obstacle.velocity = {
                "x": (window.Math.random() - 0.5) * OBSTACLE_SPEED,
                "y": (window.Math.random() - 0.5) * OBSTACLE_SPEED
            }
            
    except Exception as e:
        console.error("Error repositioning obstacle:", str(e))

def update_obstacles():
    try:
        for obstacle in obstacles:
            # Update position
            obstacle.position.x += obstacle.velocity["x"]
            obstacle.position.y += obstacle.velocity["y"]
            
            # Bounce off boundaries
            if abs(obstacle.position.x) > 4:
                obstacle.velocity["x"] *= -1
            if abs(obstacle.position.y) > 3:
                obstacle.velocity["y"] *= -1
                
    except Exception as e:
        console.error("Error updating obstacles:", str(e))

def update_player():
    global score
    try:
        if not is_paused:
            # Update player position based on input
            if keys_pressed.get("ArrowUp") or keys_pressed.get("w"):
                player.position.y += PLAYER_SPEED
            if keys_pressed.get("ArrowDown") or keys_pressed.get("s"):
                player.position.y -= PLAYER_SPEED
            if keys_pressed.get("ArrowLeft") or keys_pressed.get("a"):
                player.position.x -= PLAYER_SPEED
            if keys_pressed.get("ArrowRight") or keys_pressed.get("d"):
                player.position.x += PLAYER_SPEED
                
            # Keep player within bounds
            player.position.x = max(-4, min(4, player.position.x))
            player.position.y = max(-3, min(3, player.position.y))
            
            # Update camera to follow player
            camera.position.x = player.position.x
            camera.position.y = player.position.y
            camera.position.z = 5  # Keep constant distance
            
            # Check for collisions and update score
            check_collisions()
            
    except Exception as e:
        console.error("Error updating player:", str(e))

def check_collisions():
    global score
    try:
        player_box = THREE.Box3.new()
        player_box.setFromObject(player)
        
        for obstacle in obstacles:
            obstacle_box = THREE.Box3.new()
            obstacle_box.setFromObject(obstacle)
            
            if player_box.intersectsBox(obstacle_box):
                handle_collision()
                break
                
    except Exception as e:
        console.error("Error checking collisions:", str(e))

def handle_collision():
    global score
    try:
        # Reset player position
        player.position.set(0, 0, 0)
        
        # Decrease score
        score = max(0, score - 5)
        update_score_display()
        
    except Exception as e:
        console.error("Error handling collision:", str(e))

def update_score_display():
    try:
        document.getElementById("current-score").textContent = str(score)
        document.getElementById("current-level").textContent = str(current_level)
        
    except Exception as e:
        console.error("Error updating score display:", str(e))

def setup_controls():
    try:
        def handle_keydown(event):
            keys_pressed[event.key] = True
            
        def handle_keyup(event):
            keys_pressed[event.key] = False
            
        # Keyboard controls
        document.addEventListener("keydown", create_proxy(handle_keydown))
        document.addEventListener("keyup", create_proxy(handle_keyup))
        
        # Mobile controls
        for control_id in ["move-left", "move-right", "move-up", "move-down"]:
            element = document.getElementById(control_id)
            if element:
                element.addEventListener("touchstart", 
                    create_proxy(lambda e, id=control_id: handle_mobile_control(e, id, True)))
                element.addEventListener("touchend", 
                    create_proxy(lambda e, id=control_id: handle_mobile_control(e, id, False)))
                
    except Exception as e:
        console.error("Error setting up controls:", str(e))

def setup_game_buttons():
    try:
        # Login button
        login_btn = document.getElementById("login-btn")
        if login_btn:
            login_btn.addEventListener("click", create_proxy(handle_login))

        # Game control buttons
        start_btn = document.getElementById("start-btn")
        pause_btn = document.getElementById("pause-btn")
        restart_btn = document.getElementById("restart-btn")
        settings_btn = document.getElementById("settings-btn")
        
        if start_btn:
            start_btn.addEventListener("click", create_proxy(handle_start))
        if pause_btn:
            pause_btn.addEventListener("click", create_proxy(handle_pause))
        if restart_btn:
            restart_btn.addEventListener("click", create_proxy(handle_restart))
        if settings_btn:
            settings_btn.addEventListener("click", create_proxy(handle_settings))
            
    except Exception as e:
        console.error("Error setting up game buttons:", str(e))

def handle_login(event):
    try:
        username = document.getElementById("username").value.strip()
        login_error = document.getElementById("login-error")
        
        if not username:
            login_error.textContent = "Please enter a username."
            return
            
        # Hide login modal
        login_modal = document.getElementById("login-modal")
        login_modal.style.display = "none"
        
        # Initialize game
        init_game()
        
    except Exception as e:
        console.error("Error handling login:", str(e))

def handle_start(event):
    global is_paused
    try:
        is_paused = False
        animate()
    except Exception as e:
        console.error("Error handling start:", str(e))

def handle_pause(event):
    global is_paused
    try:
        is_paused = True
    except Exception as e:
        console.error("Error handling pause:", str(e))

def handle_restart(event):
    global score, current_level, is_paused
    try:
        # Reset game state
        score = 0
        current_level = 1
        is_paused = False
        
        # Reset player position
        if player:
            player.position.set(0, 0, 0)
        
        # Reset camera
        if camera:
            camera.position.set(0, 0, 5)
        
        # Update display
        update_score_display()
        
        # Restart animation
        animate()
        
    except Exception as e:
        console.error("Error handling restart:", str(e))

def handle_settings(event):
    try:
        settings_modal = document.getElementById("settings-modal")
        settings_modal.style.display = "flex"
    except Exception as e:
        console.error("Error handling settings:", str(e))

def handle_mobile_control(event, control_id, is_active):
    try:
        if control_id == "move-left":
            keys_pressed["ArrowLeft"] = is_active
        elif control_id == "move-right":
            keys_pressed["ArrowRight"] = is_active
        elif control_id == "move-up":
            keys_pressed["ArrowUp"] = is_active
        elif control_id == "move-down":
            keys_pressed["ArrowDown"] = is_active
            
    except Exception as e:
        console.error("Error handling mobile control:", str(e))

def animate():
    try:
        if not is_paused:
            update_player()
            update_obstacles()
            renderer.render(scene, camera)
        
        window.requestAnimationFrame(create_proxy(animate))
        
    except Exception as e:
        console.error("Error in animation loop:", str(e))

# Initialize login when document is loaded
def on_load(event):
    try:
        # Setup login button
        login_btn = document.getElementById("login-btn")
        if login_btn:
            login_btn.addEventListener("click", create_proxy(handle_login))
    except Exception as e:
        console.error("Error in on_load:", str(e))

window.addEventListener("load", create_proxy(on_load))
