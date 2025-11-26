# This version depends on: fluidsynth

# Extended QWERTY piano for Arch Linux
# White keys (lower octave):  Z X C V B N M  -> C4 D4 E4 F4 G4 A4 B4
# Black keys (lower octave):  S D   G H J    -> C#4 D#4 F#4 G#4 A#4
#
# White keys (upper octave):  Q W E R T Y U I -> C5 D5 E5 F5 G5 A5 B5 C6
# Black keys (upper octave):  2 3   5 6 7     -> C#5 D#5 F#5 G#5 A#5
#
# Quit: ESC or close window
#
# Put UprightPianoKW-20220221.sf2 in the same folder (or edit SOUNDFONT).

import os
import sys
import pygame
import fluidsynth

SOUNDFONT = "UprightPianoKW-20220221.sf2"  # change path if needed
SAMPLE_RATE = 44100

# Try common Linux audio backends (PipeWire usually exposes PulseAudio)
AUDIO_DRIVERS = ["pulseaudio", "alsa", None]

# MIDI notes:
# C4 = 60, then chromatic up
#
# Lower row (white keys)
# Z=60(C4), X=62(D4), C=64(E4), V=65(F4), B=67(G4), N=69(A4), M=71(B4)
# Lower row (black keys)
# S=61(C#4), D=63(D#4), G=66(F#4), H=68(G#4), J=70(A#4)
#
# Upper row (white keys)
# Q=72(C5), W=74(D5), E=76(E5), R=77(F5), T=79(G5), Y=81(A5), U=83(B5), I=84(C6)
# Upper row (black keys)
# 2=73(C#5), 3=75(D#5), 5=78(F#5), 6=80(G#5), 7=82(A#5)

KEYMAP = {
    # Lower octave white
    pygame.K_z: 60,  # C4
    pygame.K_x: 62,  # D4
    pygame.K_c: 64,  # E4
    pygame.K_v: 65,  # F4
    pygame.K_b: 67,  # G4
    pygame.K_n: 69,  # A4
    pygame.K_m: 71,  # B4,

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

def init_synth():
    last_err = None
    for drv in AUDIO_DRIVERS:
        try:
            fs = fluidsynth.Synth(samplerate=SAMPLE_RATE)
            fs.start(driver=drv) if drv else fs.start()
            return fs
        except Exception as e:
            last_err = e
    print("Could not start FluidSynth. Last error:", last_err)
    sys.exit(1)

def main():
    if not os.path.exists(SOUNDFONT):
        print(f"SoundFont not found: {SOUNDFONT}")
        sys.exit(1)

    # Pygame window just for key events + small HUD
    pygame.init()
    pygame.display.set_caption("Qwerty Piano (VirtualPiano-style)")
    screen = pygame.display.set_mode((640, 180))
    font = pygame.font.SysFont(None, 22)

    fs = init_synth()
    sfid = fs.sfload(SOUNDFONT)
    fs.program_select(0, sfid, 0, 0)  # bank 0, program 0 (usually piano)
    
    fs.cc(0, 7, 127)     # controller 7 = channel volume
    fs.cc(0, 11, 127)    # controller 11 = expression (secondary volume)

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
                    fs.noteon(0, note, 127)
                    down.add(event.key)

            elif event.type == pygame.KEYUP:
                if event.key in KEYMAP and event.key in down:
                    note = KEYMAP[event.key]
                    fs.noteoff(0, note)
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

    # Clean up
    try:
        fs.cc(0, 123, 0)  # All Notes Off
    except Exception:
        pass
    fs.delete()
    pygame.quit()

if __name__ == "__main__":
    main()
