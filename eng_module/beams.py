import math, csv
from PyNite import FEModel3D, Visualization
from utils import str_to_int, str_to_float, read_csv_file

def calc_shear_modulus(nu: float, E: float)-> float:
    """
    Returns the shear modulus of a material.

    'nu' - Poisson's ratio for a linear elastic material
    'E' - Elastic modulus of the material

    Assumptions:
    - linear elastic behavior
    """
    G=E/(2*(1+nu))
    return G 

def euler_buckling_load(l: float, E: float, I: float, k: float)-> float:
    """
    Returns the critical Euler buckling load for a column

    'l' - length of the column
    'E' - Elastic modulus of the column material
    'I' - Moment of inertial of the column section
    'k' - Effective length factor
    """
    Pcr = math.pi**2*E*I/(k*l)**2
    return Pcr

def beam_reactions_ss_cant(w: float, b: float, a: float)-> float:
    """
    Returns the reactions for a simple supported beam with a continuous cantilever on one end.

    'w' - Uniform distributed load on the beam
    'a' - Length of the cantilever
    'b' - Length of the backspan
    """
    R1 = w*(a+b)**2/(2*b)
    R2 = w*(a+b)-R1
    return R1, R2

def fe_model_ss_cant(w: float, b: float, a:float, E: float=1., I: float=1., A: float=1., J: float=1., nu: float=1., rho: float=1.)-> FEModel3D:
    """
    Returns the FE model for a simple supported beam with a continuous cantilever on one end.

    'w' - Uniform distributed load on the beam
    'a' - Length of the cantilever
    'b' - Length of the backspan
    'E' - Elastic modulus of the beam material
    'I' - Moment of inertial of the beam section
    'A' - Area of the beam section
    'J' - The polar moment of inetial of the beam section
    'nu' - Poisson's ratio of the beam material
    'rho' - The density of the beam material
    """

    beam_model = FEModel3D()
    
    G = calc_shear_modulus(nu, E)
    beam_model.add_material('Mat', E, G, nu, rho)

    beam_model.add_node('N0', 0, 0, 0)
    beam_model.add_node('N1', b, 0, 0)
    beam_model.add_node('N2', b+a, 0, 0)

    beam_model.add_member('Beam','N0','N2','Mat', 1, I, J, A)

    beam_model.def_support('N0',True, True, True, True, False, False)
    beam_model.def_support('N1',False, True, True, False, False, False)

    beam_model.add_member_dist_load('Beam', 'Fy', w, w, beam_model.Nodes['N0'].X, beam_model.Nodes['N2'].X)

    return beam_model

def read_beam_file(file_name: str)-> list[list[str]]:
    """
    Returns the contents of a file
    'file_name' - name of the file to be read
    """
    return read_csv_file(file_name)

def separate_data(file_data: list[str])-> list[list[str]]:
    '''
    Returns the file data in a list of individual strings
    '''
    file_separated_data = []
    for data in file_data:
        file_separated_data.append(data.split(', '))

    return file_separated_data

def convert_to_numeric(str_data:list[list[str]])->list[list[float]]:
    '''
    Return a list[list[float]]
    '''
    numeric_data = []
    for line_data in str_data:
        float_data = []
        for data in line_data:
            float_data.append(str_to_float(data))
        numeric_data.append(float_data)

    return numeric_data

def separate_lines(file_data: str)-> list[str]:
    """
    Returns file data that contains new line characters separated into individual lines
    'file_data' - Contents of the file to be separated into lines
    """
    data = file_data.split('\n')

    return data

def extract_data(list_data: list[str], index: int)-> str:
    """
    Returns the data located in the specified index
    'list_data' - List of data
    'index' - Position in the list of data that will be extracted
    """
    data = list_data[index].split(', ')

    return data

def get_spans(beam_length: float, cant_support_loc: float)-> tuple[float, float]:
    """
    Returns the length of the backspan ('b') and the length of the cantilever ('a') for a simply supported beam with a cantilever at one end
    'beam_lenth' - Total length of the simply supported beam
    'cant_support_loc' - Location of the support of the cantilever

    ASSUMPTIONS:
    This function will assume that the backspan support is located at 0.0
    """

    b = cant_support_loc
    a = beam_length - cant_support_loc

    return b, a

def build_beam(beam_data: dict, A: float = 1., J: float = 1., nu: float = 0.2, rho: float = 25.) -> FEModel3D:
    """
    Returns a beam finite element model for the data in 'beam_data' dictionary
    """
    beam_model = FEModel3D()

    G = beams.calc_shear_modulus(nu, beam_data['E'])
    beam_model.add_material('Mat', beam_data['E'], G, nu, rho)

    for idx, node in enumerate(beam_data['Supports']):
         beam_model.add_node(f'N{idx}', node, 0., 0.)

    beam_model.add_member(beam_data['Name'], 'N0', f'N{idx}', 'Mat', 1., beam_data['Iz'], J, A)

    for node in beam_model.Nodes:
        beam_model.def_support(node, False, True, True, False, False, False)
    beam_model.def_support('N0', True, True, True, True, False, False)
    
    for idx,load in enumerate(beam_data['Loads']):
        beam_model.add_member_dist_load(beam_data['Name'], 'Fy', load[0], load[0], load[1], load[2]) 

    return beam_model

def load_beam_model(file_name: str)-> FEModel3D:
    """
    Returns the the FE model of a simply supported beam loaded with an uniform load
    'file_name' - Name of the file were the data is located
    """
    beam_data = get_structured_beam_data(read_beam_file(file_name))
    beam_model = build_beam(beam_data)
    return beam_model

def parse_supports(list_of_supports: list[str])-> dict[float, str]:
    '''
    Returns a dicionary with the X coordinate of support and the rigidity of the node
    '''
    support_data = {}
    for support in list_of_supports:
        support_data.update({str_to_float(support[0:-2]): support[-1]})

    return support_data

def parse_loads(list_of_loads: list[list[float,str]])-> list[dict]:
    '''
    Returns a dictionary with the load data
    '''
    load_data = []
    for load in list_of_loads:
        if load[0][0:-3].upper() == 'POINT':
            load_data.append(
                {
                    'Type': 'Point',
                    'Direction': load[0][-2:],
                    'Magnitude': load[1],
                    'Location': load[2],
                    'Case': load[3][5:]
                }
            )
        elif load[0][0:-3].upper() == 'DIST':
            load_data.append(
                {
                    'Type': 'Dist',
                    'Direction': load[0][-2:],
                    'Start Magnitude': load[1],
                    'End Magnitude': load[2],
                    'Start Location': load[3],
                    'End Location': load[4],
                    'Case': load[5][5:]
                }
            )
    
    return load_data

def parse_beam_attributes(beam_attributes: list[float])-> dict[str,float]:
    '''
    Returns a dictionary with the beam attributes
    '''
    beam_data = {
        'L': 1.,
        'E': 1.,
        'Iz':1.,
        'Iy':1.,
        'A': 1.,
        'J': 1.,
        'nu': 1.,
        'rho': 1.
    }
    aux_keys = [key for key in beam_data.keys()]
    for idx, attribute in enumerate(beam_attributes):
        beam_data.update({aux_keys[idx]: attribute})

    return beam_data

def get_structured_beam_data(str_data:list[list[str]])->dict:
    '''
    Returns structured data in dictionary format
    '''
    beam_data = convert_to_numeric(str_data)
    name = {'Name': beam_data[0][0]}
    beam_atributes = parse_beam_attributes(beam_data[1])
    supports = {'Supports': parse_supports(beam_data[2])}
    loads = {'Loads': parse_loads(beam_data[3:])}

    structured_beam_data = name| beam_atributes| supports| loads

    return structured_beam_data

def get_node_locations(beam_length: float, supports: list[float])-> dict[str, float]:
    '''
    Returns a dictionary with the node location
    '''
        
    node_locations = {'N0': 0.}
    idx = 1
    for coord in supports:
        if coord > 0. and coord < beam_length and coord not in node_locations.values():
            node_locations.update({f'N{idx}': coord})
            idx += 1
    node_locations.update({f'N{idx}': beam_length})

    return node_locations     

def build_beam(beam_data: dict) -> FEModel3D:
    """
    Returns a beam finite element model for the data in 'beam_data' dictionary
    """
    beam_model = FEModel3D()

    G = calc_shear_modulus(beam_data['nu'], beam_data['E'])
    beam_model.add_material('Mat', beam_data['E'], G, beam_data['nu'], beam_data['rho'])

    node_locations = get_node_locations(beam_data['L'], list(beam_data['Supports'].keys()))
    connectivity = {'P': [True, True, True, False, False, False], 'F': [False, True, True, True, False, False], 'R': [True, True, True, True, True, True]}
    for idx, node in enumerate(node_locations.values()):
         beam_model.add_node(f'N{idx}', node, 0., 0.)
         if node in beam_data['Supports'].keys():
            beam_model.def_support(f'N{idx}', *connectivity[beam_data['Supports'][node]])

    beam_model.add_member(beam_data['Name'], 'N0', f'N{idx}', 'Mat', beam_data['Iy'], beam_data['Iz'], beam_data['J'], beam_data['A'])

    for load in beam_data['Loads']:
        if load['Type'].upper() == 'POINT':
            beam_model.add_member_pt_load(beam_data['Name'], *list(load.values())[1:-1])
        elif load['Type'].upper() == 'DIST':
            beam_model.add_member_dist_load(beam_data['Name'], *list(load.values())[1:-1])

    return beam_model
