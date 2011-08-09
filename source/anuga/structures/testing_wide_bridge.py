""" Testing CULVERT (Changing from Horizontal Abstraction to Vertical Abstraction

This example includes a Model Topography that shows a TYPICAL Headwall Configuration

The aim is to change the Culvert Routine to Model more precisely the abstraction
from a vertical face.

The inflow must include the impact of Approach velocity.
Similarly the Outflow has MOMENTUM Not just Up welling as in the Horizontal Style
abstraction

"""
print 'Starting.... Importing Modules...'
#------------------------------------------------------------------------------
# Import necessary modules
#------------------------------------------------------------------------------
import anuga

from anuga.abstract_2d_finite_volumes.mesh_factory import rectangular_cross
from anuga.shallow_water.shallow_water_domain import Domain
from anuga.shallow_water.forcing import Rainfall, Inflow
#from anuga.shallow_water.forcing import Reflective_boundary
#from anuga.shallow_water.forcing import Dirichlet_boundary
#from anuga.shallow_water.forcing import Transmissive_boundary, Time_boundary


#from anuga.culvert_flows.culvert_routines import weir_orifice_channel_culvert_model
from math import pi,pow,sqrt

import numpy as num


#------------------------------------------------------------------------------
# Setup computational domain
#------------------------------------------------------------------------------
print 'Setting up domain'

length = 200. #x-Dir
width = 200.  #y-dir

dx = dy = 2.0          # Resolution: Length of subdivisions on both axes
#dx = dy = .5           # Resolution: Length of subdivisions on both axes
#dx = dy = .5           # Resolution: Length of subdivisions on both axes
#dx = dy = .1           # Resolution: Length of subdivisions on both axes

points, vertices, boundary = rectangular_cross(int(length/dx), int(width/dy),
                                                    len1=length, len2=width)
domain = Domain(points, vertices, boundary)   
domain.set_name('Test_WIDE_BRIDGE')                 # Output name
domain.set_default_order(2)
domain.H0 = 0.01
domain.tight_slope_limiters = 1

print 'Size', len(domain)

#------------------------------------------------------------------------------
# Setup initial conditions
#------------------------------------------------------------------------------

def topography(x, y):
    """Set up a weir
    
    A culvert will connect either side
    """
    # General Slope of Topography
    z=10.0-x/100.0  # % Longitudinal Slope
    
    #       NOW Add bits and Pieces to topography
    bank_hgt=10.0
    bridge_width = 50.0
    bank_width = 10.0
    
    us_apron_skew = 1.0 # 1.0 = 1 Length: 1 Width, 2.0 = 2 Length : 1 Width
    us_start_x = 10.0
    top_start_y = 50.0
    us_slope = 3.0  #Horiz : Vertic
    ds_slope = 3.0
    ds_apron_skew = 1.0 # 1.0 = 1 Length: 1 Width, 2.0 = 2 Length : 1 Width
    centre_line_y= top_start_y+bridge_width/2.0

    # CALCULATE PARAMETERS TO FORM THE EMBANKMENT
    us_slope_length = bank_hgt*us_slope
    us_end_x =us_start_x + us_slope_length
    us_toe_start_y =top_start_y - us_slope_length / us_apron_skew
    us_toe_end_y = top_start_y + bridge_width + us_slope_length / us_apron_skew

    top_end_y = top_start_y + bridge_width
    ds_slope_length = bank_hgt*ds_slope
    ds_start_x = us_end_x + bank_width
    ds_end_x = ds_start_x + ds_slope_length

    ds_toe_start_y =top_start_y - ds_slope_length / ds_apron_skew
    ds_toe_end_y = top_start_y + bridge_width + ds_slope_length / ds_apron_skew


    N = len(x)
    for i in range(N):

       # Sloping Embankment Across Channel
        if us_start_x < x[i] < us_end_x +0.1:   # For UPSLOPE on the Upstream FACE
        #if 5.0 < x[i] < 10.1: # For a Range of X, and over a Range of Y based on X adjust Z
            if us_toe_start_y +(x[i] - us_start_x)/us_apron_skew < y[i] < us_toe_end_y - (x[i] - us_start_x)/us_apron_skew:
                #if  49.0+(x[i]-5.0)/5.0 <  y[i]  < 151.0 - (x[i]-5.0)/5.0: # Cut Out Base Segment for Culvert FACE
                 z[i]=z[i] # Flat Apron
                #z[i] += z[i] + (x[i] - us_start_x)/us_slope
                #pass
            else:
               z[i] += z[i] + (x[i] - us_start_x)/us_slope    # Sloping Segment  U/S Face
        if us_end_x < x[i] < ds_start_x + 0.1:
           z[i] +=  z[i]+bank_hgt        # Flat Crest of Embankment
        if ds_start_x < x[i] < ds_end_x: # DOWN SDLOPE Segment on Downstream face
            if  top_start_y-(x[i]-ds_start_x)/ds_apron_skew <  y[i]  < top_end_y + (x[i]-ds_start_x)/ds_apron_skew: # Cut Out Segment for Culvert FACE
                 z[i]=z[i] # Flat Apron
                #z[i] += z[i]+bank_hgt-(x[i] -ds_start_x)/ds_slope
                #pass
            else:
               z[i] += z[i]+bank_hgt-(x[i] -ds_start_x)/ds_slope       # Sloping D/S Face
           
        

    return z

print 'Setting Quantities....'
domain.set_quantity('elevation', topography)  # Use function for elevation
domain.set_quantity('friction', 0.01)         # Constant friction 
domain.set_quantity('stage',
                    expression='elevation')   # Dry initial condition




#------------------------------------------------------------------------------
# Setup specialised forcing terms
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Setup CULVERT INLETS and OUTLETS in Current Topography
#------------------------------------------------------------------------------
print 'DEFINING any Structures if Required'

#  DEFINE CULVERT INLET AND OUTLETS

"""
culvert_rating = Culvert_flow(domain,
    culvert_description_filename='example_rating_curve.csv',
    end_point0=[0.0, 75.0], 
    end_point1=[50.0, 75.0],
    verbose=True)

culvert_energy = Culvert_flow(domain,
    label='Culvert No. 1',
    description='This culvert is a test unit 4m diameter',   
    end_point0=[40.0, 75.0], 
    end_point1=[50.0, 75.0],
    width=4.0,
    culvert_routine=boyd_generalised_culvert_model,  #culvert_routine=weir_orifice_channel_culvert_model,     
    number_of_barrels=1,
    number_of_smoothing_steps=10,
    #update_interval=0.25,
    log_file=True,
    discharge_hydrograph=True,
    use_velocity_head=False,
    use_momentum_jet=False,
    verbose=True)

domain.forcing_terms.append(culvert_energy)
"""
#from anuga.structures.boyd_box_operator import Boyd_box_operator
#culvert0 = Culvert_operator(domain,
#                            end_point0=[40.0, 75.0],
#                            end_point1=[50.0, 75.0],
#                            width=50.0,
#                            depth=10.0,
#                            apron=5.0,
#                            verbose=False)


#------------------------------------------------------------------------------
# Setup culverts
#------------------------------------------------------------------------------
culverts = []
number_of_culverts = 1 
for i in range(number_of_culverts):
    culvert_width = 50.0/number_of_culverts
    y = 100-i*culvert_width - culvert_width/2.0
    ep0 = num.array([40.0, y])
    ep1 = num.array([50.0, y])
    culverts.append(anuga.Boyd_box_operator(domain,
                                            losses=1.5,
                                            width=3.658,
                                            height=3.658,
                                            end_points=[ep0, ep1],
                                            apron=0.5,
                                            manning=0.013,
                                            enquiry_gap=1.0,
                                            description='bridge culvert',
                                            verbose=False))

#culvert2 = Culvert_operator(domain,
#                            end_point0=[40.0, 62.5],
#                            end_point1=[50.0, 62.5],
#                            width=25.0,
#                            depth=10.0,
#                            apron=5.0,
#                            manning=0.013,
#                            verbose=False)



"""
culvert_energy = Culvert_flow(domain,
    label='Culvert No. 1',
    description='This culvert is a test unit 50m Wide by 5m High',   
    end_point0=[40.0, 75.0],
    end_point1=[50.0, 75.0],
    width=50.0,depth=5.0,
    culvert_routine=boyd_generalised_culvert_model,  #culvert_routine=weir_orifice_channel_culvert_model,     
    number_of_barrels=1,
    number_of_smoothing_steps=10,
    #update_interval=0.25,
    log_file=True,
    discharge_hydrograph=True,
    use_velocity_head=False,
    use_momentum_jet=False,
    verbose=True)

domain.forcing_terms.append(culvert_energy)
"""

#------------------------------------------------------------------------------
# Setup boundary conditions
#------------------------------------------------------------------------------
print 'Setting Boundary Conditions'
Br = anuga.Reflective_boundary(domain)              # Solid reflective wall
Bi = anuga.Dirichlet_boundary([0.0, 0.0, 0.0])          # Inflow based on Flow Depth and Approaching Momentum !!!

Bo = anuga.Dirichlet_boundary([-5.0, 0, 0])           # Outflow water at -5.0
Bd = anuga.Dirichlet_boundary([0,0,0])                # Outflow water at 0.0

#Btus = Time_boundary(domain, lambda t: [0.0+ 1.025*(1+num.sin(2*pi*(t-4)/10)), 0.0, 0.0])
#Btds = Time_boundary(domain, lambda t: [0.0+ 0.0075*(1+num.sin(2*pi*(t-4)/20)), 0.0, 0.0])

Btus = anuga.Dirichlet_boundary([20.0, 0, 0])           # Outflow water at 20
Btds = anuga.Dirichlet_boundary([19.0, 0, 0])           # Outflow water at 19
domain.set_boundary({'left': Btus, 'right': Br, 'top': Br, 'bottom': Br})


#------------------------------------------------------------------------------
# Evolve system through time
#------------------------------------------------------------------------------

for t in domain.evolve(yieldstep = 1, finaltime = 100):
    print domain.timestepping_statistics()
    print domain.volumetric_balance_statistics()
    for i, culvert in enumerate(culverts):
        print 'culvert: ', i
        print culvert.statistics()
    

    
"""    
#import sys; sys.exit() 
# Profiling code
import time
t0 = time.time()
   
s = 'for t in domain.evolve(yieldstep = 0.1, finaltime = 300): domain.write_time()'

import profile, pstats
FN = 'profile.dat'

profile.run(s, FN)
    
print 'That took %.2f seconds' %(time.time()-t0)

S = pstats.Stats(FN)
#S.sort_stats('time').print_stats(20)
s = S.sort_stats('cumulative').print_stats(30)

print s
"""
