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
PLATFORM_DISTANCE = 1  # Space between platforms along Z-axis
INITIAL_PLATFORMS = 30

# Initialize
start_x, start_y, start_z = pos.x, pos.y + 20, pos.z
platforms = {}
checkpoint = None
score = 0
last_safe_z = start_z

# Create iron starting platform
mc.setBlocks(start_x - 1, start_y - 1, start_z,
             start_x + 1, start_y - 1, start_z + 1,
             block.IRON_BLOCK.id)
mc.player.setTilePos(start_x, start_y, start_z)


def generate_platform_pair(z_pos):
    """Generate two platforms at given Z position (left and right)"""
    # Left platform (X-2)
    left_fake = random.choice([True, False])
    right_fake = not left_fake  # Ensure one is safe

    # Left platform
    mc.setBlocks(start_x - 2, start_y - 1, z_pos,
                 start_x - 2, start_y - 1, z_pos,
                 FAKE_BLOCK if left_fake else SAFE_BLOCK)
    platforms[(start_x - 2, z_pos)] = ('fake' if left_fake else 'safe', False)

    # Right platform (X+2)
    mc.setBlocks(start_x + 2, start_y - 1, z_pos,
                 start_x + 2, start_y - 1, z_pos,
                 FAKE_BLOCK if right_fake else SAFE_BLOCK)
    platforms[(start_x + 2, z_pos)] = ('fake' if right_fake else 'safe', False)


def generate_bridge():
    """Generate platform pairs"""
    current_z = start_z + 1
    for _ in range(INITIAL_PLATFORMS):
        generate_platform_pair(current_z)
        current_z += PLATFORM_DISTANCE


def update_checkpoint(z_pos):
    global checkpoint
    # Replace last safe platform with checkpoint
    mc.setBlock(start_x - 2, start_y - 1, z_pos, CHECKPOINT_BLOCK[0], CHECKPOINT_BLOCK[1])
    mc.setBlock(start_x + 2, start_y - 1, z_pos, CHECKPOINT_BLOCK[0], CHECKPOINT_BLOCK[1])
    checkpoint = z_pos


# Game setup
mc.postToChat("Squid Game Bridge: Choose the right platform!")
mc.postToChat("Starting in 3 seconds...")
time.sleep(3)
generate_bridge()

while True:
    time.sleep(0.1)
    pos = mc.player.getTilePos()

    # Fall detection
    if pos.y < start_y - 2:
        if checkpoint:
            mc.player.setTilePos(start_x, start_y, checkpoint)
            mc.postToChat("Teleported to checkpoint!")
        else:
            mc.player.setTilePos(start_x, start_y, start_z)
            mc.postToChat(f"Game Over! Score: {score}")
        score = 0

    # Platform check
    current_z = pos.z
    if (pos.x, current_z) in platforms:
        ptype, is_check = platforms[(pos.x, current_z)]

        if ptype == 'fake':
            # Break platform and deduct score
            mc.setBlock(pos.x, start_y - 1, current_z, block.AIR.id)
            score = max(0, score - 1)
            mc.postToChat(f"Wrong! Score: {score}")
        else:
            score += 1
            last_safe_z = current_z
            if score % 3 == 0:
                update_checkpoint(current_z)
            mc.postToChat(f"Correct! Score: {score}")

        # Generate new platforms ahead
        if current_z > start_z + INITIAL_PLATFORMS - 5:
            generate_platform_pair(current_z + PLATFORM_DISTANCE)
