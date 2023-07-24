from accompaniment_generator import *
from genetic_algo import *
from chorus_generator import *
from melody_generator import *
from music_composition import *
import time

start_time = time.time()

orig = 'rivers_flow_in_you.mid'

# Verse melody generation
value = 1
while value != 0:
    melody = Melody(orig)
    value = melody.generate()

# Verse accompaniment generation
midi_file = 'verse_melody.mid'
GA = GeneticAlgo(midi_file)
accomp = Accompaniment(midi_file, GA.chromosome_size)
accomp.generate_accomp()

# Chorus generation
generate_chorus(orig)

end_time = time.time()
runtime = end_time - start_time
print("Generation time: {:.6f} seconds".format(runtime))

# Play composition
play()
