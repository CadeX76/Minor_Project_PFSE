from math import sqrt, pi
from dataclasses import dataclass

@dataclass
class Ec_response_spectrum:
    ag: float
    spectra_type: int = 1
    soil_type: str = 'C'
    damping: float = 5.0

    def acceleration(self, T: float) -> float:
        S, Tb, Tc, Td = response_spectrum_parameters(self.spectra_type, self.soil_type).values()
        n = sqrt(10 / (5 + self.damping))
        nu = (n >= 0.55) * n + (n < 0.55)*0.55
       
        if T >= 0. and T <= Tb:
            Se = self.ag * S * (1 + T / Tb * (nu * 2.5 - 1.))

        elif T > Tb and T <= Tc:
            Se = self.ag * S * nu * 2.5

        elif T > Tc and T <= Td:
            Se = self.ag * S * nu * 2.5 * (Tc / T)

        elif T > Td and T <= 4:
            Se = self.ag * S * nu * 2.5 * (Tc * Td / T ** 2)
        
        else:
            raise ValueError(f'The value of the period of the system needs to be between 0 sec and 4 sec. The current value is {T}')
    
        return Se

    def displacement(self, T: float)-> float:
        Sd = self.acceleration(T) * (T/(2 * pi)) ** 2

        return Sd

def response_spectrum_parameters(spectra_type: int, soil_type: int) -> dict[str, float]:
    rsp = {
        1:{
            'A':{
                'S': 1.0, 'Tb': 0.15, 'Tc': 0.4, 'Td':2.0
            },
            'B':{
                'S': 1.2, 'Tb': 0.15, 'Tc': 0.5, 'Td':2.0
            },
            'C':{
                'S': 1.15, 'Tb': 0.20, 'Tc': 0.6, 'Td':2.0
            },
            'D':{
                'S': 1.35, 'Tb': 0.20, 'Tc': 0.8, 'Td':2.0
            },
            'E':{
                'S': 1.4, 'Tb': 0.15, 'Tc': 0.5, 'Td':2.0
            }
        },
        2:{
            'A':{
                'S': 1.0, 'Tb': 0.05, 'Tc': 0.25, 'Td':1.2
            },
            'B':{
                'S': 1.35, 'Tb': 0.05, 'Tc': 0.25, 'Td':1.2
            },
            'C':{
                'S': 1.5, 'Tb': 0.10, 'Tc': 0.25, 'Td':1.2
            },
            'D':{
                'S': 1.8, 'Tb': 0.10, 'Tc': 0.3, 'Td':1.2
            },
            'E':{
                'S': 1.6, 'Tb': 0.05, 'Tc': 0.25, 'Td':1.2
            }
        }
    }
        
    return rsp[spectra_type][soil_type]

def system_demand(mass: float, spectrum: Ec_response_spectrum) -> list[float]:
    period_range = list(range(0, 400, 1))
    y_demand = []
    x = []
    for t in period_range:
        force = mass * spectrum.acceleration(t/100)
        disp = spectrum.displacement(t/100)
        y_demand.append(force)
        x.append(disp)
    xy_demand = list(zip(x, y_demand))

    return xy_demand

def system_capacity(k_type: str, x: list[float], k1: float, k2: float = 0., f1max: float = 0.) -> list[float]:
    y_capacity = []
    for xi in x:
        if k_type == 'Linear':
            capacity = k1 * xi
            y_capacity.append(capacity)
        elif k_type == 'Multi-linear':
            force_first_branch = k1 * xi
            capacity = (force_first_branch <= f1max) * force_first_branch + (force_first_branch > f1max) * (f1max + k2 * (xi - f1max / k1))
            y_capacity.append(capacity)   
    xy_capacity = list(zip(x, y_capacity))

    return xy_capacity


