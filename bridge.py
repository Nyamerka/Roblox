import mcpi.minecraft as minecraft
import mcpi.block as block
import time
import random

mc = minecraft.Minecraft.create()
pos = mc.player.getTilePos()

# Constants
SAFE_BLOCK = block.WOOD_PLANKS.id
FAKE_BLOCK = block.GLASS.id
CHECKPOINT_BLOCK = block.WOOL.id, 13  # Green wool
PLATFORM_WIDTH = 2
PLATFORM_LENGTH = 3
PLATFORM_SPACING = 1
INITIAL_PLATFORMS = 30

# Initialize
start_x, start_y, start_z = pos.x, pos.y + 20, pos.z
platforms = {}
checkpoint = None
score = 0
processed_platforms = set()
checkpoint_data = {}

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
                'checkpoint': False,
                'original': block_type
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

def create_checkpoint(z_pos):
    global checkpoint, checkpoint_data
    checkpoint_data.clear()
    
    for side in [start_x-2, start_x+1]:
        for dx in range(PLATFORM_WIDTH):
            for dz in range(PLATFORM_LENGTH):
                x = side + dx
                z = z_pos + dz
                checkpoint_data[(x, z)] = mc.getBlock(x, start_y-1, z)
                mc.setBlock(x, start_y-1, z, CHECKPOINT_BLOCK[0], CHECKPOINT_BLOCK[1])
                platforms[(x, z)]['checkpoint'] = True
                
    checkpoint = z_pos

def restore_checkpoint():
    for (x, z), block_id in checkpoint_data.items():
        mc.setBlock(x, start_y-1, z, block_id)
        platforms[(x, z)]['checkpoint'] = False
    checkpoint_data.clear()

# Game setup
mc.postToChat("Squid Game Bridge: Jump carefully!")
time.sleep(3)
generate_bridge()

while True:
    time.sleep(0.1)
    pos = mc.player.getTilePos()
    
    # Fall detection
    if pos.y < start_y - 2:
        if checkpoint:
            restore_checkpoint()
            mc.player.setTilePos(start_x, start_y, checkpoint + 1)
            mc.postToChat("Teleported to checkpoint!")
            checkpoint = None
        else:
            mc.player.setTilePos(start_x, start_y, start_z + 1)
            mc.postToChat(f"Game Over! Score: {score}")
        score = 0
        processed_platforms.clear()
    
    # Platform processing
    current_platform_z = (pos.z // (PLATFORM_LENGTH + PLATFORM_SPACING)) * (PLATFORM_LENGTH + PLATFORM_SPACING)
    
    if current_platform_z not in processed_platforms and current_platform_z > start_z:
        safe_found = False
        # Check both platforms at this Z level
        for side in [start_x-2, start_x+1]:
            platform_type = None
            for dz in range(PLATFORM_LENGTH):
                if (side, current_platform_z + dz) in platforms:
                    platform_type = platforms[(side, current_platform_z + dz)]['type']
                    break
            
            if platform_type == 'safe':
                safe_found = True
                score += 1
                mc.postToChat(f"Correct! Score: {score}")
                processed_platforms.add(current_platform_z)
                
                if score % 3 == 0:
                    create_checkpoint(current_platform_z)
                break
        
        if not safe_found:
            score = max(0, score-1)
            mc.postToChat(f"Wrong! Score: {score}")
            processed_platforms.add(current_platform_z)
    
    # Generate new platforms
    if current_platform_z > start_z + (INITIAL_PLATFORMS - 10) * (PLATFORM_LENGTH + PLATFORM_SPACING):
        generate_platform_pair(current_platform_z + (PLATFORM_LENGTH + PLATFORM_SPACING))
