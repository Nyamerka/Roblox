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
PLATFORM_WIDTH = 2  # X-axis size
PLATFORM_LENGTH = 3  # Z-axis size
PLATFORM_SPACING = 4  # Space between platforms
INITIAL_PLATFORMS = 30

# Initialize
start_x, start_y, start_z = pos.x, pos.y + 50, pos.z
platforms = {}
checkpoint = None
score = 0
last_safe = None

# Create iron starting platform
mc.setBlocks(start_x - 1, start_y - 1, start_z,
             start_x + 1, start_y - 1, start_z + 2,
             block.IRON_BLOCK.id)
mc.player.setTilePos(start_x, start_y, start_z)


def create_platform(z_pos, is_fake):
    """Create straight platform at given Z position"""
    for dx in range(-1, 1):  # 2 blocks wide (X-axis)
        for dz in range(PLATFORM_LENGTH):
            x = start_x + dx
            z = z_pos + dz
            blk = FAKE_BLOCK if is_fake else SAFE_BLOCK
            mc.setBlock(x, start_y - 1, z, blk)
            platforms[(x, z)] = ('fake' if is_fake else 'safe', False)


def generate_bridge():
    """Generate straight platform sequence"""
    current_z = start_z + PLATFORM_LENGTH + PLATFORM_SPACING
    for _ in range(INITIAL_PLATFORMS):
        create_platform(current_z, random.choice([True, False]))
        current_z += PLATFORM_LENGTH + PLATFORM_SPACING


def update_checkpoint():
    global checkpoint
    if score % 3 == 0 and score > 0 and last_safe:
        x, z = last_safe
        for dx in range(-1, 1):
            for dz in range(PLATFORM_LENGTH):
                mc.setBlock(x + dx, start_y - 1, z + dz, CHECKPOINT_BLOCK[0], CHECKPOINT_BLOCK[1])
                platforms[(x + dx, z + dz)] = ('safe', True)
        checkpoint = (x, z)


# Game setup
mc.postToChat("Squid Game Bridge: Don't step on glass!")
mc.postToChat("Starting in 3 seconds...")
time.sleep(3)
generate_bridge()

while True:
    time.sleep(0.2)
    pos = mc.player.getTilePos()

    # Fall detection
    if pos.y < start_y - 2:
        if checkpoint:
            cx, cz = checkpoint
            mc.player.setTilePos(cx, start_y, cz + 1)
            mc.postToChat("Teleported to checkpoint!")
        else:
            mc.player.setTilePos(start_x, start_y, start_z)
            mc.postToChat(f"Game Over! Final score: {score}")
        score = 0
        checkpoint = None

    # Platform check
    block_pos = (pos.x, pos.z)
    if block_pos in platforms:
        ptype, is_check = platforms[block_pos]

        if ptype == 'fake' and not is_check:
            # Break fake platform
            for dx in range(-1, 1):
                for dz in range(PLATFORM_LENGTH):
                    x = pos.x + dx
                    z = pos.z - (pos.z % PLATFORM_LENGTH) + dz
                    if (x, z) in platforms:
                        mc.setBlock(x, start_y - 1, z, block.AIR.id)
                        del platforms[(x, z)]
            score = max(0, score - 1)
            mc.postToChat(f"Wrong! Score: {score}")

        elif ptype == 'safe' and not is_check:
            score += 1
            last_safe = (pos.x, pos.z - (pos.z % PLATFORM_LENGTH))
            update_checkpoint()
            mc.postToChat(f"+1! Score: {score}")