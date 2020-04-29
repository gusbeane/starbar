import numpy as np
import arepo
import sys
from tqdm import tqdm
from scipy.optimize import minimize

m_p = 1.67262178e-24 # g
k = 1.38065e-16 # cgs

G = 43007.1

def compute_u_from_T(T):
    # T in K
    if T > 1e4:
        mu = 10.0/17.0 #Assume fully ionised, ignore metals
    else:
        mu = 50.0/41.0 #Assume fully neutral, ignore metals

    u = (3.0 * k * T) / (2.0 * mu * m_p) # cgs units
    u /= 1e10 # code units
    return u

def _Q2_of_k_(k, cs, kappa, sigmaR, sigmaStar, sigmaGas):
    Qg = (kappa**2 + (k*cs)**2) / (2. * np.pi * G * k * sigmaGas)
    Qs = (kappa**2 + (k*sigmaR)**2) / (2. * np.pi * G * k * sigmaStar)
    return 1./(1./Qg + 1./Qs)

def _toomre2_(kmin, kmax, cs, kappa, sigmaR, sigmaStar, sigmaGas):
    fun_list = []
    x_list = []
    print('cs=', cs, 'kappa=', kappa, 'sigmaR=', sigmaR, 'sigmaStar=', sigmaStar, 'sigmaGas=', sigmaGas)
    for kguess in np.logspace(np.log10(kmin), np.log10(kmax), 10):
        ans = minimize(_Q2_of_k_, kguess, (cs, kappa, sigmaR, sigmaStar, sigmaGas), bounds=((kmin, kmax),))
        fun_list.append(ans.fun[0])
        x_list.append(ans.x)

    fun = np.min(fun_list)
    x = x_list[np.argmin(fun)]

    return fun, x

def _toomre_star_(kappa, sigmaR, sigmaStar):
    return kappa * sigmaR / (3.36 * G * sigmaStar)


def compute_two_comp_toomre(path, name, output_dir='data/'):
    # try loading snapshot
    dat = np.genfromtxt(path+'/ICs/MW_ICs.vc2comp', names=True)

    gamma = 5./3.
    u = compute_u_from_T(1e4)
    cs2 = gamma * (gamma-1) * u

    kmin = 0.06
    kmax = 6000.0

    Q_star = []
    Q2_list = []
    for kappa, sigmaR, sigmaStar, sigmaGas in zip(tqdm(dat['kappa']), dat['sigmaR'], dat['sigmaStar'], dat['sigmaGas']):
        Q = _toomre_star_(kappa, sigmaR, sigmaStar)
        Q2, k = _toomre2_(kmin, kmax, np.sqrt(cs2), kappa, sigmaR, sigmaStar, sigmaGas)
        
        Q_star.append(Q)
        Q2_list.append(Q2)

    np.save(output_dir+name+'-Q2.npy', np.transpose([dat['R'], Q_star, Q2_list]))


if __name__ == '__main__':

    basepath = '../../runs/'

    fid_g1 = 'fid-disp1.0-fg0.1'
    fid_d15_g1 = 'fid-disp1.5-fg0.1'

    # look to see if we are on my macbook or on the cluster
    if sys.platform == 'darwin':
        pair_list = [(fid_g1, 'lvl5'), (fid_d15_g1, 'lvl5')]
    else:
        pair_list = [(fid_g1, 'lvl5'), (fid_g1, 'lvl4'), (fid_g1, 'lvl3')]

    name_list = [           p[0] + '-' + p[1] for p in pair_list]
    path_list = [basepath + p[0] + '/' + p[1] for p in pair_list]
                                            
    for path, name in zip(path_list, name_list):
        compute_two_comp_toomre(path, name)
    
