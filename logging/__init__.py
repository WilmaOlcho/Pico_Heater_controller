import utime
import sys
import uio
from machine import ADC

CRITICAL = 50
ERROR    = 40
WARNING  = 30
INFO     = 20
DEBUG    = 10
NOTSET   = 0

_level_dict = {
    CRITICAL: "CRITICAL",
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    DEBUG: "DEBUG",
}


class Logger:

    level = NOTSET

    def __init__(self, name):
        self.name = name
        self.handlers = None

    def _level_str(self, level):
        l = _level_dict.get(level)
        if l is not None:
            return l
        return "LVL%s" % level

    def setLevel(self, level):
        self.level = level

    def isEnabledFor(self, level):
        return level >= (self.level or _level)

    def log(self, level, msg, *args, **kwargs):
        if level >= (self.level or _level):
            record = LogRecord(
                self.name, level, None, None, msg, args, None, None, None, kwargs.pop("cputemp", None)
            )

            if self.handlers:
                for hdlr in self.handlers:
                    hdlr.emit(record)

    def debug(self, msg, *args, **kwargs):
        self.log(DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.log(INFO, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.log(WARNING, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.log(ERROR, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.log(CRITICAL, msg, *args, **kwargs)

    def exc(self, e, msg, *args, **kwargs):
        buf = uio.StringIO()
        sys.print_exception(e, buf)
        self.log(ERROR, msg + "\n" + buf.getvalue(), *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.exc(sys.exc_info()[1], msg, *args, **kwargs)

    def addHandler(self, hdlr):
        if self.handlers is None:
            self.handlers = []
        self.handlers.append(hdlr)


_level = INFO
_loggers = {}


def getLogger(name=None):
    if name is None:
        name = "root"
    if name in _loggers:
        return _loggers[name]
    if name == "root":
        l = Logger(name)
        sh = StreamHandler()
        sh.formatter = Formatter()
        l.addHandler(sh)
    else:
        l = Logger(name)
    _loggers[name] = l
    return l

def info(msg, *args):
    getLogger(None).info(msg, *args)

def debug(msg, *args):
    getLogger(None).debug(msg, *args)

def basicConfig(level=INFO, filename=None, stream=None, format=None, style="%"):
    global _level
    _level = level
    if filename:
        h = FileHandler(filename)
    else:
        h = StreamHandler(stream)
    h.setFormatter(Formatter(format, style=style))
    root.handlers.clear()
    root.addHandler(h)


class Handler:
    def __init__(self):
        self.formatter = Formatter()

    def setFormatter(self, fmt):
        self.formatter = fmt


class StreamHandler(Handler):
    def __init__(self, stream=None):
        self._stream = stream or sys.stderr
        self.terminator = "\n"
        self.formatter = Formatter()

    def emit(self, record):
        self._stream.write(self.formatter.format(record) + self.terminator)

    def flush(self):
        pass


class FileHandler(Handler):
    def __init__(self, filename, mode="a", encoding=None, delay=False):
        super().__init__()

        self.encoding = encoding
        self.mode = mode
        self.delay = delay
        self.terminator = "\n"
        self.filename = filename

        self._f = None
        if not delay:
            self._f = open(self.filename, self.mode)

    def emit(self, record):
        with open(self.filename, self.mode) as f:
            f.write(self.formatter.format(record) + self.terminator)

    def close(self):
        if self._f is not None:
            self._f.close()


class Formatter:

    converter = utime.localtime

    def __init__(self, fmt=None, datefmt=None, style="%"):
        self.fmt = fmt or "%(message)s"
        self.datefmt = datefmt

        if style not in ("%", "{"):
            raise ValueError("Style must be one of: %, {")

        self.style = style

    def usesTime(self):
        if self.style == "%":
            return "%(asctime)" in self.fmt
        elif self.style == "{":
            return "{asctime" in self.fmt
        
    def usesCpuTemp(self):
        if self.style == "%":
            return "%(cputemp)" in self.fmt
        elif self.style == "{":
            return "{cputemp" in self.fmt

    def format(self, record):
        # The message attribute of the record is computed using msg % args.
        record.message = record.msg % record.args

        # If the formatting string contains '(asctime)', formatTime() is called to
        # format the event time.
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        if self.usesCpuTemp():
            record.cputemp = self.formatCpuTemp(record)

        # If there is exception information, it is formatted using formatException()
        # and appended to the message. The formatted exception information is cached
        # in attribute exc_text.
        if record.exc_info is not None:
            record.exc_text += self.formatException(record.exc_info)
            record.message += "\n" + record.exc_text

        # The record’s attribute dictionary is used as the operand to a string
        # formatting operation.
        if self.style == "%":
            return self.fmt % record.__dict__
        elif self.style == "{":
            return self.fmt.format(**record.__dict__)
        else:
            raise ValueError(
                "Style {0} is not supported by logging.".format(self.style)
            )

    def formatTime(self, record, datefmt=None):
        assert datefmt is None  # datefmt is not supported
        ct = utime.localtime(record.created)
        return "{0}-{1}-{2} {3}:{4}:{5}".format(*ct)
    
    def formatCpuTemp(self, record):
        chip_temp = ADC(4)
        conversion_factor = 3.3 / (65535)
        reading = chip_temp.read_u16() * conversion_factor 
        cputemp = 27.0 - (reading - 0.706)/0.001721
        return cputemp

    def formatException(self, exc_info):
        raise NotImplementedError()

    def formatStack(self, stack_info):
        raise NotImplementedError()


root = getLogger()


class LogRecord:
    def __init__(
        self, name, level, pathname, lineno, msg, args, exc_info, func=None, sinfo=None, cputemp=0
    ):
        ct = utime.time()
        self.created = ct
        self.msecs = (ct - int(ct)) * 1000
        self.name = name
        self.levelno = level
        self.levelname = _level_dict.get(level, None)
        self.pathname = pathname
        self.lineno = lineno
        self.msg = msg
        self.args = args
        self.exc_info = exc_info
        self.func = func
        self.sinfo = sinfo
        self.cputemp = cputemp

class printstream:
    @classmethod
    def write(cls, s):
        print(s, end='')