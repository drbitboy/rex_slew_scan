"""
Slew REX from Earth to RA,DEC=10,-20
Then scan REX to RA,DEC=10,+40

Usage:  python rex_slew_scan.py {UTC} {kernels} {options}

- {UTC}
  - E.g. 2021-300T12:00:00
  - N.B. must be first
- {kernels} e.g.
  - kernels/naif00012.tls
  - kernels/new-horizons_1234.tsc
  - kernels/nh_abcdef.bsp
  - kernels/nh_v220.tf
  - kernels/nh_rex_v100.ti
- {options}
  - start with --
  - TBD

Setup:

  wget -P kernels naif.jpl.nasa.gov/pub/naif/pds/data/nh-j_p_ss-spice-6-v1.0/nhsp_1000/data/spk/nh_pred_alleph_od151.bsp
  wget -P kernels naif.jpl.nasa.gov/pub/naif/pds/data/nh-j_p_ss-spice-6-v1.0/nhsp_1000/data/lsk/naif0012.tls
  wget -P kernels naif.jpl.nasa.gov/pub/naif/pds/data/nh-j_p_ss-spice-6-v1.0/nhsp_1000/data/sclk/new_horizons_2132.tsc
  wget -P kernels naif.jpl.nasa.gov/pub/naif/pds/data/nh-j_p_ss-spice-6-v1.0/nhsp_1000/data/fk/nh_v220.tf
  wget -P kernels naif.jpl.nasa.gov/pub/naif/pds/data/nh-j_p_ss-spice-6-v1.0/nhsp_1000/data/ik/nh_rex_v100.ti

"""

import os
import sys
import numpy
import pprint
from math import acos
import spiceypy as sp
try   : import simplejson as sj
except: import json as sj

def fourvec(VB,AP,Roll,RollRef):
  """
Return rotation matrix that transforms vector from
- frame of [AimPoint,Roll Reference] vectors, typically J2000 frame,
to
- frame of [Virtual Boresight,Roll] vectors, typically S/C frame,
where
- Virtual Boresight (VB) vector is aligned with AimPoint (AP), and
- Roll vector and Roll Reference vector (RollRef) are in the same
  half-plane that has the VB and AimPoint vectors as its ecge

"""
  return sp.mtxm(sp.twovec(VB,1,Roll,3)
                ,sp.twovec(AP,1,RollRef,3)
                )

if "__main__" == __name__ and sys.argv[1:]:

  ######################################################################
  ### 1) Process command-line arguments
  ### N.B. {options} are ignored for now
  ######################################################################

  UTC = sys.argv[1]
  for kernel in sys.argv[2:]:
    if kernel.startswith('--'): continue     ### Ignore options
    sp.furnsh(kernel)

  ######################################################################
  ### 2) Calculate various "a priori" known input quantities
  ######################################################################

  ### Retrieve REX instrument ID and FOV data from SPICE kernel pool
  rexid = sp.bods2c('NH_REX')
  shape,rex_frame,rexbore,nbounds,bounds = sp.getfov(rexid,99,99)

  ### Convert REX boresight in REX frame (rex_frame = "NH_REX") to its
  ### equivalent vector in NH Spacecraft frame, i.e. virtual boresight
  vvb = sp.mxv(sp.pxform(rex_frame,'NH_SPACECRAFT',0.0),rexbore)

  ### Calculate ET from UTC input argument
  et = sp.utc2et(UTC)

  ### Calculate various vectors
  ### - Z, will be NEP in ecliptic frame, and roll vector in S/C frame
  ### - Pre-slew AimPoint i.e. Earth, J2000 frame
  ### - North Ecliptic Pole, J2000 frame
  ### - Scan begin Aimpoint RA,DEC=10,-20, J2000 frame
  ### - Scan end Aimpoint RA,DEC=10,+40, J2000 frame
  vZ = sp.vpack(0,0,1)
  vearth = sp.vhat(sp.spkezr('earth',et,'j2000','LT','nh')[0][:3])
  vnep = sp.mxv(sp.pxform('ECLIPJ2000','J2000',0.0),vZ)
  vapscanbeg = sp.radrec(1.0,10*sp.rpd(),-20*sp.rpd())
  vapscanend = sp.radrec(1.0,10*sp.rpd(),+40*sp.rpd())

  ######################################################################
  ### 3) Calculate rotation matrices for the seqeuence of frames
  ###    N.B. all matrices rotate vectors from J2000 frame to S/C frame
  ######################################################################

  ### Pre-slew rotation matrix
  ### - VB = REX boresight, (expressed in) S/C frame
  ### - AP = Direction toward earth, J2000 frame
  ### - ROLL = S/C +Z, S/C frame
  ### - ROLLREF = NEP, J2000 frame
  mtx_preslew = fourvec(vvb,vearth,vZ,vnep)

  ### i) Cross product of pre-slew and scan begin aimpoints, would be
  ###      the rotation axis for a minimum angular slew magnitude
  ### ii) Rotate that minimum angular slew axis into the S/C frame
  ###       with S/C oriented in the pre-slew attitude
  minslewaxis_j2k = sp.ucrss(vearth,vapscanbeg)
  minslewaxis_sc = sp.mxv(mtx_preslew,minslewaxis_j2k)

  ### Calculate scan begin rotation matrix
  ### - VB = REX boresight, S/C frame
  ### - AP = Scan begin aimpoint, RA,DEC=10,-20, J2000 frame
  ### - ROLL = minimum angular slew axis, S/C frame
  ### - ROLLREF = minimum angular slew axis, J2000 frame
  mtx_scanbeg = fourvec(vvb,vapscanbeg,minslewaxis_sc,minslewaxis_j2k)

  ### i) Cross product of scan begin and scan end aimpoints, which
  ###      is the rotation axis for the scan
  ### ii) Rotate that scan axis into the S/C frame
  ###       with S/C oriented in the scan begin attitude
  vscanaxis_j2k = sp.ucrss(vapscanbeg,vapscanend)
  vscanaxis_sc = sp.mxv(mtx_scanbeg,vscanaxis_j2k)

  ### Calculate scan end rotation matrix
  ### - VB = REX boresight, S/C frame
  ### - AP = Scan end aimpoint, RA,DEC=10,+40, J2000 frame
  ### - ROLL = minimum angular scan axis, S/C frame
  ### - ROLLREF = minimum angular scan axis, J2000 frame
  mtx_scanend = fourvec(vvb,vapscanend,vscanaxis_sc,vscanaxis_j2k)

  ### For scan begin and scan end attitude aimpoints, calculate VB for
  ### the other end of the scan, since changing VB may be used to
  ### implement the scan
  vvb_at_end = sp.mxv(mtx_scanbeg,vapscanend)
  vvb_at_beg = sp.mxv(mtx_scanend,vapscanbeg)

  ######################################################################
  ### 4) Check results
  ######################################################################

  ### Calculate the differences of the angles between aimpoints and the
  ### angles from scalar of quaternions that convert between frames;
  ### the difference should be very near zero
  slewerr = sp.vsep(vearth,vapscanbeg
            ) - 2.0*acos(sp.m2q(sp.mtxm(mtx_preslew,mtx_scanbeg))[0])
  scanerr = sp.vsep(vapscanbeg,vapscanend
            ) - 2.0*acos(sp.m2q(sp.mtxm(mtx_scanbeg,mtx_scanend))[0])

  ### Calculate the rotation matrix for the scan begin aimpoint and the
  ### vvb_at_beg virtual boresight; it should be near identical to the
  ### scan end matrix.  Do the same for the scan end aimpoint, the
  ### vvb_at_end virtual boresight, and the scan beg matrix; do the same
  ### for the pre-slew aimpoint, the REX virtual boresight, the pre-slew
  ### matrix, and the minimum angular slew axes

  ### - Instantiate a lambda function to calculate the maximum difference
  ###   in magnitude between elements of two matrices
  mtxerr = lambda mtx,vb,ap,roll,rollref: numpy.abs(mtx-fourvec(vb,ap,roll,rollref)).max()

  scanenderr = mtxerr(mtx_scanend,vvb_at_beg,vapscanbeg,vscanaxis_sc,vscanaxis_j2k)
  scanbegerr = mtxerr(mtx_scanbeg,vvb_at_end,vapscanend,vscanaxis_sc,vscanaxis_j2k)
  preslewerr = mtxerr(mtx_preslew,vvb,vearth,minslewaxis_sc,minslewaxis_j2k)

  ######################################################################
  ### 5) Output results
  ######################################################################

  ### Check assumptions:  angles between aimpoints should equal angle
  sj.dump(dict(Scan_begin=dict(VB=vvb
                              ,AP=vapscanbeg
                              ,ROLL=vscanaxis_sc
                              ,ROLLREF=vscanaxis_j2k
                              ,VB_at_end=vvb_at_end
                              )
              ,Scan_end=dict(VB=vvb
                            ,AP=vapscanend
                            ,ROLL=vscanaxis_sc
                            ,ROLLREF=vscanaxis_j2k
                            ,VB_at_beg=vvb_at_beg
                            )
              ,Error_checks=dict(slewerr=slewerr
                                ,scanerr=scanerr
                                ,scanbegerr=scanbegerr
                                ,scanenderr=scanenderr
                                ,preslewerr=preslewerr
                                )
              ,Misc=dict(Min_Angular_Slew_Axis_SC=minslewaxis_sc
                        ,Min_Angular_Slew_Axis_J2k=minslewaxis_j2k
                        )
              )
         ,sys.stdout
         ,indent=2
         ,default=lambda val : str(list(val))
         )
  sys.stdout.write('\n')
########################################################################
