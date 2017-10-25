import argparse

import ezdxf
import svgwrite


class AirfoilDat(object):
    def __init__(self):
        self.__surfacepts = []
        self.__chord_mm = None

    @property
    def chord_mm(self):
        self.__chord_mm = self.__chord()
        return self.__chord_mm

    @chord_mm.setter
    def chord_mm(self, chord_mm):
        if chord_mm > 0:
            self.__chord_mm = chord_mm
            pts = self.__surfacepts
            xmin = min( [p[0] for p in pts] )
            xmax = max( [p[0] for p in pts] )
            ymin = min( [p[1] for p in pts] )
            scale_factor = chord_mm / (xmax-xmin)
            print("scale factor={}".format(scale_factor))
            #translate coords such that foil borders xy axes
            pts_translated = [ [p[0]-xmin, p[1]-ymin] for p in pts ]
            pts_scaled = [ [p[0]*scale_factor, p[1]*scale_factor] for p in pts_translated ]
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
#        self.__chord_mm = self.__chord()
#        print("set surfacepts and chord={}".format(self.__chord_mm))


    def __chord(self):
        pts = self.__surfacepts
        xmin = min( [p[0] for p in pts] )
        xmax = max( [p[0] for p in pts] )
        return xmax-xmin



class AirfoilDatReader(object):

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



class AirfoilWriter(object):
    def __init__(self, airfoil):
        self._airfoil = airfoil

    def to_dxf(self, filename):
        #drawing = dxf.drawing(filename)
        drawing = ezdxf.new('AC1015')
        msp = drawing.modelspace()
        msp.add_lwpolyline( self._airfoil.surfacepts, dxfattribs={'closed':True})
#        print("Foil points:{}".format(self._airfoil.surfacepts))
        drawing.saveas(filename)

    def to_svg(self, filename):
        drawing = svgwrite.Drawing(filename)
        drawing.add( drawing.polygon(self._airfoil.surfacepts) )
        drawing.add(drawing.text('chord='+str(self._airfoil.chord_mm), insert=(0,0.2)))
        drawing.save()



'''
CLI
'''
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='convert airfol dat to dxf')
    parser.add_argument('-i', '--input', dest="input_file", help='input dat file', action='store', default="test.dat")
    parser.add_argument('-o', '--output', dest="output_file", help='output dxf file', action='store')
    parser.add_argument('-c', '--chord_mm', dest="chord", type=float, help='dimension of chord', action='store', default=300)
    args = parser.parse_args()


    '''
    TODO: Clean up the filenames and user options to be more clear and flexible
    '''

    if( args.output_file is None ):
        input_file = args.input_file
        output_file_dxf = input_file + ".dxf"
        output_file_svg = input_file + ".svg"
    else:
        output_file_dxf = args.output_file + ".dxf"
        output_file_svg = args.output_file + ".svg"


    afread = AirfoilDatReader()
    foil = afread.load_dat_file(input_file)
    print("rescaling chord to {} mm".format(args.chord))
    foil.chord_mm = args.chord
    afwrite = AirfoilWriter(foil)
    afwrite.to_dxf(output_file_dxf)
    print("Wrote to {}".format(output_file_dxf))
    afwrite.to_svg(output_file_svg)
    print("Wrote to {}".format(output_file_svg))
