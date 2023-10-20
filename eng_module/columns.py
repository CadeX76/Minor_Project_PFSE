from math import pi, sqrt
from dataclasses import dataclass
from eng_module import utils, load_factors

@dataclass
class Column:
    h: float
    E: float
    A: float
    Ix: float
    Iy: float
    kx: float
    ky: float

    def critical_buckling_load(self, axis: str)-> float:
        if axis.upper() == 'X':
            return euler_buckling_load(self.h, self.E, self.Ix, self.kx)
        elif axis.upper() == 'Y':
            return euler_buckling_load(self.h, self.E, self.Iy, self.ky)
        else:
            raise ValueError(f"Axis must be one of 'x' or 'y', not {axis}")
    
    def radius_of_gyration(self, axis: float)-> float:
        if axis.upper() == 'X':
            return radius_gyration(self.Ix, self.A)
        elif axis.upper() == 'Y':
            return radius_gyration(self.Iy, self.A)
        else:
            raise ValueError(f"Axis must be one of 'x' or 'y', not {axis}")

@dataclass
class SteelColumn(Column):
    fy: float
    gamma_m1: float = 1.0

    def factored_compressive_resistance(self, buckling_curve: str = 'b')-> float:
        pcr = min(
            self.critical_buckling_load('x'),
            self.critical_buckling_load('y')
        )
        
        lmda = lamda(self.A, self.fy, pcr)
        
        return qsi(lmda, buckling_curve)*self.A*self.fy/self.gamma_m1

    def factored_crushing_load(self):
        return self.A*self.fy/self.gamma_m1

def euler_buckling_load(h: float, E: float, I: float, k: float)-> float:
    '''
    Returns the Euler critical bucking load
    '''
    return (pi**2)*E*I/(k*h)**2
    

def radius_gyration(I: float, A: float)-> float:
    '''
    Returns the radius of gyration
    '''
    return sqrt(I/A)

def lamda(a_w: float, fy: float, pcr_mcr: float)-> float:
    '''
    Returns the non-dimensional slenderness of an element
    'a_w' - Is either be the area or the elastic modulus of the section
    'fy' - Is the material yield stress
    'pcr_mcr' - Is either the Euler buckling load or the 
    '''
    return sqrt(a_w*fy/pcr_mcr)

def imperfection_factor(buckling_curve: str)-> float:
    '''
    Returns the imperfection factor
    '''
    alfa = {
        'a0': 0.13,
        'a': 0.21,
        'b': 0.34,
        'c': 0.49,
        'd': 0.76
    }
    
    if buckling_curve.lower() in alfa.keys():
        return alfa[buckling_curve.lower()]
    else:
        raise ValueError(f"The buckling curve must be one of 'a0', 'a', 'b', 'c' or 'd', not {buckling_curve}")

def qsi(lmda: float, buckling_curve: str)-> float:
    '''
    Returns the reduction factor for the compressive resistance
    '''
    alfa = imperfection_factor(buckling_curve)
    teta = 0.5*(1+alfa*(lmda-0.2)+lmda**2)
    qsi = 1/(teta+sqrt(teta**2-lmda**2))

    return (qsi <= 1.0) * qsi + (qsi> 1.0)*1

def csv_record_to_steelcolumn(record: list[str], **kwargs)-> SteelColumn:
    sc = SteelColumn(
        A = utils.str_to_float(record[1]),
        h = utils.str_to_float(record[2]),
        Ix = utils.str_to_float(record[3]),
        Iy = utils.str_to_float(record[4]),
        fy = utils.str_to_float(record[5]),
        E = utils.str_to_float(record[6]),
        kx = utils.str_to_float(record[7]),
        ky = utils.str_to_float(record[8]),
        **kwargs
    )
    
    return sc

def convert_csv_data_to_steelcolumns(csv_data: list[list[str]])-> list[SteelColumn]:
    '''
    Returns a list of steel columns
    '''
    converted_data = []
    for data in csv_data[1:]:
        converted_data.append(csv_record_to_steelcolumn(data))

    return converted_data

def calculate_factored_csv_load(record: list[str])-> float:
    '''
    Returns the factored load from csv data
    '''
    loads = {'D': utils.str_to_float(record[9]), 'L': utils.str_to_float(record[10])}
    factored_load = []
    for combo in load_factors.EC_COMBINATIONS.values():
        factored_load.append(load_factors.factor_load(**loads, **combo))

    return max(factored_load)

def run_all_columns(filename: str, **kwargs)-> list[SteelColumn]:
    '''
    Returns a list of Steel Columns in a csv file with the loading demand and capacity
    '''
    file_data = utils.read_csv_file(filename)
    list_of_steelcolumns = []
    for data in file_data[1:]:
        steelcolumn = csv_record_to_steelcolumn(data)
        list_of_steelcolumns.append(steelcolumn)
        demand = calculate_factored_csv_load(data)
        capacity = min(steelcolumn.factored_compressive_resistance(), steelcolumn.factored_crushing_load())
        ratio = demand / capacity
        steelcolumn.factored_load = demand
        steelcolumn.demand_capacity_ratio = ratio
    
    return list_of_steelcolumns