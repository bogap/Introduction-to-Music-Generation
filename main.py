from accompaniment_generator import *
from genetic_algo import *
from chorus_generator import *
from melody_generator import *
from music_composition import *

# # Verse melody generation
# value = 1
# while value != 0:
#     melody = Melody('rivers_flow_in_you.mid')
#     value = melody.generate()
#
# # Verse accompaniment generation
# midi_file = 'verse_melody.mid'
# GA = GeneticAlgo(midi_file)
# accomp = Accompaniment(midi_file, GA.chromosome_size)
# accomp.generate_accomp()
#
# # Chorus generation
# generate_chorus('rivers_flow_in_you.mid')

# Play composition
play()
