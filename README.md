# REX Slew then Scan

## Quick start

### Usage

make run

### Expected typical output

    {
      "Scan_begin": {
        "VB": "[0.005183550983728896, 0.9999865403262471, -0.00022352973394401443]",
        "AP": "[0.9254165783983234, 0.16317591116653482, -0.3420201433256687]",
        "ROLL": "[0.9941461195988329, -0.005177400070845994, -0.10791981938036031]",
        "ROLLREF": "[0.1736481776669304, -0.9848077530122082, 0.0]",
        "VB_at_end": "[0.09605282494208564, 0.4997012579425605, 0.8608556833937191]"
      },
      "Scan_end": {
        "VB": "[0.005183550983728896, 0.9999865403262471, -0.00022352973394401443]",
        "AP": "[0.7544065067354889, 0.133022221559489, 0.6427876096865393]",
        "ROLL": "[0.9941461195988329, -0.005177400070845994, -0.10791981938036031]",
        "ROLLREF": "[0.1736481776669304, -0.9848077530122082, 0.0]",
        "VB_at_beg": "[-0.09086927395835681, 0.5002852823836866, -0.8610792131276634]"
      },
      "Error_checks": {
        "slewerr": 0.0,
        "scanerr": -4.440892098500626e-16,
        "scanbegerr": 2.220446049250313e-16,
        "scanenderr": 2.220446049250313e-16,
        "preslewerr": 2.220446049250313e-16
      },
      "Misc": {
        "Min_Angular_Slew_Axis_SC": "[-0.3977411025789536, 0.00185664867829477, -0.917495813709776]",
        "Min_Angular_Slew_Axis_J2k": "[-0.37315828805084317, 0.23518107614331446, -0.8974646251986964]"
      }
    }

### Modeled behavior

* NH S/C at nominal initial attitude at 2021-300T12:00:00
  * REX boresight (VB) pointed at Earth (Aimpt)
  * S/C +Z (Roll) rolled to NEP (Rollref)
* NH slews to point REX boresight (VB) at initial RA=10deg Dec=-20deg (Aimpt)
  * Select roll to minimum angular magnitude from initial attitude
* NH scans to point REX boresight (VB) at final RA=10deg Dec=+40deg (Aimpt)
  * Select scan axis as cross product of initial and final aimpoints

### TODO

* Add selected UTC to output
* Add options e.g. alternate aimpoints

