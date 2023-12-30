import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import time

# TODO: Architecture:   - UI that opens a sample from a song which allows you to low pass it
# TODO:                 - The UI contains a knob which allows us to change the cutoff frequency and displays the updated signal after 2 seconds (debouncing)
# TODO:                 - The UI should allow us to play the original song and the low passed song
# TODO: Figure out how to import a sound and transform it into a numpy array
# TODO: Figure ouy how to use PyQT and how to plot using PyQT # https://www.youtube.com/watch?v=je9Cj7G5pnY. If this doesn't work fall back to jupyter notebooks? 

def apply_filter(b, a, inputs):
    outputs = np.zeros(inputs.size)

    for input_index in range(0, inputs.size):
        # print("y[{0}]=".format(input_index), end="")
        for b_index in range(0, b.size):
            if input_index - b_index >= 0:
                # print("+b[{0}]x[{1}]=".format(b_index, input_index - b_index), end="")
                outputs[input_index] = outputs[input_index] + b[b_index] * inputs[input_index - b_index]
        for a_index in range(1, a.size):
            if input_index - a_index >= 0:
                # print("-a[{0}]y[{1}]=".format(a_index, input_index - a_index), end="")
                outputs[input_index] = outputs[input_index] - a[a_index] * outputs[input_index - a_index]
        # print()
    return outputs

def main_loop():
    sample_period = 0.1
    sample_freq = 1 / sample_period
    cutoff_freq = 0.4
    samples = np.arange(0, 100, 0.1, dtype=float)

    original_signal = np.sin(0.08 * samples) + np.sin(0.2 * samples) + np.sin(0.32 * samples) + np.sin(0.4 * samples)
    signal_with_noise = original_signal + np.random.rand(original_signal.size) - np.random.rand(original_signal.size)
    b, a = sp.signal.butter(3, cutoff_freq/sample_freq)

    plt.ion()
    figure = plt.figure()
    subplot = figure.add_subplot(1, 1, 1)
    graph_original_signal, graph_signal_with_noise, graph_signal_filtered = subplot.plot(samples, original_signal, 
                                                                                         samples, original_signal, 
                                                                                         samples, original_signal)

    while True:
        signal_with_noise = original_signal + np.random.rand(original_signal.size) - np.random.rand(original_signal.size)
        filtered_signal = apply_filter(b, a , signal_with_noise)
        graph_signal_with_noise.set_ydata(signal_with_noise)
        graph_signal_filtered.set_ydata(filtered_signal)
        figure.canvas.draw()
        figure.canvas.flush_events()
        time.sleep(1)

if __name__ == "__main__":
    main_loop()
