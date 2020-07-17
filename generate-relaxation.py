# inputs: cif or POSCAR, theory (GGA/ SCAN), list of elements (list same elements with diff charge),
# list of potentials, INCAR file (NUPDOWN not necessary), KPOINTS file, vasp-script file
# outputs: directory with three subdirectories corresponding to relax1, relax2, single point energy, with 
# INCAR, POSCAR, POTCAR, KPOINTS, vasp-script files filled
import sys
import os
import heapq
import tkinter as tk
from tkinter import filedialog
import re
from StaticData import pseudopotentials, d_filling
import IncarTemplate
import Errors

# An object representing an ion. Contains information such as element, charge, and magnetic moment
class Ion:
    def __init__(self, name, system='octahedral', spin='high'):
        self.name = name
        # Extract element using regex
        self.element = re.sub(r'[^a-zA-Z]', '', name)
        self.charge = self.get_charge(self.name)
        self.spin = spin
        self.system = system
        self.magmom = self.get_magmom()
    #get the charge of ion based on name
    def get_charge(self, name):
        # Extract charge using regex
        number = re.sub(r'[^0-9]', '', name)
        try:
            if number != '':
                number = int(number)
            # If no charge specified, asssume it is 0
            else:
                number = 0
            if '+' in name:
                return number
            else:
                return -1*number
        except:
            raise Errors.ChargeError(name)
    def __repr__(self):
        return self.name
    # get the magnetic moment of the ion
    def get_magmom(self):
        try:
            d_electrons = d_filling[self.element]
        except KeyError:
            raise Errors.ElementNotRecognizedError(self.element)
        if d_electrons == 0:
            num_electrons = 0
        else:
            num_electrons = d_electrons - self.charge
        field = CrystalField(self.system, self.spin)
        return field.get_moment(num_electrons)

# An object representing a crystal field, which is specified by an energy level and a spin. 
# Energy levels are represented by an array, with each number representing the number of available 
# positions in each level, starting with the lowest energy level. For example, the octahedral system
# is represented as [3,2], the tetrahdral system as [2,3], and the square planar as [2,1,1,1]
class CrystalField:
    def __init__(self, system, spin):
        self.system = system
        self.spin = spin
        self.energy_levels = self.construct_field(system)
    #construct the energy levels based on the system
    def construct_field(self, system):
        if system == 'octahedral':
            energy_levels = [3, 2]
        elif system == 'tetrahedral':
            energy_levels = [2, 3]
        elif system == 'square planar':
            energy_levels = [2, 1, 1, 1]
        else:
            raise Errors.CrystalGeometryInputError(system)
        return energy_levels
    # Calculate total moment of system given a number of electrons
    def get_moment(self, num_electrons):
        if num_electrons == 0 or num_electrons >= 10:
            return 0
        else:
            charge = num_electrons
            moment = 0
            # case for high spin
            if self.spin == 'high':
                for espin in ['up', 'down']:
                    for level in self.energy_levels:
                        for i in range(level):
                            if espin == 'up':
                                moment += 1
                            elif espin == 'down':
                                moment += -1
                            charge += -1
                            if charge == 0:
                                return moment
            # case for low spin        
            elif self.spin == 'low':
                for level in self.energy_levels:
                    for espin in ['up', 'down']:
                        for i in range(level):
                            if espin == 'up':
                                moment += 1
                            elif espin == 'down':
                                moment += -1
                            charge += -1
                            if charge == 0:
                                return moment
            else:
                raise Errors.SpinInputError(self.spin)
# Description: reads a POSCAR file and outputs data needed to generate correct INCAR and POTCAR files
# Input: a path to the POSCAR file
# Output: a nested list of elements and their multiplicities ordered by their occurence in the POSCAR file
# Eg. [['Na', 8], ['Mn', 8], ['Fe', 4], ['V', 12], ['O', 48]]
def parsePOSCAR(path):
    try:
        f = open(path, 'r')
        # read the first line in POSCAR file
        first_line = f.readline()
        # get the first element; this will be used to detect the lines that give
        # information about elements/ the # of occurences in the structure
        first_elem = re.sub(r'[^a-zA-Z]', '', first_line.split(' ')[0])
        second_elem = re.sub(r'[^a-zA-Z]', '', first_line.split(' ')[1])
        # get information about the order of elements and their # of occurences in the structure
        element_text = ''
        multiplicity_text = ''
        # read each line in the file until the lines containing multiplicity information are found 
        while True:
            text =  f.readline()
            # if the first element pops up, this means we have found the correct line
            if re.search('%s'%(first_elem), text) and re.search('%s'%(second_elem), text):
                element_text = text
                multiplicity_text = f.readline()
                break
            if not text:
                raise Errors.MultiplicitySearchError
        # get element order based on how elements are orderd in the POSCAR file
        element_order = [element for element in element_text.split()]
        print(element_order)
        for element in element_order:
            if not element in d_filling:
                raise Errors.ElementNotRecognizedError(element)
        # get the muliplicities, which is the line underneath the elements line
        element_multiplicity = [int(multiplicity) for multiplicity in multiplicity_text.split()]
        # store both information in a nested list
        element_params = [[order, multiplicity] for order, multiplicity in zip(element_order, element_multiplicity)]
        return element_params
    except Exception as e:
        raise Errors.ParsePoscarError(e)

# Description: Generate a POTCAR file based on the theory and on the POSCAR
def generatePOTCAR(theory, element_order):
    try:
        filenames = []
        # Retrieve the atomic POTCAR file according the element and theory
        # Psuedopotentials used for each element are defined in StaticData.py and can be changed
        for element in element_order:
            pseudopotential = pseudopotentials[element]
            if theory == 'SCAN':
                path = 'POTPAW_PBE_52_SCAN/%s/POTCAR'%(pseudopotential)
            elif theory == 'GGA':
                path = 'POT_GGA_PAW_PBE/%s'%(pseudopotential)
            else:
                raise Errors.TheoryInputError(theory)
            filenames.append(path)
        # Combine all individual pseudopotentials into a POTCAR file
        with open('POTCAR', 'w') as outfile:
            for fname in filenames:
                with open(fname) as infile:
                    outfile.write(infile.read())
        print('\n')
        print('POTCAR file succesfully generated!')
        print('--------------------------------------------------------------------')
    except Exception as e:
        raise Errors.PotcarGenerationError(e)
# Description: Retrieves the order and multiplicity of elements based on the POSCAR file and user inputs
def parseIonData(ions, params, multivalent_params, crystal_params):
    try:     
        # Get the order of elements according to the POSCAR file
        element_order = [param[0] for param in params]

        # Determine all multivalent elements, through both the "ions" and "multivalent_params" input
        multivalent_elements = [Ion(input).element for input in multivalent_params if isinstance(input, str)]
        elements_list = [Ion(name).element for name in ions]
        for duplicate in [element for element in elements_list if elements_list.count(element) > 1]:
            multivalent_elements.append(duplicate)
        
        # Populate ion_list with all ions, their multiplicities, and their orderings
        ion_list = []
        parsed_multivalent = False
        # loop through each ion in the "ions" input
        for name in ions:
            # create an Ion object using the ion name (eg. 'Li+') If crystal parameters are specified, include them
            if name in crystal_params:
                system = crystal_params[crystal_params.index(name)+1]
                spin = crystal_params[crystal_params.index(name)+2]
                ion = Ion(name, system, spin) 
            else:
                ion = Ion(name)
            # if the ion is multivalent, get its multiplicity and order through "ions" and "multivalent_params inputs"
            if name in multivalent_params:
                multiplicity = multivalent_params[multivalent_params.index(name)+1]
                # On passing a multivalent ion for the second time, need to adjust ordering as the POSCAR file
                # does not account for multivalent ordering. The order follows the order of in the "ion" input
                if parsed_multivalent:
                    parsed_multivalent = False
                    order = element_order.index(ion.element) + 0.1
                # On passing a multivalent ion for the first time, ordering is done normally. Multiplicity is set
                # based on the "multivalent_params" input. 
                else:
                    parsed_multivalent = True
                    try:
                        order = element_order.index(ion.element)
                    # Error handling for mising element in POSCAR file
                    except ValueError:
                        raise Errors.ElementMissingError(ion.element)
            # If the ion is not multivalent, use information from the POSCAR file to determine ordering and 
            # multiplicity
            else:
                # Error handling for when an ion that is expected to be multivalent but lack sufficient inputs
                try:
                    multiplicity = params[element_order.index(ion.element)][1]
                # Error handling for mising element in POSCAR file
                except ValueError:
                    raise Errors.ElementMissingError(ion.element)
                if ion.element in multivalent_elements:
                    raise Errors.MultivalentInputError(name)
                # Set the order of the ion according to the POSCAR file
                order = element_order.index(ion.element)
            # Add data including ion, ordering, and multiplicity into a list
            ion_list.append((order, [ion, multiplicity]))
        # Turn the list into a priority queue based on ordering
        heapq.heapify(ion_list)
        ordered_ion_list = []
        # Generate an ordered list based on the priority queue
        while ion_list:
            ordered_ion_list.append(heapq.heappop(ion_list)[1])
        # Print results to console
        print('Extracted multiplicities and order of ions according to inputs and POSCAR file: ')
        print(ordered_ion_list)
        print('--------------------------------------------------------------------')
        # Check that multiplicities match those of POSCAR file
        if sum([param[1] for param in ordered_ion_list]) != sum(param[1] for param in params):
            raise Errors.MultiplicityConflictError
        return(ordered_ion_list)
    except Exception as e:
        raise Errors.ParseIonDataError(e)
# Description: Generates the NUPDOWN input line
def generateMAGMOM(ordered_ion_list):
    string = 'MAGMOM = '
    for [ion, multiplicity] in ordered_ion_list:
        moment = ion.magmom
        if moment == 0:
            moment = 0.6
        moment = str(moment)
        multiplicity = str(multiplicity)
        string += '%s*%s '%(multiplicity, moment)
    return string

# Description: Generates the INCAR file
def generateINCAR(system_name, theory, ordered_ion_list, type):
    try:
        MAGMOM_input = generateMAGMOM(ordered_ion_list)
        NUPDOWN_input = str(sum([ion.magmom*multiplicity for [ion, multiplicity] in ordered_ion_list]))
        print('Calculated magnetic moment inputs for each ion following the order of elements in the POSCAR file:')
        print(MAGMOM_input)
        print('NUPDOWN =', NUPDOWN_input)
        print('--------------------------------------------------------------------')
        if theory == 'SCAN':
            incar_str = IncarTemplate.SCAN_INCAR
        elif theory == 'GGA-dia':
            incar_str = IncarTemplate.GGA_DIA_INCAR
        elif theory == 'GGA-para':
            incar_str = IncarTemplate.GGA_PARA_INCAR
        else:
            raise Errors.TheoryInputError(theory)
        incar_str.replace('<system>', system_name)
        if type == 'relax' or 'relax1':
            incar_str.replace('<ibrion>', '2')
        elif type == 'spe':
            incar_str.replace('<ibrion>', '-1')
    except Exception as e:
        raise Errors.IncarGenerationError(e)


# Main function, runs all tasks
def runTasks(system_name, theory, ions, choose_POSCAR=False, multivalent_params=[], crystal_params=[]):
    # Get path to POSCAR file
    if choose_POSCAR:
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename()
    else:
        path = 'POSCAR'
    params = parsePOSCAR(path)
    # Extract element order from params
    element_order = [param[0] for param in params]
    # Generate the POTCAR file
    generatePOTCAR(theory, element_order)
    # Get a list of ordered ions with their multiplicities
    ordered_ion_list = parseIonData(ions, params, multivalent_params, crystal_params)
    # Generate the INCAR file
    generateINCAR(system_name, theory, ordered_ion_list, type='relax1')


runTasks(
        system_name = 'Na2Mn2Fe(VO4)3',
        theory='SCAN', 
        ions=['O2-', 'Mn2+', 'Mn3+', 'V5+', 'Na+'], 
        choose_POSCAR=False, 
        multivalent_params=['Mn2+', 8, 'Mn3+', 4],
        crystal_params=['Fe2+', 'octahedral', 'high', 'Fe3+', 'octahedral', 'high']
    )



