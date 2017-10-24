import argparse

import ezdxf


class AirfoilDat:
    def __init__(self):
        self.__surfacepts = []
        self.__chord_mm = None

    @property
    def chord_mm(self):
        return self.__chord_mm

    @chord_mm.setter
    def chord_mm(self, chord_mm):
        if chord_mm != None and chord_mm > 0:
            self.__chord_mm = chord_mm
            pts = self.__surfacepts
            xmin = min( [p[0] for p in pts] )
            xmax = min( [p[0] for p in pts] )
            scale_factor = chord_mm / (xmax-xmin)
            pts_scaled = [ [p[0]*scale_factor, p[1]*scale_factor] for p in pts ]
            self.__surfacepts = pts_scaled

    @property
    def surfacepts(self):
        '''
        get surface points, scaled such that the chord is the dimension given in mm
        '''
        return self.__surfacepts

    @surfacepts.setter
    def surfacepts(self, newpts):
        self.__surfacepts = newpts



class AirfoilDatReader:

    def __init__(self):
        pass

    def load_dat_file(self, filename):
        '''
        Returns an object containing Airfoil points
        '''
        afdat = AirfoilDat()

        with open(filename,'r') as fp:
            import re
            numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
            coord_pattern = '\s* ' + numeric_const_pattern + ' \s+ ' + numeric_const_pattern
            rx = re.compile(coord_pattern, re.VERBOSE)
            for line in fp:

                '''
                TODO:  put other dat file specific parsing here
                '''

                if( rx.match(line) ):
                    (x,y) = line.split()
                    afdat.surfacepts.append([float(x),float(y)])

        return afdat




class AirfoilWriter:
    def __init__(self, airfoil):
        self._airfoil = airfoil

    def to_dxf(self, filename):
        #drawing = dxf.drawing(filename)
        drawing = ezdxf.new('AC1015')
        msp = drawing.modelspace()
        msp.add_lwpolyline( self._airfoil.surfacepts, dxfattribs={'closed':True})
        print("Foil points:{}".format(self._airfoil.surfacepts))
        drawing.saveas(filename)



'''
CLI
'''
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='convert airfol dat to dxf')
    parser.add_argument('-i', '--input', dest="input_file", help='input dat file', action='store', default="test.dat")
    parser.add_argument('-o', '--output', dest="output_file", help='output dxf file', action='store')
    args = parser.parse_args()

    if( args.output_file is None ):
        input_file = args.input_file
        output_file = input_file + ".dxf"

    afread = AirfoilDatReader()
    foil = afread.load_dat_file(input_file)
    afwrite = AirfoilWriter(foil)
    afwrite.to_dxf(output_file)
    print("Wrote to {}".format(output_file))
