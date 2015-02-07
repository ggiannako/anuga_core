"""Script for running a tsunami inundation scenario for Cairns, QLD Australia.

Source data such as elevation and boundary data is assumed to be available in
directories specified by project.py
The output sww file is stored in directory named after the scenario, i.e
slide or fixed_wave.

The scenario is defined by a triangular mesh created from project.polygon,
the elevation data and a tsunami wave generated by a submarine mass failure.

Geoscience Australia, 2004-present
"""

#------------------------------------------------------------------------------
# Import necessary modules
#------------------------------------------------------------------------------
# Standard modules
import os
import time
import sys

# Related major packages
import anuga

# Application specific imports
import project                 # Definition of file names and polygons

time00 = time.time()
#------------------------------------------------------------------------------
# Preparation of topographic data
# Convert ASC 2 DEM 2 PTS using source data and store result in source data
#------------------------------------------------------------------------------
# Unzip asc from zip file
import zipfile as zf
if project.verbose: print 'Reading ASC from cairns.zip'
zf.ZipFile(project.name_stem+'.zip').extract(project.name_stem+'.asc')

# Create DEM from asc data
anuga.asc2dem(project.name_stem+'.asc', use_cache=project.cache, verbose=project.verbose)

# Create pts file for onshore DEM
anuga.dem2pts(project.name_stem+'.dem', use_cache=project.cache, verbose=project.verbose)

#------------------------------------------------------------------------------
# Create the triangular mesh and domain based on 
# overall clipping polygon with a tagged
# boundary and interior regions as defined in project.py
#------------------------------------------------------------------------------
domain = anuga.create_domain_from_regions(project.bounding_polygon,
                                    boundary_tags={'top': [0],
                                                   'ocean_east': [1],
                                                   'bottom': [2],
                                                   'onshore': [3]},
                                    maximum_triangle_area=project.default_res,
                                    mesh_filename=project.meshname,
                                    interior_regions=project.interior_regions,
                                    use_cache=project.cache,
                                    verbose=project.verbose)

# Print some stats about mesh and domain
print 'Number of triangles = ', len(domain)
print 'The extent is ', domain.get_extent()
print domain.statistics()
                                    
#------------------------------------------------------------------------------
# Setup parameters of computational domain
#------------------------------------------------------------------------------
domain.set_name('cairns_' + project.scenario) # Name of sww file
domain.set_datadir('.')                       # Store sww output here
domain.set_minimum_storable_height(0.01)      # Store only depth > 1cm
domain.set_flow_algorithm('DE0')


                                    
#------------------------------------------------------------------------------
# Setup initial conditions
#------------------------------------------------------------------------------
tide = project.tide
domain.set_quantity('stage', tide)
domain.set_quantity('friction', 0.0)


domain.set_quantity('elevation', 
                    filename=project.name_stem + '.pts',
                    use_cache=project.cache,
                    verbose=project.verbose,
                    alpha=0.1)


time01 = time.time()
print 'That took %.2f seconds to fit data' %(time01-time00)

if project.just_fitting:
    import sys
    sys.exit()

#------------------------------------------------------------------------------
# Setup information for slide scenario (to be applied 1 min into simulation
#------------------------------------------------------------------------------
if project.scenario == 'slide':
    # Function for submarine slide
    tsunami_source = anuga.slide_tsunami(length=35000.0,
                                   depth=project.slide_depth,
                                   slope=6.0,
                                   thickness=500.0, 
                                   x0=project.slide_origin[0], 
                                   y0=project.slide_origin[1], 
                                   alpha=0.0, 
                                   domain=domain,
                                   verbose=project.verbose)

#------------------------------------------------------------------------------
# Setup boundary conditions
#------------------------------------------------------------------------------
print 'Available boundary tags', domain.get_boundary_tags()

Bd = anuga.Dirichlet_boundary([tide, 0, 0]) # Mean water level
Bs = anuga.Transmissive_stage_zero_momentum_boundary(domain) # Neutral boundary

if project.scenario == 'fixed_wave':
    # Huge 50m wave starting after 60 seconds and lasting 1 hour.
    Bw = anuga.Transmissive_n_momentum_zero_t_momentum_set_stage_boundary(
                        domain=domain, 
                        function=lambda t: [(60<t<3660)*10, 0, 0])

    domain.set_boundary({'ocean_east': Bw,
                         'bottom': Bs,
                         'onshore': Bd,
                         'top': Bs})

if project.scenario == 'slide':
    # Boundary conditions for slide scenario
    domain.set_boundary({'ocean_east': Bd,
                         'bottom': Bd,
                         'onshore': Bd,
                         'top': Bd})

#------------------------------------------------------------------------------
# Evolve system through time
#------------------------------------------------------------------------------
import time
t0 = time.time()

from numpy import allclose

if project.scenario == 'slide':
    # Initial run without any event
    for t in domain.evolve(yieldstep=10, finaltime=60): 
        print domain.timestepping_statistics()
        print domain.boundary_statistics(tags='ocean_east')        
        
    # Add slide to water surface
    if allclose(t, 60):
        domain.add_quantity('stage', tsunami_source)    

    # Continue propagating wave
    for t in domain.evolve(yieldstep=10, finaltime=5000, 
                           skip_initial_step=True):
        print domain.timestepping_statistics()
        print domain.boundary_statistics(tags='ocean_east')    

if project.scenario == 'fixed_wave':
    # Save every two mins leading up to wave approaching land
    for t in domain.evolve(yieldstep=2*60, finaltime=5000): 
        print domain.timestepping_statistics()
        print domain.boundary_statistics(tags='ocean_east')    

    # Save every 30 secs as wave starts inundating ashore
    for t in domain.evolve(yieldstep=60*0.5, finaltime=10000, 
                           skip_initial_step=True):
        print domain.timestepping_statistics()
        print domain.boundary_statistics(tags='ocean_east')
            
print 'That took %.2f seconds' %(time.time()-t0)
