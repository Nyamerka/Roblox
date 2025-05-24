import mcpi.minecraft as minecraft
import mcpi.block as block
import time
import random

mc = minecraft.Minecraft.create()
pos = mc.player.getTilePos()

# Constants
SAFE_BLOCK = block.WOOD_PLANKS.id
FAKE_BLOCK = block.GLASS.id
PLATFORM_WIDTH = 2
PLATFORM_LENGTH = 3
PLATFORM_SPACING = 1
INITIAL_PLATFORMS = 30

# Initialize
start_x, start_y, start_z = pos.x, pos.y + 20, pos.z
platforms = {}
score = 0
processed_platforms = set()

# Create iron starting platform
mc.setBlocks(start_x - 1, start_y-1, start_z,
             start_x + 1, start_y-1, start_z + 2,
             block.IRON_BLOCK.id)
mc.player.setTilePos(start_x, start_y, start_z + 1)

def create_platform(base_z, is_left, is_fake):
    x_start = start_x - 2 if is_left else start_x + 1
    block_type = FAKE_BLOCK if is_fake else SAFE_BLOCK
    for dx in range(PLATFORM_WIDTH):
        for dz in range(PLATFORM_LENGTH):
            x = x_start + dx
            z = base_z + dz
            mc.setBlock(x, start_y-1, z, block_type)
            platforms[(x, z)] = {
                'type': 'fake' if is_fake else 'safe',
                'base_z': base_z,
                'side': 'left' if is_left else 'right'
            }

def generate_platform_pair(z_pos):
    left_is_fake = random.choice([True, False])
    right_is_fake = not left_is_fake
    create_platform(z_pos, True, left_is_fake)
    create_platform(z_pos, False, right_is_fake)

def generate_bridge():
    current_z = start_z + PLATFORM_LENGTH
    for _ in range(INITIAL_PLATFORMS):
        generate_platform_pair(current_z)
        current_z += PLATFORM_LENGTH + PLATFORM_SPACING

# Game setup
mc.postToChat("Squid Game Bridge: Jump carefully!")
time.sleep(3)
generate_bridge()

while True:
    time.sleep(0.1)
    pos = mc.player.getTilePos()
    
    # Fall detection
    if pos.y < start_y - 2:
        mc.player.setTilePos(start_x, start_y, start_z + 1)
        mc.postToChat(f"Game Over! Score: {score}")
        score = 0
        processed_platforms.clear()
    
    # Platform processing
    current_platform_z = pos.z - (pos.z % (PLATFORM_LENGTH + PLATFORM_SPACING))
    
    if current_platform_z not in processed_platforms and current_platform_z > start_z:
        # Detect current platform side
        if start_x - 2 <= pos.x <= start_x - 1:
            side = 'left'
        elif start_x + 1 <= pos.x <= start_x + 2:
            side = 'right'
        else:
            continue

        # Get platform type
        platform_type = None
        for dz in range(PLATFORM_LENGTH):
            if (pos.x, current_platform_z + dz) in platforms:
                platform_type = platforms[(pos.x, current_platform_z + dz)]['type']
                break

        if platform_type == 'safe':
            score += 1
            mc.postToChat(f"Correct! Score: {score}")
            processed_platforms.add(current_platform_z)
        else:
            # Destroy fake platform
            x_start = start_x - 2 if side == 'left' else start_x + 1
            for dx in range(PLATFORM_WIDTH):
                for dz in range(PLATFORM_LENGTH):
                    x = x_start + dx
                    z = current_platform_z + dz
                    if (x, z) in platforms:
                        mc.setBlock(x, start_y-1, z, block.AIR.id)
                        del platforms[(x, z)]
            score = max(0, score-1)
            mc.postToChat(f"Wrong! Score: {score}")
            processed_platforms.add(current_platform_z)
    
    # Generate new platforms
    if current_platform_z > start_z + (INITIAL_PLATFORMS - 10) * (PLATFORM_LENGTH + PLATFORM_SPACING):
        generate_platform_pair(current_platform_z + (PLATFORM_LENGTH + PLATFORM_SPACING))
