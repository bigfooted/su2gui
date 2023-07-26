import vtk

# export vtk multiblock mesh to an su2 file
# single block with boundary conditions only
def export_files(multiblock,su2_export_filename):
    print(type(multiblock))
    print("export files:","clicked")
    # export an su2 file
    # first, get the dimensions. If the z-dimension is smaller than 1e-6, we assume 2D


    NDIME = 3
    NELEM = 1
    NPOIN = 1
    NMARK = 1
    MARKER_TAG = "1"
    MARKER_ELEMS = 1
    print("saving su2 mesh file")
    #global mb1
    #print(type(mb1))
    #print(dir(mb1))
    #print("nr of blocks inside block = ",mb1.GetNumberOfBlocks())

    internalBlock = multiblock.GetBlock(0)
    if (internalBlock==None):
        print("no internal block, exiting")
        return

    boundaryBlock = multiblock.GetBlock(1)
    #print("nr of blocks inside internal block = ",internalBlock.GetNumberOfBlocks())
    #print("nr of blocks inside block = ",boundaryBlock.GetNumberOfBlocks())

    print(dir(internalBlock))
    # nr of data in internal block
    NELEM = internalBlock.GetNumberOfCells()
    NPOINT = internalBlock.GetNumberOfPoints()
    BOUND=[0,0,0,0,0,0]
    internalBlock.GetBounds(BOUND)
    dz = BOUND[5] - BOUND[2]
    #print("dz=",dz)
    if (dz<1e-12):
        print("case is 2D")
        NDIME= 2
    else:
        print("dz > 0, case is 3D")

    pts = vtk.vtkIdList()
    for i in range(internalBlock.GetNumberOfBlocks()):
        #print("number of internal elements = ", i+1," / ", internalBlock.GetNumberOfBlocks() )
        data = internalBlock.GetBlock(i)
        celldata = data.GetCells()
        #print("data type=",type(data))
        #print("data type=",dir(data))
        #print("celldata type=",type(celldata))
        #print("celldata type=",dir(celldata))

        for i in range(NELEM):
            #print(i," ",celldata.GetCellSize(i))
            celldata.GetCellAtId(i,pts)
            #print("number of ids = ",pts.GetNumberOfIds())
            #print("cell type =",data.GetCellType(i))
            #for j in range(pts.GetNumberOfIds()):
            #    print(pts.GetId(j))


    for i in range(internalBlock.GetNumberOfBlocks()):
        #print("number of internal elements = ", i+1," / ", internalBlock.GetNumberOfBlocks() )
        data = internalBlock.GetBlock(i)
        #for p in range(NPOINT):
        #    print(p," ",data.GetPoint(p))


    with open(su2_export_filename, 'w') as f:
      # write dimensions
      s = "NDIME= " + str(NDIME) + "\n"
      f.write(s)
      # write element connectivity
      s = "NELEM= " + str(NELEM) + "\n"
      f.write(s)

      # write element connectivity
      for i in range(NELEM):
        s = str(data.GetCellType(i)) + " "
        #print(i," ",celldata.GetCellSize(i))
        celldata.GetCellAtId(i,pts)
        #print("number of ids = ",pts.GetNumberOfIds())
        for j in range(pts.GetNumberOfIds()):
            #print(pts.GetId(j))
            s += str(pts.GetId(j)) + " "
        s += str(i) + "\n"
        f.write(s)

      # write point coordinates
      s = "NPOIN= " + str(NPOINT) + "\n"
      f.write(s)
      for i in range(NPOINT):
          p = data.GetPoint(i)
          if (NDIME==3):
            s = str(p[0]) + " " + str(p[1]) + " " + str(p[2]) + " " + str(i) + "\n"
          else:
            s = str(p[0]) + " " + str(p[1]) + " " + str(i) + "\n"
          f.write(s)
      # write markers
      NMARK = boundaryBlock.GetNumberOfBlocks()
      s = "NMARK= " + str(NMARK) + "\n"
      f.write(s)
      for i in range(NMARK):
        #print("i = ",i," / ",NMARK)
        data = boundaryBlock.GetBlock(i)
        celldata = data.GetCells()
        name = boundaryBlock.GetMetaData(i).Get(vtk.vtkCompositeDataSet.NAME())
        s = "MARKER_TAG= " + str(name) + "\n"
        f.write(s)
        #print("metadata block name = ",name)
        #print(type(data))
        NCELLS = data.GetNumberOfCells()
        #print("Npoints = ", data.GetNumberOfPoints())
        s = "MARKER_ELEMS= " + str(NCELLS)
        for i in range(NCELLS):
            s = str(data.GetCellType(i)) + " "
            celldata.GetCellAtId(i,pts)
            for j in range(pts.GetNumberOfIds()):
              s += str(pts.GetId(j)) + " "
            s += str(i) + "\n"
            f.write(s)