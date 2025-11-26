# Raspberry Pi QWERTY Piano box (Fluidsynth Binary)

This project turns a Raspberry Pi Zero 2W (or any compatible system) into a virtual piano by mapping QWERTY keyboard keys to MIDI notes. It uses a Python/Pygame application to capture key presses and controls an external Fluidsynth process to generate the actual piano sound.

## Project Overview

The core idea is to create a low-latency, software-based piano that can be played using a standard computer keyboard. Unlike solutions that use the pyfluidsynth library (which can be resource-heavy), this project communicates directly with the fluidsynth command-line binary as a subprocess, making it efficient for smaller devices like the Raspberry Pi Zero 2W.

## Installation and Setup

### 1. Requirements

- A keyboard connected to the device
- Operation system: linux
- (optional) Any Raspberry pi with audio output.

### 2. Install Dependencies

You need to install the `fluidsynth` sound synthesizer and the `pygame` Python library.

```bash
# Install fluidsynth and the necessary Python library
sudo apt update;
sudo apt install fluidsynth python3-pygame -y
```

### 3. Project Files

1. piano.py: Your provided Python script.

2. SoundFont: Download a SoundFont file (e.g., the specified UprightPianoKW-20220221.sf2) and place it in the same directory as piano.py.

    ⚠️ Note: The script is hardcoded to look for UprightPianoKW-20220221.sf2. If you use a different name, you must update the SOUNDFONT variable in piano.py.


## How it Works (The Process)

How It Works (The Process)

### 1. Initialization

1. Start fluidsynth: The start_fluidsynth() function in piano.py attempts to launch the fluidsynth binary as a subprocess.

    - It tries different audio drivers (pulseaudio, alsa) to ensure compatibility with the Pi's audio setup.
    - The command used is roughly: fluidsynth -a <driver> UprightPianoKW-20220221.sf2
    - It directs the output/errors of fluidsynth to /dev/null to keep the console clean.

2. Set Volume: Once started, the script sends MIDI Control Change (CC) commands via the subprocess's standard input (stdin) to set the channel volume (cc 0 7 127) and expression (cc 0 11 127) to maximum (127).

3. Start Pygame Loop: Pygame initializes and displays the key mapping guide.

### 2. Key Press Handling

1. Detect Keydown: Pygame captures a pygame.KEYDOWN event.

2. Map Key: The script checks if the key is in the KEYMAP dictionary (e.g., Z maps to 60 / C4).

3. Send noteon: A command is sent to the fluidsynth subprocess's stdin to start playing the note:

```noteon 0 <MIDI_Note> 127```

(e.g., noteon 0 60 127 plays C4 at max velocity 127 on channel 0).

4. Track Pressed Keys: The key is added to the down set to prevent repeated noteon commands while the key is held.

### 3. Key Release Handling

1. Detect Keyup: Pygame captures a pygame.KEYUP event.

2. Send noteoff: A command is sent to the fluidsynth subprocess's stdin to stop the note:

```noteoff 0 <MIDI_Note>```

(e.g., noteoff 0 60 stops C4).

3. Update Tracker: The key is removed from the down set.

### 4. Cleanup

When the user presses ESC or closes the window, the script sends the panic command to stop all currently playing notes, sends quit to the fluidsynth subprocess, and then uses fs_proc.terminate() to ensure the process fully exits.

## Usage

### 1. Clone and Navigate to the project directory in your terminal.

```bash
git clone https://github.com/jarbbie/qwerty_piano_box.git;
cd qwerty_piano_box
```

### 2. Install dependencies, and source Python venv

```bash
# Install os packages dependencies
bash os_packages_dependencies.sh;

# Initialize and Source python virtual environment
python3 -m venv .venv;
source ./.venv/bin/activate;

# Install dependencies
pip3 install -r requirements.txt;
```

### 3. Run the script

```bash
python3 piano.py
```