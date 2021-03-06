import matplotlib.pyplot as plt 
import numpy as np 
import pickle

def plot_pattern_speed(name_list, c_list, ls_list, fout, n=5):
    fig, ax = plt.subplots(1, 1)

    for name, c, ls in zip(name_list, c_list, ls_list):
        fdata = 'data/veldisp_' + name + '.p'

        dat = pickle.load(open(fdata, 'rb'))

        time = dat[:,0]
        sigmaR = dat[:,1]
        sigmaz = dat[:,3]

        ax.plot(time, sigmaR/sigmaz, c=c, ls=ls, label=name)


    ax.set_xlabel('time [Myr]')
    ax.set_ylabel('sigmaR/sigmaz')
    ax.legend(frameon=False)

    fig.tight_layout()
    fig.savefig(fout)

if __name__ == '__main__':
    name_list = ['nbody-lvl5']#, 'nbody-lvl4', 'nbody-lvl3']
    c_list = [None, None, None]
    ls_list = [None, None, None]

    plot_pattern_speed(name_list, c_list, ls_list, 'veldisp_nbody.pdf')

