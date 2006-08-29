from Numeric import array, Float, zeros
from Scientific.IO.NetCDF import NetCDFFile
from Tkinter import Button, E, W
from visualiser import Visualiser
from vtk import vtkCellArray, vtkPoints, vtkPolyData

class OfflineVisualiser(Visualiser):
    """A VTK-powered offline visualiser which runs in its own thread.
    """
    def __init__(self, source):
        """The source parameter is assumed to be a NetCDF sww file.
        """
        Visualiser.__init__(self, source)

        self.frameNumber = 0
        fin = NetCDFFile(self.source, 'r')
        self.maxFrameNumber = fin.variables['time'].shape[0] - 1
        fin.close()

        self.vtk_heightQuantityCache = []
        for i in range(self.maxFrameNumber):
            self.vtk_heightQuantityCache.append({})

    def setup_grid(self):
        fin = NetCDFFile(self.source, 'r')
        self.vtk_cells = vtkCellArray()
        N_tri = fin.variables['volumes'].shape[0]
        for v in range(N_tri):
            self.vtk_cells.InsertNextCell(3)
            for i in range(3):
                self.vtk_cells.InsertCellPoint(fin.variables['volumes'][v][i])
        fin.close()

    def update_height_quantity(self, quantityName, dynamic=True):
        polydata = self.vtk_polyData[quantityName] = vtkPolyData()
        if dynamic is True:
            if not self.vtk_heightQuantityCache[self.frameNumber].has_key(quantityName):
                self.vtk_heightQuantityCache[self.frameNumber][quantityName]\
                    = self.read_height_quantity(quantityName, True, self.frameNumber);
                print "Caching %s (frame %d)" % (quantityName, self.frameNumber)
            else:
                print "Using cache of %s (frame %d)" % (quantityName, self.frameNumber)
            polydata.SetPoints(self.vtk_heightQuantityCache[self.frameNumber][quantityName])
        else:
            polydata.SetPoints(self.read_height_quantity(quantityName, False))
        polydata.SetPolys(self.vtk_cells)
            
    def read_height_quantity(self, quantityName, dynamic=True, frameNumber=0):
        """Read in a height based quantity from the NetCDF source file
        and return a vtkPoints object. frameNumber is ignored if
        dynamic is false."""
        fin = NetCDFFile(self.source, 'r')
        points = vtkPoints()
        if dynamic is True:
            N_vert = fin.variables[quantityName].shape[1]
        else:
            N_vert = len(fin.variables[quantityName])
        x = array(fin.variables['x'], Float)
        y = array(fin.variables['y'], Float)
        if dynamic is True:
            q = array(fin.variables[quantityName][self.frameNumber], Float)
        else:
            q = array(fin.variables[quantityName], Float)

        q *= self.height_zScales[quantityName]
        q += self.height_offset[quantityName]

        for v in range(N_vert):
            points.InsertNextPoint(x[v], y[v], q[v])
        fin.close()
        return points

    def setup_gui(self):
        Visualiser.setup_gui(self)
        self.tk_renderWidget.grid(row=0, column=0, columnspan=6)
        self.tk_quit.grid(row=2, column=0, columnspan=6, sticky=W+E)
        self.tk_restart = Button(self.tk_root, text="<<<", command=self.restart)
        self.tk_restart.grid(row=1, column=0, sticky=W+E)
        self.tk_back10 = Button(self.tk_root, text="<<", command=self.back10)
        self.tk_back10.grid(row=1, column=1, sticky=W+E)
        self.tk_back = Button(self.tk_root, text="<", command=self.back)
        self.tk_back.grid(row=1, column=2, sticky=W+E)
        self.tk_pauseResume = Button(self.tk_root, text="Pause", command=self.pauseResume)
        self.tk_pauseResume.grid(row=1, column=3, sticky=W+E)
        self.tk_forward = Button(self.tk_root, text=">", command=self.forward)
        self.tk_forward.grid(row=1, column=4, sticky=W+E)
        self.tk_forward10 = Button(self.tk_root, text=">>", command=self.forward10)
        self.tk_forward10.grid(row=1, column=5, sticky=W+E)

    def restart(self):
        self.frameNumber = 0
        self.redraw_quantities(True)

    def back10(self):
        if self.frameNumber - 10 >= 0:
            self.frameNumber -= 10
        else:
            self.frameNumber = 0
        self.redraw_quantities(True)

    def back(self):
        if self.frameNumber > 0:
            self.frameNumber -= 1
            self.redraw_quantities(True)

    def pauseResume(self):
        print "Pause/Resume"

    def forward(self):
        if self.frameNumber < self.maxFrameNumber:
            self.frameNumber += 1
            self.redraw_quantities(True)

    def forward10(self):
        if self.frameNumber + 10 <= self.maxFrameNumber:
            self.frameNumber += 10
        else:
            self.frameNumber = self.maxFrameNumber
        self.redraw_quantities(True)
