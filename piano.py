# fluidsynth-free version

# QWERTY piano using external fluidsynth process (no pyfluidsynth)
# Needs: python3-pygame, fluidsynth (apt install)

import os
import sys
import pygame
import subprocess

SOUNDFONT = "UprightPianoKW-20220221.sf2"  # put this file next to piano.py
AUDIO_DRIVERS = ["pulseaudio", "alsa", None]  # try these for fluidsynth

# MIDI note mapping (same as before)
KEYMAP = {
    # Lower octave white
    pygame.K_z: 60,  # C4
    pygame.K_x: 62,  # D4
    pygame.K_c: 64,  # E4
    pygame.K_v: 65,  # F4
    pygame.K_b: 67,  # G4
    pygame.K_n: 69,  # A4
    pygame.K_m: 71,  # B4

    # Lower octave black
    pygame.K_s: 61,  # C#4
    pygame.K_d: 63,  # D#4
    pygame.K_g: 66,  # F#4
    pygame.K_h: 68,  # G#4
    pygame.K_j: 70,  # A#4

    # Upper octave white
    pygame.K_q: 72,  # C5
    pygame.K_w: 74,  # D5
    pygame.K_e: 76,  # E5
    pygame.K_r: 77,  # F5
    pygame.K_t: 79,  # G5
    pygame.K_y: 81,  # A5
    pygame.K_u: 83,  # B5
    pygame.K_i: 84,  # C6

    # Upper octave black
    pygame.K_2: 73,  # C#5
    pygame.K_3: 75,  # D#5
    pygame.K_5: 78,  # F#5
    pygame.K_6: 80,  # G#5
    pygame.K_7: 82,  # A#5
}


def start_fluidsynth():
    """Start fluidsynth as a subprocess and return the process object."""
    if not os.path.exists(SOUNDFONT):
        print(f"SoundFont not found: {SOUNDFONT}")
        sys.exit(1)

    last_err = None
    for drv in AUDIO_DRIVERS:
        try:
            cmd = ["fluidsynth"]  # -i = no interactive prompt
            if drv:
                cmd += ["-a", drv]       # set audio driver
            cmd.append(SOUNDFONT)

            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
            )
            return proc
        except Exception as e:
            last_err = e

    print("Could not start fluidsynth. Last error:", last_err)
    sys.exit(1)


def fs_cmd(proc, line: str):
    """Send a single command line to fluidsynth."""
    try:
        proc.stdin.write(line + "\n")
        proc.stdin.flush()
    except Exception:
        pass


def main():
    pygame.init()
    pygame.display.set_caption("Qwerty Piano (fluidsynth binary)")
    screen = pygame.display.set_mode((640, 180))
    font = pygame.font.SysFont(None, 22)

    fs_proc = start_fluidsynth()

    # optional: max volume
    fs_cmd(fs_proc, "cc 0 7 127")    # channel volume
    fs_cmd(fs_proc, "cc 0 11 127")   # expression

    down = set()
    running = True
    clock = pygame.time.Clock()

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
            "Lower white: Z X C V B N M   -> C4..B4",
            "Lower black:   S D   G H J   -> C#4..A#4",
            "Upper white: Q W E R T Y U I -> C5..C6",
            "Upper black: 2 3   5 6 7     -> C#5..A#5",
            f"SoundFont: {os.path.basename(SOUNDFONT)}   |   ESC to quit",
        ]
        y = 20
        for line in lines:
            screen.blit(font.render(line, True, (230, 230, 230)), (12, y))
            y += 24

        pygame.display.flip()
        clock.tick(120)

    # stop all notes & quit fluidsynth
    fs_cmd(fs_proc, "panic")
    fs_cmd(fs_proc, "quit")
    try:
        fs_proc.terminate()
    except Exception:
        pass

    pygame.quit()


if __name__ == "__main__":
    main()
