from mido import Message, MidiFile, MidiTrack
from music21 import converter
from genetic_algo import *

num = 2

MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]

# indexes of scales where minor/major chords
MINORS_IN_MAJOR_SCALE = [1, 2, 5]
MINORS_IN_MINOR_SCALE = [0, 3, 4]
MAJORS_IN_MAJOR_SCALE = [0, 3, 4, 6]
MAJORS_IN_MINOR_SCALE = [1, 2, 5, 6]

CHORDS = {0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'}
POSSIBLE_CHORDS = []
for i in range(24, 96):
    POSSIBLE_CHORDS.append((i, define_chord(i, CHORDS), [i, i + 4, i + 7]))
    POSSIBLE_CHORDS.append((i, define_chord(i, CHORDS) + 'm', [i, i + 3, i + 7]))


def melody_time(melody):
    """
    Calculates the duration of a generated melody.

    Args:
        melody (MidiFile): The MIDI file containing the melody.

    Returns:
        float: The duration of the melody.
    """
    time = 0
    for note in melody.tracks[0]:
        if note.type == 'note_on' or note.type == 'note_off':
            time += note.time
    return time


class Accompaniment:
    """
    Class representing the accompaniment generation process.
    """

    def __init__(self, midi_file, parts):
        """
        Initializes the Accompaniment object.

        Args:
            midi_file (str): The MIDI file name.
            parts (int): The number of parts to generate in the accompaniment.
        """
        self.midi_file = midi_file
        self.melody = MidiFile(midi_file, clip=True)
        self.melody_notes = []
        for note in self.melody.tracks[0]:
            if note.type == 'note_on':
                self.melody_notes.append(note.note)

        self.accompaniment = MidiFile()
        track = MidiTrack()
        self.accompaniment.tracks.append(track)

        time = melody_time(self.melody)
        self.parts = parts
        self.unit_time = self.melody.ticks_per_beat * num
        #self.unit_time = 512

    def detect_key(self, midi):
        """
        Detects the key of a MIDI file.

        Args:
            midi (str): The MIDI file name.

        Returns:
            str: The detected key of the MIDI file.
        """
        midi_stream = converter.parse(midi)
        key_analysis = midi_stream.analyze("key")
        print(key_analysis.tonicPitchNameWithCase)
        return key_analysis.tonicPitchNameWithCase

    def define_good_chords(self, midi_file):
        """
        Defines the good chords based on the detected key of the MIDI file.

        Args:
            midi_file (str): The MIDI file name.

        Returns:
            list: The list of chords considered good.
        """
        detected_key = self.detect_key(midi_file)

        key = detected_key.upper()
        note_key = define_note(key, CHORDS)
        maj_keys = []
        min_keys = []

        if detected_key[0].islower():
            keys = [(note + note_key) % 12 for note in MINOR_SCALE]
            for i in MAJORS_IN_MINOR_SCALE:
                maj_keys.append(keys[i])
            for i in MINORS_IN_MINOR_SCALE:
                min_keys.append(keys[i])
        else:
            keys = [(note + note_key) % 12 for note in MAJOR_SCALE]
            for i in MAJORS_IN_MAJOR_SCALE:
                maj_keys.append(keys[i])
            for i in MINORS_IN_MAJOR_SCALE:
                min_keys.append(keys[i])

        good_chords = []

        for chord in POSSIBLE_CHORDS:
            if chord[0] % 12 in maj_keys:
                if not ('m' in chord[1]):
                    good_chords.append(chord)
            if chord[0] % 12 in min_keys:
                if 'm' in chord[1]:
                    good_chords.append(chord)

        return good_chords

    def create_midi(self, chord_progression):
        """
        Creates a MIDI file from the chord progression.

        Args:
            chord_progression (list): The chord progression represented by a list of MIDI notes.

        Returns:
            None
        """
        for i in range(len(chord_progression)):
            chord = chord_progression[i][2]
            self.accompaniment.tracks[0].append(Message('note_on', channel=0, note=chord[0], velocity=100, time=0))
            self.accompaniment.tracks[0].append(Message('note_on', channel=0, note=chord[1], velocity=100, time=0))
            self.accompaniment.tracks[0].append(Message('note_on', channel=0, note=chord[2], velocity=100, time=0))
            self.accompaniment.tracks[0].append(Message('note_off', channel=0, note=chord[0], velocity=0,
                                                        time=self.unit_time))
            self.accompaniment.tracks[0].append(Message('note_off', channel=0, note=chord[1], velocity=0, time=0))
            self.accompaniment.tracks[0].append(Message('note_off', channel=0, note=chord[2], velocity=0, time=0))
            # self.accompaniment.tracks[0].append(
            #     Message('note_on', channel=0, note=chord[0], velocity=80, time=0))
            # self.accompaniment.tracks[0].append(
            #     Message('note_off', channel=0, note=chord[0], velocity=80, time=self.unit_time))
            # self.accompaniment.tracks[0].append(
            #     Message('note_on', channel=0, note=chord[1], velocity=80, time=0))
            # self.accompaniment.tracks[0].append(
            #     Message('note_off', channel=0, note=chord[1], velocity=80, time=self.unit_time))
            # self.accompaniment.tracks[0].append(
            #     Message('note_on', channel=0, note=chord[2], velocity=80, time=0))
            # self.accompaniment.tracks[0].append(
            #     Message('note_off', channel=0, note=chord[2], velocity=80, time=self.unit_time))

        self.melody.tracks.append(self.accompaniment.tracks[0])
        self.melody.save('verse.mid')

    def generate_accomp(self):
        """
        Generates the accompaniment using the Genetic Algorithm.

        Returns:
            None
        """
        good_chords = self.define_good_chords(self.midi_file)
        print(good_chords)
        GA = GeneticAlgo(self.midi_file)
        best_chord_progression = GA.genetic_algorithm(good_chords)
        self.create_midi(best_chord_progression)
