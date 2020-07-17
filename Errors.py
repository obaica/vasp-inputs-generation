class PotcarGenerationError(Exception):
    def __init__(self, value):
        self.value = value
        line = '\n\n---------------------------------------------------------------------\n'
        self.message = line + 'POTCAR Generation Failed:\n%s'%(self.value)
        super().__init__(self.message)

class ParsePoscarError(Exception):
    def __init__(self, value):
        self.value = value
        line = '\n\n---------------------------------------------------------------------\n'
        self.message = line + 'POSCAR Parsing Failed:\n%s'%(self.value)
        super().__init__(self.message)

class ParseIonDataError(Exception):
    def __init__(self, value):
        self.value = value
        line = '\n\n---------------------------------------------------------------------\n'
        self.message = line + 'Ion Data Parsing Failed:\n%s'%(self.value)
        super().__init__(self.message)

class IncarGenerationError(Exception):
    def __init__(self, value):
        self.value = value
        line = '\n\n---------------------------------------------------------------------\n'
        self.message = line + 'INCAR Generation Failed:\n%s'%(self.value)
        super().__init__(self.message)

class TheoryInputError(Exception):
    def __init__(self, value):
        self.value = value
        self.message = '"%s" is not a valid input for "theory" - please check your inputs!'%(self.value)
        super().__init__(self.message)

class CrystalGeometryInputError(Exception):
    def __init__(self, value):
        self.value = value
        self.message = '"%s" is not a valid crystal geometry- please check your inputs!'%(self.value)
        super().__init__(self.message)

class ChargeError(Exception):
    def __init__(self, value):
        self.value = value
        self.message = 'Unable to assign a charge to "%s". Please check your inputs!'%(self.value)
        super().__init__(self.message)

class MultiplicitySearchError(Exception):
    def __init__(self):
        self.message = '''Data about atoms and their multiplicity in the structure could not be found, 
please check for errors in your POSCAR file.
'''
        super().__init__(self.message)

class ElementNotRecognizedError(Exception):
    def __init__(self, value):
        self.value = value
        self.message = '"%s" is not a recognized element. Please check your inputs!'%(self.value)
        super().__init__(self.message)

class MultiplicityConflictError(Exception):
    def __init__(self):
        self.message = 'Atom multiplicites do not match. \
Double check that your ion inputs are correct, and that \
inputs for multivalent multiplicities correspond to your POSCAR file.'
        super().__init__(self.message)

class ElementMissingError(Exception):
    def __init__(self, value):
        self.value = value
        self.message =  'Multiplicity data for %s was not found in the POSCAR file. \
Double check your inputs!'%(value)
        super().__init__(self.message)

class MultivalentInputError(Exception):
    def __init__(self, value):
        self.value = value
        self.message =  'Expected %s to have multiplicity specified in "multivalent_params" input \
because it is multivalent. Please double check your inputs.'%(value)
        super().__init__(self.message)

class SpinInputError(Exception):
    def __init__(self, value):
        self.value = value
        self.message = '"%s" is not a recognized spin system. Please check your inputs!'%(self.value)
        super().__init__(self.message)