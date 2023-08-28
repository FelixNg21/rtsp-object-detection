import argparse
class Arguments:
    """
    Class to handle the arguments for the detect module
    The attributes are:
        - input: path to input image
        - outputfile: filename for output video
        - outputdir: path to output folder
        - framestart: start frame
        - framelimit: number of frames to process (0 = all)
        - config: path to yolo config file
        - weights: path to yolo pre-trained weights
        - classes: path to text file containing class names
        - invertcolor: flag to invert RGB 2 BGR
        - fpsthrottle: frames to skip in order to catch up to the stream for slow machines (1 = no throttle)
        - saveimages: flag to save cropped object images for training
    """
    def __init__(self):
        self.input = None
        self.outputfile = None
        self.outputdir = None
        self.framestart = None
        self.framelimit = None
        self.config = None
        self.weights = None
        self.classes = None
        self.invertcolor = None
        self.fpsthrottle = None
        self.saveimages = None


def arg_parse():
    """
    Parse arguements to the detect module
    """
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input', required=False,
                    help='path to input image', default='sampledata')
    ap.add_argument('-o', '--outputfile', required=False,
                    help='filename for output video', default='output.mp4')
    ap.add_argument('-od', '--outputdir', required=False,
                    help='path to output folder', default='output')
    ap.add_argument('-fs', '--framestart', required=False, type=check_positive,
                    help='start frame', default=0)
    ap.add_argument('-fl', '--framelimit', required=False, type=check_positive,
                    help='number of frames to process (0 = all)', default=0)
    ap.add_argument('-c', '--config', required=False,
                    help='path to yolo config file', default='cfg/yolov3-tiny.cfg')
    ap.add_argument('-w', '--weights', required=False,
                    help='path to yolo pre-trained weights', default='yolov3-tiny.weights')
    ap.add_argument('-cl', '--classes', required=False,
                    help='path to text file containing class names', default='cfg/yolov3.txt')
    ap.add_argument('-ic', '--invertcolor', required=False, action='store_false',
                    help='pass the flag to invert RGB 2 BGR')
    ap.add_argument('-fpt', '--fpsthrottle', required=False,
                    help='skips (int) x frames in order to catch up with the stream for slow machines 1 = no throttle',
                    default=1)
    ap.add_argument('-si', '--saveimages', required=False, action='store_true',
                    help='pass the flag to save cropped object images for training')

    try:
        args = ap.parse_args()
        arguments = Arguments()
        arguments.input = args.input
        arguments.outputfile = args.outputfile
        arguments.outputdir = args.outputdir
        arguments.framestart = args.framestart
        arguments.framelimit = args.framelimit
        arguments.config = args.config
        arguments.weights = args.weights
        arguments.classes = args.classes
        arguments.invertcolor = args.invertcolor
        arguments.fpsthrottle = args.fpsthrottle
        arguments.saveimages = args.saveimages
        return arguments
    except Exception as e:
        print(e)
        ap.print_help()
        quit()

def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue
