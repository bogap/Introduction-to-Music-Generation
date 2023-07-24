import pygame


def play():
    def play_midi(file_path):
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

    # Replace 'file1.mid' and 'file2.mid' with the paths to your MIDI files
    midi_file1 = 'verse_melody.mid'
    midi_file2 = 'verse.mid'
    midi_file3 = 'chorus.mid'

    # Play the first MIDI file
    play_midi(midi_file1)

    # Play the second MIDI file
    play_midi(midi_file2)
    play_midi(midi_file2)

    play_midi(midi_file3)

    play_midi(midi_file2)
    play_midi(midi_file2)

    play_midi(midi_file1)


