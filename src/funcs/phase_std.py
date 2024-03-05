import numpy as np

from scipy.special import gamma as G
from scipy.special import hyp2f1 
def phase_pdf(cor, L, phase, expected_phase = 0.0):
    return (G(L + 1/2) * (1 - cor**2)**L * cor * np.cos(phase - expected_phase)) / (2 * np.pi**0.5 * G(L) * (1 - cor**2 * np.cos(phase - expected_phase)**2)**(L+1/2)) + ((1 - cor**2)**L / (2 * np.pi)) * hyp2f1(L, 1, 0.5, cor**2 * np.cos(phase - expected_phase)**2)

def phase_pdf_timex(cor, L, phase, expected_phase = 0.0):
    return phase* phase_pdf(cor, L, phase)

def phase_pdf_timex2(cor, L, phase, expected_phase = 0.0):
    return phase**2 * phase_pdf(cor, L, phase)

import scipy.integrate as integrate
from functools import partial
def get_pdf_moments(cor, L):
    f = partial(phase_pdf_timex, cor, L)
    Ex = integrate.quad(f, -np.pi, np.pi)[0]
    f = partial(phase_pdf_timex2, cor, L)
    E2x = integrate.quad(f, -np.pi, np.pi)[0] - Ex
    # Ex,
    return E2x**0.5