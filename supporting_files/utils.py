import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('utils')

def validate_bids(dirname):
    """ """
    logger.info('Validating BIDS directory')

    cmd = ['/usr/bin/bids-validator', dirname]
    proc = subprocess.Popen(cmd,
                            #cwd=dirname,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    returncode = proc.returncode

    # TODO: Determine if an error should be raised or just a warning
    logger.info('returncode: %d' % returncode)
    logger.info('\n' + stdout)
