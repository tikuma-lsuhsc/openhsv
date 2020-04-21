from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from skimage.util import pad
import pyqtgraph as pg
from skimage.color import rgb2gray
import numpy as np
from tqdm import tqdm

def _divpad(im, multiple_of=32, cval=0):
    """preprocesses an cropped image for feeding into neural network.
    In most convolutional neural networks, images need to have a specific minimum
    size that it can be processed by the network. In a U-Net-like architecture,
    image dimensions should be a multiple of 32.
    
    :param im: cropped input image (grayscale or RGB)
    :type im: numpy.ndarray
    :param multiple_of: number image dimensions should be a multiple of, defaults to 32
    :type multiple_of: int, optional
    :param cval: value that should be used for padded columns, defaults to 0
    :type cval: int, optional
    :return: padded input image
    :rtype: numpy.ndarray
    """
    needed_padding = []
    real_padding = []

    for sh in im.shape:
        if sh > 3 and sh % multiple_of:
            needed_padding.append(multiple_of - sh % multiple_of)
        else:
            needed_padding.append(0)

    real_padding.append([needed_padding[0] // 2,
                         needed_padding[0] // 2 + needed_padding[0] % 2])

    real_padding.append([needed_padding[1] // 2,
                         needed_padding[1] // 2 + needed_padding[1] % 2])

    return pad(im, real_padding, 'constant', constant_values=cval)

class Analysis(QWidget):
    def __init__(self, app=None):
        """Analysis widget that shows the segmentation process of the neural network.
        
        :param QWidget: Inherits from QWidget
        :type QWidget: PyQt5.QtWidgets.QWidget
        :param app: QApplication, needed to process events to avoid freezing of the GUI, defaults to None
        :type app: PyQt5.QtWidgets.QWidget, optional
        """
        super().__init__()

        self.setWindowTitle("Analysis - Full automatic glottis segmentation")

        self.app = app
        self.model = None
        self.segmentations = []
        self.GAW = []

        self.initUI()
        self.initTensorflow()

    def initUI(self):
        """inits the user interface. In particular, it prepares the preview window for
        the endoscopic image, the segmentation map and the glottal area waveform (GAW).
        """
        self.l = QGridLayout(self)
        self.setGeometry(50, 50, 1800, 600)

        pen = pg.mkPen("y", width=2)

        # Preview Endoscopic image
        self.im = pg.ImageView()
        # Preview segmentation
        self.seg = pg.ImageView()
        # Preview GAW
        self.plt = pg.PlotWidget()
        self.plt.setMaximumWidth(400)
        self.curve = self.plt.plot(pen=pen, symbolBrush=(255, 255, 255), symbolPen="w", symbolSize=8, symbol="o")

        # Set dummy image - needed?!
        self.im.setImage(np.random.randint(0, 100, (200, 200)))
        self.seg.setImage(np.random.randint(0, 100, (200, 200)))

        self.l.addWidget(QLabel("Endoscopy image"), 0, 0, 1, 1)
        self.l.addWidget(QLabel("Segmentation map"), 0, 2, 1, 1)
        self.l.addWidget(QLabel("Glottal area waveform (GAW)"), 0, 4, 1, 1)

        self.l.addWidget(self.im, 1, 0, 1, 1)
        self.l.addWidget(self.seg, 1, 2, 1, 1)
        self.l.addWidget(self.plt, 1, 4, 1, 1)

    def initTensorflow(self):
        """Initializes tensorflow and loads glottis segmentation neural network
        """
        from tensorflow.keras.models import load_model
        self.model = load_model(r"./openhsv/cnn/GlottisSegmentation.h5", compile=False)

    def segmentSequence(self, ims, normalize=True, reinit=True):
        """segments an image sequence, such as a video, frame by frame.
        
        :param ims: collection of images
        :type ims: list of numpy.ndarray, or numpy.ndarray
        :param normalize: normalize 0..255 to -1..1, defaults to True
        :type normalize: bool, optional
        :param reinit: deletes any previous segmentation information, defaults to True
        :type reinit: bool, optional
        """
        if reinit:
            self.GAW = []
            self.segmentations = []

        for im in tqdm(ims):
            if normalize:
                im = im.astype(np.float32) / 127.5 - 1

            # Segment frame
            self.segment(im)

            # Ensure that the GUI is response
            if self.app:
                app.processEvents()

    def segment(self, im):
        """Segments an endoscopic image using a deep neural network

        :param im: np.ndarray (HxWx3)
        :return:
        """
        # Process image to fit the DNN
        processed = _divpad(rgb2gray(im).astype(np.float32))
        # print(processed.min(), processed.max())
        # processed = processed * 2 - 1

        # Run neural network
        pr = self.model.predict(processed[None, ..., None]).squeeze()

        # Save segmentation and GAW
        self.segmentations.append(pr)
        self.GAW.append(pr.sum())

        # Transpose image if RGB
        if im.ndim == 3:
            im = im.transpose((1, 0, 2))

        # Transpose image if grayscale
        elif im.ndim == 2:
            im = im.transpose((1, 0))

        # Show image, show segmentation, show GAW
        self.im.setImage(im)
        self.seg.setImage(pr.transpose((1, 0)))
        self.curve.setData(self.GAW[-40:])

    def get(self):
        """returns GAW and segmentation maps for video
        
        :return: GAW and segmentations
        :rtype: tuple(list, list(numpy.ndarray))
        """
        return dict(gaw=self.GAW, segmentation=self.segmentations)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import imageio as io

    app = QApplication([])
    
    # Load an example video
    vid = io.mimread(r"./openhsv/examples/oscillating_vocal_folds.mp4",
        memtest=False)

    # Create analysis class and show widget
    a = Analysis(app)
    a.show()
    a.segmentSequence(vid)

    app.exec_()