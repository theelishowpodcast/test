from ursina import *
import requests
from io import BytesIO
from PIL import Image
import random

# 1. Initialize Ursina Engine
app = Ursina()

# 2. Optimized Asset Loader
def get_3d_texture(url):
    try:
        response = requests.get(url, timeout=5)
        return Texture(Image.open(BytesIO(response.content)))
    except Exception as e:
        print(f"Texture error: {e}")
        return 'white_cube'

# Download car textures
player_tex = get_3d_texture("i.ibb.co")
ai_tex = get_3d_texture("i.ibb.co")

# 3. Mega-Environment Setup
# An extremely long road for the massive pack
road = Entity(model='cube', color=color.gray, scale=(20, 0.1, 10000), z=5000, texture='white_cube')
grass = Entity(model='plane', color=color.green, scale=(800, 1, 10000), z=5000, y=-0.2)
Sky() # Adds a horizon for 2025 visual standards

# 4. Player Car Class (with Camera and Performance Logic)
class PlayerCar(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='cube', 
            texture=player_tex, 
            scale=(1.6, 1.1, 2.7), 
            y=0.5, 
            collider='box',
            **kwargs
        )
        self.speed = 0
        self.max_speed = 60
        self.nitro_speed = 105

    def update(self):
        # Throttle & Nitro ('Z' Key)
        is_boosting = held_keys['z']
        target_max = self.nitro_speed if is_boosting else self.max_speed
        
        if held_keys['w'] or held_keys['up arrow']:
            self.speed = lerp(self.speed, target_max, time.dt * 2)
        elif held_keys['s'] or held_keys['down arrow']:
            self.speed = lerp(self.speed, 0, time.dt * 5)
        else:
            self.speed = lerp(self.speed, 0, time.dt * 0.4)

        # High-Speed Steering
        steer = (held_keys['d'] - held_keys['a']) + (held_keys['right arrow'] - held_keys['left arrow'])
        self.x += steer * time.dt * 18
        self.x = clamp(self.x, -8, 8) 

        # Forward Progress
        self.z += self.speed * time.dt

        # Dynamic Camera follow
        camera.position = self.position + Vec3(0, 8, -25)
        camera.look_at(self.position + Vec3(0, 2, 20))

# 5. AI Competitor Class (Optimized for Large Packs)
class AICar(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='cube', 
            texture=ai_tex, 
            scale=(1.6, 1.1, 2.7), 
            y=0.5, 
            collider='box',
            **kwargs
        )
        self.speed = random.uniform(40, 65)

    def update(self):
        # AI moves forward
        self.z += self.speed * time.dt
        
        # Performance/Endless Race Hack: 
        # If player passes AI by a large distance, move AI back to the front
        if player.z - self.z > 150:
            self.z = player.z + random.uniform(300, 500)
            self.x = random.uniform(-8, 8)
            self.speed = random.uniform(45, 70) # Give them a speed boost for the front line

# 6. Initialize the Massive Grid
player = PlayerCar(z=0)

# Spawning 50 AI players!
opponents = []
for i in range(50):
    # Scatter them across the initial 800 units of the road
    ai = AICar(z=random.uniform(50, 800), x=random.uniform(-7, 7))
    opponents.append(ai)

# 7. Collision Detection & Performance Logic
def update():
    # Detect hits
    hit_info = player.intersects()
    if hit_info.hit:
        player.speed *= 0.2 # Crash slow-down penalty
        # Provide visual feedback via the console
        print(f"CRASH! Speed reduced. Total players still racing: {len(opponents) + 1}")

# 8. Launch the Application
app.run()

