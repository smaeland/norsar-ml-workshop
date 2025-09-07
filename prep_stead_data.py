import csv
import h5py
import numpy as np

def pick_events(num_events=1000):

    # Collect the contents of the flippin csv files
    signal_traces = []
    errors = 0
    with open('chunk2.csv') as fin:

        header = fin.readline()

        for line in fin:
            row = line.strip().split(',')
            try:
                name, p_start, s_start, mag = row[-1], float(row[6]), float(row[10]), float(row[23])
            except ValueError:
                errors += 1
                continue

            signal_traces.append([name, p_start, s_start, mag])

    print(f'Signal file: {errors} errors')

    noise_traces = []
    with open('chunk1.csv') as fin:

        header = fin.readline()

        for line in fin:
            row = line.strip().split(',')
            name = row[-1]
            noise_traces.append([name, -1, -1, -1])


    # Read h5 files and randomly pick events
    fin_signal = h5py.File('chunk2.hdf5', 'r')
    data_signal = fin_signal.get('data')
    fin_noise = h5py.File('chunk1.hdf5', 'r')
    data_noise = fin_noise.get('data')

    data_out = []
    type_out = []
    p_start_out = []
    s_start_out = []
    mag_out = []

    rng = np.random.default_rng()

    while len(data_out) < num_events:

        type = rng.integers(0, 1, endpoint=True)

        if type == 0:
            name, p_start, s_start, mag = noise_traces.pop(0)
            data_out.append(data_noise.get(name)[:])

        elif type == 1:
            name, p_start, s_start, mag = signal_traces.pop(0)
            data_out.append(data_signal.get(name)[:])

        type_out.append(type)
        p_start_out.append(p_start)
        s_start_out.append(s_start)
        mag_out.append(mag)

        print('name:', name, 'type:', type, 'p_start:', p_start, 's_start:', s_start, 'mag:', mag)

    fout = h5py.File('selected_events.h5', 'w')
    fout.create_dataset('waveforms', data=np.stack(data_out), dtype=np.float32)
    fout.create_dataset('type', data=np.array(type_out), dtype=np.int8)
    fout.create_dataset('p_start', data=np.array(p_start_out), dtype=np.int16)
    fout.create_dataset('s_start', data=np.array(s_start_out), dtype=np.int16)
    fout.create_dataset('mag', data=np.array(mag_out), dtype=np.float16)

    fout.close()



if __name__ == '__main__':
    pick_events(10)

