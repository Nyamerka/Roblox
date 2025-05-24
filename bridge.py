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
PLATFORM_WIDTH = 2    # X-axis size
PLATFORM_LENGTH = 3   # Z-axis size
PLATFORM_SPACING = 1  # Space between platforms
INITIAL_PLATFORMS = 30

# Initialize
start_x, start_y, start_z = pos.x, pos.y + 20, pos.z
platforms = {}
checkpoint = None
score = 0
last_safe_z = start_z

# Create iron starting platform (3x2)
mc.setBlocks(start_x - 1, start_y-1, start_z,
             start_x + 1, start_y-1, start_z + 2,
             block.IRON_BLOCK.id)
mc.player.setTilePos(start_x, start_y, start_z + 1)

def create_platform(base_z, is_left, is_fake):
    """Create 2x3 platform at specified position"""
    block_type = FAKE_BLOCK if is_fake else SAFE_BLOCK
    x_start = start_x - 2 if is_left else start_x + 1
    for dx in range(PLATFORM_WIDTH):
        for dz in range(PLATFORM_LENGTH):
            x = x_start + dx
            z = base_z + dz
            mc.setBlock(x, start_y-1, z, block_type)
            platforms[(x,z)] = ('fake' if is_fake else 'safe', False)

def generate_platform_pair(z_pos):
    """Generate two platforms (left and right)"""
    # Randomly choose which side is safe
    left_is_fake = random.choice([True, False])
    right_is_fake = not left_is_fake
    
    # Create platforms
    create_platform(z_pos, is_left=True, is_fake=left_is_fake)
    create_platform(z_pos, is_left=False, is_fake=right_is_fake)

def generate_bridge():
    """Generate initial platform sequence"""
    current_z = start_z + PLATFORM_LENGTH
    for _ in range(INITIAL_PLATFORMS):
        generate_platform_pair(current_z)
        current_z += PLATFORM_LENGTH + PLATFORM_SPACING

def update_checkpoint(z_pos):
    global checkpoint
    # Convert last safe platform to checkpoint
    for x in [start_x-2, start_x+1]:
        for dx in range(PLATFORM_WIDTH):
            for dz in range(PLATFORM_LENGTH):
                mc.setBlock(x+dx, start_y-1, z_pos+dz, CHECKPOINT_BLOCK[0], CHECKPOINT_BLOCK[1])
                platforms[(x+dx, z_pos+dz)] = ('safe', True)
    checkpoint = z_pos

# Game setup
mc.postToChat("Squid Game Bridge: Jump carefully!")
mc.postToChat("Starting in 3 seconds...")
time.sleep(3)
generate_bridge()

while True:
    time.sleep(0.1)
    pos = mc.player.getTilePos()
    
    # Fall detection
    if pos.y < start_y - 2:
        if checkpoint:
            mc.player.setTilePos(start_x, start_y, checkpoint + 1)
            mc.postToChat("Teleported to checkpoint!")
        else:
            mc.player.setTilePos(start_x, start_y, start_z + 1)
            mc.postToChat(f"Game Over! Score: {score}")
        score = 0
    
    # Platform check
    on_platform = any((pos.x + dx, pos.z + dz) in platforms
                   for dx in [-1,0,1] for dz in [-1,0,1])
    
    if on_platform:
        # Find exact platform block
        for dz in range(-PLATFORM_LENGTH, PLATFORM_LENGTH):
            for dx in range(-PLATFORM_WIDTH, PLATFORM_WIDTH):
                block_pos = (pos.x + dx, pos.z + dz)
                if block_pos in platforms:
                    ptype, is_check = platforms[block_pos]
                    
                    if ptype == 'fake':
                        # Destroy entire platform
                        platform_z = block_pos[1] - dz
                        for x in [start_x-2, start_x+1]:
                            for px in range(PLATFORM_WIDTH):
                                for pz in range(PLATFORM_LENGTH):
                                    coord = (x + px, platform_z + pz)
                                    if coord in platforms:
                                        mc.setBlock(coord[0], start_y-1, coord[1], block.AIR.id)
                                        del platforms[coord]
                        score = max(0, score-1)
                        mc.postToChat(f"Wrong! Score: {score}")
                    
                    else:
                        score += 1
                        last_safe_z = block_pos[1] - dz
                        if score % 3 == 0:
                            update_checkpoint(last_safe_z)
                        mc.postToChat(f"Correct! Score: {score}")
                    
                    # Generate new platforms
                    if block_pos[1] > start_z + INITIAL_PLATFORMS * (PLATFORM_LENGTH + PLATFORM_SPACING) - 10:
                        generate_platform_pair(block_pos[1] + PLATFORM_LENGTH + PLATFORM_SPACING)
                    break
