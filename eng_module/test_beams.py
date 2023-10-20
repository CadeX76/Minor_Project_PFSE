import beams, pytest

def test_calc_shear_modulus():
    test_value1 = beams.calc_shear_modulus(0.2,35)
    test_value2 = beams.calc_shear_modulus(0.3,200)
       
    assert test_value1 == pytest.approx(14.583333)
    assert test_value2 == pytest.approx(76.923077)

def test_euler_buckling_load():
    test_value1 = beams.euler_buckling_load(5300,200000,632e6,1.0)
    test_value2 = beams.euler_buckling_load(212,3645,5125.4,2.0)
       
    assert test_value1 == pytest.approx(44411463.02234584)
    assert test_value2 == pytest.approx(1025.6361727834453)

def test_beam_reactions_ss_cant():
    test_value1 = beams.beam_reactions_ss_cant(50,4500,2350)
    test_value2 = beams.beam_reactions_ss_cant(19,96,96)
    
    assert test_value1 == (260680.55555555556, 81819.44444444444)
    assert test_value2 == (3648.0, 0.0)

def test_fe_model_ss_cant():
    beam_model=beams.fe_model_ss_cant(50, 4500, 2350)
    beam_model.analyze_linear()
    R1 = beam_model.Nodes['N1'].RxnFY['Combo 1']
    R2 = beam_model.Nodes['N0'].RxnFY['Combo 1']

    assert R1 == -260680.55555555553
    assert R2 == -81819.44444444447

    beam_model=beams.fe_model_ss_cant(19, 96, 96)
    beam_model.analyze_linear()
    R1 = beam_model.Nodes['N1'].RxnFY['Combo 1']
    R2 = beam_model.Nodes['N0'].RxnFY['Combo 1']

    assert R1 == -3648.000000000001
    assert R2 == 1.1368683772161603e-13

def test_read_beam_file():
    beam1_data = beams.read_beam_file('test_data/beam_1.txt')
    beam4_data = beams.read_beam_file('test_data/beam_4.txt')

    assert beam1_data == [['4800', ' 200000', ' 437000000'], ['0', ' 3000'], ['-10']]
    assert beam4_data == [['8000', ' 28000', ' 756e6'], ['0', ' 7000'], ['-52']]

def test_separate_lines():
    example1_data = '4800, 200000, 437000000\n0, 3000\n-10'
    example2_data = '8000, 28000, 756e6\n0, 7000\n-52'

    assert beams.separate_lines(example1_data) == ['4800, 200000, 437000000', '0, 3000', '-10']
    assert beams.separate_lines(example2_data) == ['8000, 28000, 756e6', '0, 7000', '-52']

def test_extract_data():
    example1_data = ['4800, 200000, 437000000', '0, 3000', '-10']
    example2_data = ['8000, 28000, 756e6', '0, 7000', '-52']

    assert beams.extract_data(example1_data, 2) == ['-10']
    assert beams.extract_data(example2_data, 1) == ['0', '7000']

def test_get_spans():

    assert beams.get_spans(15., 10.) == (10.0, 5.0)
    assert beams.get_spans(10, 7) == (7, 3)

