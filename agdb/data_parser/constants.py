PERIOD_TABLE = {'Ac': 89, 'Ag': 47, 'Al': 13, 'Am': 95, 'Ar': 18, 'As': 33, 'At': 85, 'Au': 79, 'B': 5, 'Ba': 56,
                'Be': 4, 'Bi': 83, 'Bk': 97, 'Br': 35, 'C': 6, 'Ca': 20, 'Cd': 48, 'Ce': 58, 'Cf': 98, 'Cl': 17,
                'Cm': 96, 'Co': 27, 'Cr': 24, 'Cs': 55, 'Cu': 29, 'Dy': 66, 'Er': 68, 'Es': 99, 'Eu': 63, 'F': 9,
                'Fe': 26, 'Fm': 100, 'Fr': 87, 'Ga': 31, 'Gd': 64, 'Ge': 32, 'H': 1, 'He': 2, 'Hf': 72, 'Hg': 80,
                'Ho': 67, 'I': 53, 'In': 49, 'Ir': 77, 'K': 19, 'Kr': 36, 'La': 57, 'Li': 3, 'Lr': 103, 'Lu': 71,
                'Md': 101, 'Mg': 12, 'Mn': 25, 'Mo': 42, 'N': 7, 'Na': 11, 'Nb': 41, 'Nd': 60, 'Ne': 10, 'Ni': 28,
                'No': 102, 'Np': 93, 'O': 8, 'Os': 76, 'P': 15, 'Pa': 91, 'Pb': 82, 'Pd': 46, 'Pm': 61, 'Po': 84,
                'Pr': 59, 'Pt': 78, 'Pu': 94, 'Ra': 88, 'Rb': 37, 'Re': 75, 'Rh': 45, 'Rn': 86, 'Ru': 44, 'S': 16,
                'Sb': 51, 'Sc': 21, 'Se': 34, 'Si': 14, 'Sm': 62, 'Sn': 50, 'Sr': 38, 'Ta': 73, 'Tb': 65, 'Tc': 43,
                'Te': 52, 'Th': 90, 'Ti': 22, 'Tl': 81, 'Tm': 69, 'U': 92, 'V': 23, 'W': 74, 'Xe': 54, 'Y': 39,
                'Yb': 70, 'Zn': 30, 'Zr': 40, 'Rf': 104, 'Db': 105, 'Sg': 106, 'Bh': 107, 'Hs': 108, 'Mt': 109,
                'Ds': 110, 'Rg': 111, 'Cn': 112, 'Nh': 113, 'Fl': 114, 'Mc': 115, 'Lv': 116, 'Ts': 117, 'Og': 118}

LIGHT_SPEED = 137.03599967994   # http://physics.nist.gov/cgi-bin/cuu/Value?alph
# BOHR = .529 177 210 92(17) e-10m  # http://physics.nist.gov/cgi-bin/cuu/Value?bohrrada0
BOHR = 0.52917721092  # Angstroms
BOHR_SI = BOHR * 1e-10

ALPHA = 7.2973525664e-3         # http://physics.nist.gov/cgi-bin/cuu/Value?alph
G_ELECTRON = 2.00231930436182   # http://physics.nist.gov/cgi-bin/cuu/Value?gem
E_MASS = 9.10938356e-31         # kg https://physics.nist.gov/cgi-bin/cuu/Value?me
AVOGADRO = 6.022140857e23       # https://physics.nist.gov/cgi-bin/cuu/Value?na
ATOMIC_MASS = 1e-3/AVOGADRO
PROTON_MASS = 1.672621898e-27   # kg https://physics.nist.gov/cgi-bin/cuu/Value?mp
PROTON_MASS_AU = PROTON_MASS/ATOMIC_MASS
MP_ME = PROTON_MASS / E_MASS    # Proton-to-electron mass ratio
BOHR_MAGNETON = 927.4009994e-26 # J/T http://physics.nist.gov/cgi-bin/cuu/Value?mub
NUC_MAGNETON = BOHR_MAGNETON / MP_ME
PLANCK = 6.626070040e-34        # J*s http://physics.nist.gov/cgi-bin/cuu/Value?h
HBAR = PLANCK/(2*3.141592653589793) # https://physics.nist.gov/cgi-bin/cuu/Value?hbar
#HARTREE2J = 4.359744650e-18     # J https://physics.nist.gov/cgi-bin/cuu/Value?hrj
HARTREE2J = HBAR**2/(E_MASS*BOHR_SI**2)
HARTREE2EV = 27.21138602        # eV https://physics.nist.gov/cgi-bin/cuu/Value?threv
E_CHARGE = 1.6021766208e-19     # C https://physics.nist.gov/cgi-bin/cuu/Value?e
LIGHT_SPEED_SI = 299792458      # https://physics.nist.gov/cgi-bin/cuu/Value?c
DEBYE = 3.335641e-30            # C*m = 1e-18/LIGHT_SPEED_SI https://cccbdb.nist.gov/debye.asp
AU2DEBYE = E_CHARGE * BOHR*1e-10 / DEBYE # 2.541746
AUEFG = 9.71736235660e21        # V/m^2 https://physics.nist.gov/cgi-bin/cuu/Value?auefg
AU2TESLA = HBAR/(BOHR_SI**2 * E_CHARGE)
BOLTZMANN = 1.38064852e-23      # J/K https://physics.nist.gov/cgi-bin/cuu/Value?k
HARTREE2WAVENUMBER = 1e-2 * HARTREE2J / (LIGHT_SPEED_SI * PLANCK) # 2.194746313702e5
AMU2AU = ATOMIC_MASS/E_MASS
