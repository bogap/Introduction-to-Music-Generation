from melody_generator import Melody

if __name__ == '__main__':
    value = 1
    while value != 0:
        melody = Melody('rivers_flow_in_you.mid')
        value = melody.generate()
