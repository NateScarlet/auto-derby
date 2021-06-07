from typing import (
    Any,
    Dict,
    Literal,
    Text,
    Tuple,
    TypeVar,
    Union,
    overload,
    type_check_only,
)

@type_check_only
class PyAssocObject: ...

@type_check_only
class PyCDC(PyAssocObject):
    def AbortDoc(self, *args, **kwargs):
        """ """
        ...
    def Arc(self, *args, **kwargs):
        """ """
        ...
    def BeginPath(self, *args, **kwargs):
        """ """
        ...
    def BitBlt(
        self,
        destPos: Tuple[int, int],
        size: Tuple[int, int],
        dc: PyCDC,
        srcPos: Tuple[int, int],
        rop: int,
    ) -> None:
        """Copies a bitmap from the source device context to this device context.
        MFC References:  CDC::BitBlt

        Args:
            destPos (Tuple[int,int]): The logical x,y coordinates of the upper-left corner of the destination rectangle.
            size (Tuple[int,int]): Specifies the width and height (in logical units) of the destination rectangle and source bitmap.
            dc (PyCDC): Specifies the PyCDC object from which the bitmap will be copied. It must be None if rop specifies a raster operation that does not include a source.
            srcPos (Tuple[int,int]): Specifies the logical x,y coordinates of the upper-left corner of the source bitmap.
            rop (int): Specifies the raster operation to be performed. See the win32 api documentation for details.
        """
        ...
    def Chord(self, *args, **kwargs):
        """ """
        ...
    def CreateCompatibleDC(self, dcFrom: PyCDC = None) -> PyCDC:
        """Creates a memory device context that is compatible with this DC.
        Note that unlike the MFC version, this function calls the global CreateCompatibleDC function and returns a new PyCDC object.
        MFC References: CDC::CreateCompatibleDC

        Args:
            dcFrom (PyCDC, optional): The source DC, or None to make a screen compatible DC. Defaults to None.

        Returns:
            PyCDC: memory device context that is compatible with this DC
        """
        ...
    def CreatePrinterDC(self, *args, **kwargs):
        """ """
        ...
    def DPtoLP(self, *args, **kwargs):
        """ """
        ...
    def DeleteDC(self) -> None:
        """
        Deletes all resources associated with a device context.

        In general, do not call this function; the destructor will do it for you.
        An application should not call DeleteDC if objects have been selected into the device context.
        Objects must first be selected out of the device context before it it is deleted.
        An application must not delete a device context whose handle was obtained by calling CWnd::GetDC.
        Instead, it must call CWnd::ReleaseDC to free the device context.
        The DeleteDC function is generally used to delete device contexts created with CreateDC, CreateIC, or CreateCompatibleDC.
        """
        ...
    def Draw3dRect(self, *args, **kwargs):
        """ """
        ...
    def DrawFocusRect(self, *args, **kwargs):
        """ """
        ...
    def DrawFrameControl(self, *args, **kwargs):
        """ """
        ...
    def DrawIcon(self, *args, **kwargs):
        """ """
        ...
    def DrawText(self, *args, **kwargs):
        """ """
        ...
    def Ellipse(self, *args, **kwargs):
        """ """
        ...
    def EndDoc(self, *args, **kwargs):
        """ """
        ...
    def EndPage(self, *args, **kwargs):
        """ """
        ...
    def EndPath(self, *args, **kwargs):
        """ """
        ...
    def ExtTextOut(self, *args, **kwargs):
        """ """
        ...
    def FillPath(self, *args, **kwargs):
        """ """
        ...
    def FillRect(self, *args, **kwargs):
        """ """
        ...
    def FillSolidRect(self, *args, **kwargs):
        """ """
        ...
    def FrameRect(self, *args, **kwargs):
        """ """
        ...
    def GetBrushOrg(self, *args, **kwargs):
        """ """
        ...
    def GetClipBox(self, *args, **kwargs):
        """ """
        ...
    def GetCurrentPosition(self, *args, **kwargs):
        """ """
        ...
    def GetDeviceCaps(self, *args, **kwargs):
        """ """
        ...
    def GetHandleAttrib(self, *args, **kwargs):
        """ """
        ...
    def GetHandleOutput(self, *args, **kwargs):
        """ """
        ...
    def GetMapMode(self, *args, **kwargs):
        """ """
        ...
    def GetNearestColor(self, *args, **kwargs):
        """ """
        ...
    def GetPixel(self, *args, **kwargs):
        """ """
        ...
    def GetSafeHdc(self) -> int:
        """
        Returns the HDC of this DC object.

        MFC References:  CDC::GetSafeHdc
        """
        ...
    def GetTextExtent(self, *args, **kwargs):
        """ """
        ...
    def GetTextExtentPoint(self, *args, **kwargs):
        """ """
        ...
    def GetTextFace(self, *args, **kwargs):
        """ """
        ...
    def GetTextMetrics(self, *args, **kwargs):
        """ """
        ...
    def GetViewportExt(self, *args, **kwargs):
        """ """
        ...
    def GetViewportOrg(self, *args, **kwargs):
        """ """
        ...
    def GetWindowExt(self, *args, **kwargs):
        """ """
        ...
    def GetWindowOrg(self, *args, **kwargs):
        """ """
        ...
    def IntersectClipRect(self, *args, **kwargs):
        """ """
        ...
    def IsPrinting(self, *args, **kwargs):
        """ """
        ...
    def LPtoDP(self, *args, **kwargs):
        """ """
        ...
    def LineTo(self, *args, **kwargs):
        """ """
        ...
    def MoveTo(self, *args, **kwargs):
        """ """
        ...
    def OffsetViewportOrg(self, *args, **kwargs):
        """ """
        ...
    def OffsetWindowOrg(self, *args, **kwargs):
        """ """
        ...
    def PatBlt(self, *args, **kwargs):
        """ """
        ...
    def Pie(self, *args, **kwargs):
        """ """
        ...
    def PolyBezier(self, *args, **kwargs):
        """ """
        ...
    def Polygon(self, *args, **kwargs):
        """ """
        ...
    def Polyline(self, *args, **kwargs):
        """ """
        ...
    def RealizePalette(self, *args, **kwargs):
        """ """
        ...
    def RectVisible(self, *args, **kwargs):
        """ """
        ...
    def Rectangle(self, *args, **kwargs):
        """ """
        ...
    def RestoreDC(self, *args, **kwargs):
        """ """
        ...
    def SaveDC(self, *args, **kwargs):
        """ """
        ...
    def ScaleViewportExt(self, *args, **kwargs):
        """ """
        ...
    def ScaleWindowExt(self, *args, **kwargs):
        """ """
        ...
    def SelectClipRgn(self, *args, **kwargs):
        """ """
        ...
    def SelectObject(self, ob: T) -> T:
        """
        Selects an object into the device context.
        Currently, only PyCFont, PyCBitMap, PyCBrush and PyCPen objects are supported.
        MFC References: CDC::SelectObject

        Args:
            ob (object): The object to select.

        Returns:
            object: The previously selected object. This will be the same type as the object parameter.
        """
        ...
    def SelectPalette(self, *args, **kwargs):
        """ """
        ...
    def SetBkColor(self, *args, **kwargs):
        """ """
        ...
    def SetBkMode(self, *args, **kwargs):
        """ """
        ...
    def SetBrushOrg(self, *args, **kwargs):
        """ """
        ...
    def SetGraphicsMode(self, *args, **kwargs):
        """ """
        ...
    def SetMapMode(self, *args, **kwargs):
        """ """
        ...
    def SetPixel(self, *args, **kwargs):
        """ """
        ...
    def SetPolyFillMode(self, *args, **kwargs):
        """ """
        ...
    def SetROP2(self, *args, **kwargs):
        """ """
        ...
    def SetTextAlign(self, *args, **kwargs):
        """ """
        ...
    def SetTextColor(self, *args, **kwargs):
        """ """
        ...
    def SetViewportExt(self, *args, **kwargs):
        """ """
        ...
    def SetViewportOrg(self, *args, **kwargs):
        """ """
        ...
    def SetWindowExt(self, *args, **kwargs):
        """ """
        ...
    def SetWindowOrg(self, *args, **kwargs):
        """ """
        ...
    def SetWorldTransform(self, *args, **kwargs):
        """ """
        ...
    def StartDoc(self, *args, **kwargs):
        """ """
        ...
    def StartPage(self, *args, **kwargs):
        """ """
        ...
    def StretchBlt(self, *args, **kwargs):
        """ """
        ...
    def StrokeAndFillPath(self, *args, **kwargs):
        """ """
        ...
    def StrokePath(self, *args, **kwargs):
        """ """
        ...
    def TextOut(self, *args, **kwargs):
        """ """
        ...
    def __delattr__(self, name):
        """
        Implement delattr(self, name).
        """
        ...
    def __getattribute__(self, name):
        """
        Return getattr(self, name).
        """
        ...
    def __repr__(self):
        """
        Return repr(self).
        """
        ...
    def __setattr__(self, name, value):
        """
        Implement setattr(self, name, value).
        """
        ...
    ...

@type_check_only
class GDIObject: ...

@type_check_only
class PyCBitmap(GDIObject):
    def CreateCompatibleBitmap(self, dc: PyCDC, width: int, height: int) -> None:
        """Creates a bitmap compatible with the specified device context.

        Args:
            dc (PyCDC): Specifies the device context.
            width (int): The width (in bits) of the bitmap
            height (int): The height (in bits) of the bitmap.
        """
        ...
    @overload
    def GetBitmapBits(self, asString: Literal[True]) -> Text: ...
    @overload
    def GetBitmapBits(self, asString: Literal[False] = ...) -> Tuple[int, ...]: ...
    @overload
    def GetBitmapBits(self, asString: bool = ...) -> Union[Text, Tuple[int, ...]]:
        """Returns the bitmap bits.

                Args:
                    asString (bool, optional): If False, the result is a tuple of integers, if True, the result is a Python string
        . Defaults to ....
        """
        ...
    def GetHandle(self) -> int:
        """Returns the HBITMAP for a bitmap object"""
        ...
    def GetInfo(self) -> Dict[Text, Any]:
        """Returns the BITMAP structure info

        Returns:
            dict: A dictionary of integers, keyed by the following strings:
                bmType
                bmWidth
                bmHeight
                bmWidthBytes
                bmPlanes
                bmBitsPixel
        """
        ...
    def GetSize(self, *args, **kwargs):
        """ """
        ...
    def LoadBitmap(self, *args, **kwargs):
        """ """
        ...
    def LoadBitmapFile(self, *args, **kwargs):
        """ """
        ...
    def LoadPPMFile(self, *args, **kwargs):
        """ """
        ...
    def Paint(
        self,
        dcObject: PyCDC,
        rectDest: Tuple[int, int, int, int] = ...,
        rectSrc: Tuple[int, int, int, int] = ...,
    ) -> None:
        """Paint a bitmap.

        Args:
            dcObject (PyCDC): The DC object to paint the bitmap to.
            rectDest (Tuple[int,int,int,int], optional): The destination rectangle to paint to. Defaults to (0,0,0,0).
            rectSrc (Tuple[int,int,int,int], optional): The source rectangle to paint from. Defaults to (0,0,0,0).
        """
        ...
    def SaveBitmapFile(self, dcObject: PyCDC, Filename: Text) -> None:
        """Saves a bitmap to a file.

        Args:
            dcObject (PyCDC): The DC object that has rendered the bitmap.
            Filename (Text): The file to save the bitmap to
        """
        ...
    def __delattr__(self, name):
        """
        Implement delattr(self, name).
        """
        ...
    def __getattribute__(self, name):
        """
        Return getattr(self, name).
        """
        ...
    def __repr__(self):
        """
        Return repr(self).
        """
        ...
    def __setattr__(self, name, value):
        """
        Implement setattr(self, name, value).
        """
        ...
    ...

PyRECT = Tuple[int, int, int, int]

T = TypeVar("T")
