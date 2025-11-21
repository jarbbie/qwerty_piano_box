import os
import sys
import pygame
import subprocess

SOUNDFONT = "UprightPianoKW-20220221.sf2"

# If "fluidsynth Upright..." worked, set AUDIO_DRIVER = None
# If "fluidsynth -a alsa Upright..." worked, set AUDIO_DRIVER = "alsa"
AUDIO_DRIVER = "alsa"

KEYMAP = {
    pygame.K_z: 60, pygame.K_x: 62, pygame.K_c: 64, pygame.K_v: 65,
    pygame.K_b: 67, pygame.K_n: 69, pygame.K_m: 71,
    pygame.K_s: 61, pygame.K_d: 63, pygame.K_g: 66,
    pygame.K_h: 68, pygame.K_j: 70,
    pygame.K_q: 72, pygame.K_w: 74, pygame.K_e: 76, pygame.K_r: 77,
    pygame.K_t: 79, pygame.K_y: 81, pygame.K_u: 83, pygame.K_i: 84,
    pygame.K_2: 73, pygame.K_3: 75, pygame.K_5: 78,
    pygame.K_6: 80, pygame.K_7: 82,
}

def start_fluidsynth():
    if not os.path.exists(SOUNDFONT):
        print(f"SoundFont not found: {SOUNDFONT}")
        sys.exit(1)

    cmd = ["fluidsynth", "-i"]
    if AUDIO_DRIVER is not None:
        cmd += ["-a", AUDIO_DRIVER]
    cmd.append(SOUNDFONT)

    print("Starting fluidsynth:", " ".join(cmd))
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    return proc

def fs_cmd(proc, line: str):
    try:
        proc.stdin.write(line + "\n")
        proc.stdin.flush()
    except Exception as e:
        print("Error sending to fluidsynth:", e)

def main():
    pygame.init()
    pygame.display.set_caption("Qwerty Piano")
    screen = pygame.display.set_mode((640, 180))
    font = pygame.font.SysFont(None, 22)

    fs_proc = start_fluidsynth()
    fs_cmd(fs_proc, "cc 0 7 127")
    fs_cmd(fs_proc, "cc 0 11 127")

    down = set()
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in KEYMAP and event.key not in down:
                    note = KEYMAP[event.key]
                    fs_cmd(fs_proc, f"noteon 0 {note} 127")
                    down.add(event.key)
            elif event.type == pygame.KEYUP:
                if event.key in KEYMAP and event.key in down:
                    note = KEYMAP[event.key]
                    fs_cmd(fs_proc, f"noteoff 0 {note}")
                    down.remove(event.key)

        screen.fill((18, 18, 18))
        lines = [
            "Lower: Z X C V B N M / S D G H J",
            "Upper: Q W E R T Y U I / 2 3 5 6 7",
            f"SoundFont: {os.path.basename(SOUNDFONT)}   |   ESC to quit",
        ]
        y = 30
        for line in lines:
            screen.blit(font.render(line, True, (230, 230, 230)), (20, y))
            y += 25

        pygame.display.flip()
        clock.tick(120)

    fs_cmd(fs_proc, "panic")
    fs_cmd(fs_proc, "quit")
    pygame.quit()

if __name__ == "__main__":
    main()
