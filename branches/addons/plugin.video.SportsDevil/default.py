
# REMOTE DEBUGGING
REMOTE_DBG = False

# append pydev remote debugger
if REMOTE_DBG:
    # Make pydev debugger works for auto reload.
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        import pysrc.pydevd as pydevd
    # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True, suspend=False)
    except ImportError:
        sys.stderr.write("Error: " +
            "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
        sys.exit(1)
    except:
        sys.stderr.write('Remote Debugger is not started')



##if (__name__ == "__main__" ):
##    from lib.main import Main
##    main = Main()
##    main.run()

class Main:
  def __init__(self):
    self.pDialog = None
    self.run()

  def run(self):
    from lib import main
    main.Main()

win = Main()
