run: kernels/nh_rex_v100.ti
	python rex_slew_scan.py 2021-300T12:00:00 kernels/*.[bt]*

kernels/nh_rex_v100.ti:
	wget -nv -P kernels naif.jpl.nasa.gov/pub/naif/pds/data/nh-j_p_ss-spice-6-v1.0/nhsp_1000/data/spk/nh_pred_alleph_od151.bsp
	wget -nv -P kernels naif.jpl.nasa.gov/pub/naif/pds/data/nh-j_p_ss-spice-6-v1.0/nhsp_1000/data/lsk/naif0012.tls
	wget -nv -P kernels naif.jpl.nasa.gov/pub/naif/pds/data/nh-j_p_ss-spice-6-v1.0/nhsp_1000/data/sclk/new_horizons_2132.tsc
	wget -nv -P kernels naif.jpl.nasa.gov/pub/naif/pds/data/nh-j_p_ss-spice-6-v1.0/nhsp_1000/data/fk/nh_v220.tf
	wget -nv -P kernels naif.jpl.nasa.gov/pub/naif/pds/data/nh-j_p_ss-spice-6-v1.0/nhsp_1000/data/ik/nh_rex_v100.ti

clean:
	$(RM) -R kernels
