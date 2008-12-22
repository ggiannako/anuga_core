#!/usr/bin/env python

from culvert_polygons import *

import unittest
import os.path

from Numeric import choose, greater, ones, sin, exp, cosh, allclose
from anuga.utilities.polygon import inside_polygon, polygon_area


class Test_poly(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_1(self):
        
        end_point0=[307138.813,6193474]
        end_point1=[307150.563,6193469]
        width=3 
        height=3
        number_of_barrels=1

        P = create_culvert_polygons(end_point0,
                                end_point1,
                                width=width,   
                                height=height,
                                number_of_barrels=number_of_barrels)
        
        # Compute area and check that it is greater than 0
        for key in ['exchange_polygon0',
                    'exchange_polygon1',
                    'enquiry_polygon0',
                    'enquiry_polygon1']:
            polygon = P[key]
            area = polygon_area(polygon)
            
            msg = 'Polygon %s ' %(polygon)
            msg += ' has area = %f' % area
            assert area > 0.0, msg


    def test_2(self):
        #end_point0=[307138.813,6193474]
        #end_point1=[307150.563,6193469]
        end_point0=[10., 5.]
        end_point1=[10., 10.]     
        width = 1
        height = 3.5 
        number_of_barrels=1

        P = create_culvert_polygons(end_point0,
                                end_point1,
                                width=width,   
                                height=height,
                                number_of_barrels=number_of_barrels)
        
        # Compute area and check that it is greater than 0
        for key in ['exchange_polygon0',
                    'exchange_polygon1',
                    'enquiry_polygon0',
                    'enquiry_polygon1']:
            polygon = P[key]
            area = polygon_area(polygon)
            
            msg = 'Polygon %s ' % (polygon)
            msg += ' has area = %f' % area
            assert area > 0.0, msg
            

    
               
#-------------------------------------------------------------
if __name__ == "__main__":
    suite = unittest.makeSuite(Test_poly, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
        
