import random
import numpy as np
from midiutil.MidiFile import MIDIFile
import mido
from music21 import converter, note
import music21
import matplotlib.pyplot as plt


def generate_chorus(orig):
    filename = orig
    initial_melody = []
    midi_file = converter.parse(filename)
    random_key = music21.note.Note(midi_file.analyze('key').tonic.name).pitch.midi
    random_key2 = midi_file.analyze('key').mode

    print(random_key2)
    mid = mido.MidiFile(filename)
    for i, track in enumerate(mid.tracks):
        for msg in track:
            if msg.type == 'note_on':
                note = msg.note
                initial_melody += [note + 12]
    print(initial_melody)

    MIDI_WHITE = [36, 38, 40, 41, 43, 45,
                  47, 48, 50, 52, 53, 55,
                  57, 58, 60, 62, 64, 65,
                  67, 69, 72, 73, 74, 76,
                  77, 79, 81, 83, 84]
    MIDI_BLACK = [37, 39, 42, 44, 46, 49,
                  51, 54, 56, 58, 61, 63,
                  66, 68, 70, 73, 75, 78,
                  80, 82]

    MIDI_BLACK_WHITE = MIDI_WHITE + MIDI_BLACK

    track = 0
    time = 0
    channel = 0
    channel1 = 1
    channel10 = 3
    volume = 100
    volume1 = 60
    time_melody = 0
    melody_counter = 0

    midi = MIDIFile(1)
    midi.addTrackName(track, time, "music_gen")
    midi.addTempo(track, time, 30)

    grammar_rules = dict()
    for i in range(len(initial_melody)):
        grammar_rules[initial_melody[i]] = []
    for i in range(1, len(initial_melody) - 1):
        grammar_rules[initial_melody[i]] += [initial_melody[i - 1]]
    print(grammar_rules)

    def gen_mel(gr_rules, num_notes):
        init_note = initial_melody[random.randint(0, len(initial_melody) - 1)]
        melody = []
        for k in range(num_notes):
            melody += [gr_rules[init_note][random.randint(0, len(grammar_rules[init_note]) - 1)]]
        return melody

    def gen_local_durations(local_durations, size):
        durations = [1, 0.5, 0.25, 0.125]
        dur_rules = dict()
        dur_rules[1] = [[1], [0.5, 0.5], [0.25, 0.25, 0.25, 0.25],
                        [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]]
        dur_rules[0.5] = [[0.5], [0.25, 0.25], [0.125, 0.125, 0.125, 0.125]]
        dur_rules[0.25] = [[0.25], [0.125, 0.125]]
        dur_rules[0.125] = [[0.125]]

        start_dur = durations[random.randint(0, len(durations) - 1)]
        local_durations += [start_dur]
        sm = start_dur
        if size == '4/4':
            while sm != 2:
                possible_durations = [*dur_rules[start_dur][random.randint(0, len(dur_rules[start_dur]) - 1)]]
                for j in range(len(possible_durations)):
                    if random.randint(0, 1) == 0:
                        possible_durations[j] = random.choice(dur_rules[possible_durations[j]])
                local_durations += [*dur_rules[start_dur][random.randint(0, len(dur_rules[start_dur]) - 1)]]
                sm += start_dur

        elif size == '3/4':
            while sm != 0.5 * 3:
                local_durations += [*dur_rules[start_dur][random.randint(0, len(dur_rules[start_dur]) - 1)]]
                sm += start_dur
                if sm > 0.5 * 3:
                    sm = [0.25, 0.25, 0.5, 0.5]
                    sm = 0.5 * 3

    size = ['4/4', '3/4'][random.randint(0, 1)]
    print(size)
    melody = gen_mel(grammar_rules, 12)

    duration_combinations = [[1, 1, 1, 1], [0.5, 0.5, 0.5, 0.5], [0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
                             [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125,
                              0.125, 0.125, 0.125]]

    NUM_PARTICLES = 1000  # Number of particles in the swarm
    NUM_ITERATIONS = 1000  # Number of iterations
    MAX_NOTE = 83 + 12
    MIN_NOTE = 72

    def evaluate_fitness(melody_fitness, chords_fitness):
        num_notes = len(melody_fitness)
        total_fitness = 0.0

        # if tonic note is in the first or last chord
        if random_key == chords_fitness[0]:
            total_fitness += 1
        if random_key == chords_fitness[-1]:
            total_fitness += 1

        for k in range(num_notes):
            # distance between melody note and chord
            chord_note_distance = abs(chords_fitness[k] - melody_fitness[k])

            # check if dissonant or consonant
            if chord_note_distance in [0, 12, 7, 5]:
                total_fitness += 2
            elif chord_note_distance in [7 + 12, 5 + 12, 24, 7 + 24, 5 + 24]:
                pass
            elif chord_note_distance in [1, 11, 10, 2, 6, 1 + 12, 10 + 12, 2 + 12, 6 + 12, 1 + 24, 11 + 24, 10 + 24,
                                         2 + 24,
                                         6 + 24]:
                total_fitness -= 3

            # check if same
            if chord_note_distance == 0:
                total_fitness += 3

            # if chords offsets are in pentatonic
            if abs(chords_fitness[k] - random_key) in [0, 2, 4, 7, 9] and random_key2 == 'major':
                total_fitness += 1
            elif abs(chords_fitness[k] - random_key) in [0, 3, 5, 7, 10] and random_key2 == 'minor':
                total_fitness += 1

            if k > 0:
                # if chords are not too far
                chord_jump = abs(chords_fitness[k] - chords_fitness[k - 1])
                if chord_jump > 7:
                    total_fitness -= 1
                else:
                    total_fitness += 1

        average_fitness = total_fitness / num_notes

        return average_fitness

    fitness_y = []

    def pso(melody_pso, fitness_x):
        num_notes = len(melody_pso)
        # particles - random notes
        particles = np.random.randint(MIN_NOTE, MAX_NOTE, size=(NUM_PARTICLES, num_notes))
        # velocities - zeros
        velocities = np.zeros((NUM_PARTICLES, num_notes), dtype=int)

        # personal best positions are particles themselves at start and personal best fitness are their fitness values
        personal_best_positions = particles.copy()
        personal_best_fitness = np.array([evaluate_fitness(melody_pso, ch) for ch in particles])

        # global best position with max fitness and its fitness value
        global_best_index = np.argmax(personal_best_fitness)
        global_best_position = personal_best_positions[global_best_index].copy()

        # PSO parameters
        inertia_weight = 0.9
        cognitive_weight = 3.5
        social_weight = 1.5

        # PSO main loop
        for iteration in range(NUM_ITERATIONS):
            for k in range(NUM_PARTICLES):
                # Update velocity
                velocities[k] = (inertia_weight * velocities[k] +
                                 cognitive_weight * np.random.random() * (personal_best_positions[k] - particles[k]) +
                                 social_weight * np.random.random() * (global_best_position - particles[k]))

                # Update position
                particles[k] += velocities[k]
                particles[k] = np.clip(particles[k], MIN_NOTE, MAX_NOTE)

                # Evaluate fitness for the new position
                fitness = evaluate_fitness(melody_pso, particles[k])
                fitness_x += [fitness]

                # Update personal best
                if fitness > personal_best_fitness[k]:
                    personal_best_fitness[k] = fitness
                    personal_best_positions[k] = particles[k].copy()

            # Update global best
            global_best_index = np.argmax(personal_best_fitness)
            global_best_position = personal_best_positions[global_best_index].copy()

        return global_best_position

    chords = pso(melody, fitness_y)
    fitness_x = [i for i in range(len(fitness_y))]

    # fitness_x,fitness_y=fitness_x[0:1000], fitness_y[0:1000]
    fitness_x = np.array(fitness_x)
    fitness_y = np.array(fitness_y)
    plt.plot(fitness_x, fitness_y)
    plt.title("Curve plotted using the given points")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.show()

    print(*melody)
    print(*chords)
    siz = 4 if size == '4/4' else 3
    durations = []
    loc_durations = []
    gen_local_durations(loc_durations, size)
    print(loc_durations)
    for _ in range(1):
        for bar in range(len(melody) // siz):
            sum_dur = 0
            for i in range(2):
                if siz == 4:
                    midi.tracks
                    midi.addNote(track, channel1, chords[bar * siz + (bar % 4 + i)] - 12, time, 1, volume - 40)
                    if random_key2 == 'major':
                        midi.addNote(track, channel1, chords[bar * siz + (bar % 4)] - 12 + 4, time, 1, volume - 40)
                        midi.addNote(track, channel1, chords[bar * siz + (bar % 4)] - 12 + 7, time, 1, volume - 40)
                    else:
                        midi.addNote(track, channel1, chords[bar * siz + (bar % 4)] - 12 + 3, time, 1, volume - 40)
                        midi.addNote(track, channel1, chords[bar * siz + (bar % 4)] - 12 + 7, time, 1, volume - 40)

                    sum_dur = 0
                    for j in range(len(loc_durations)):
                        duration = loc_durations[j % len(loc_durations)]
                        sum_dur += duration
                        if sum_dur == 1:
                            continue
                        try:
                            midi.addNote(track, channel, melody[bar * siz + j], time, duration, volume)
                            midi.addNote(track, channel, melody[bar * siz + j] - 12, time, duration, volume)
                            time += duration
                            pass
                        except:
                            break

                elif siz == 3:
                    midi.addNote(track, channel1, chords[bar * siz + (bar % 3 + i)] - 12, time, 0.5, volume - 40)
                    if random_key2 == 'major':
                        midi.addNote(track, channel1, chords[bar * siz + (bar % 3)] - 12 + 4, time, 0.5, volume - 40)
                        midi.addNote(track, channel1, chords[bar * siz + (bar % 3)] - 12 + 7, time, 0.5, volume - 40)
                    else:
                        midi.addNote(track, channel1, chords[bar * siz + (bar % 3)] - 12 + 3, time, 0.5, volume - 40)
                        midi.addNote(track, channel1, chords[bar * siz + (bar % 3)] - 12 + 7, time, 0.5, volume - 40)

                    sum_dur = 0
                    for j in range(len(loc_durations)):
                        duration = loc_durations[j % len(loc_durations)]
                        sum_dur += duration
                        if sum_dur == 0.5:
                            continue
                        try:
                            midi.addNote(track, channel, melody[bar * siz + j], time, duration, volume)
                            midi.addNote(track, channel, melody[bar * siz + j] - 12, time, duration, volume)
                            time += duration
                            pass
                        except:
                            break

    with open("chorus.mid", 'wb') as out:
        midi.writeFile(out)

    return midi


