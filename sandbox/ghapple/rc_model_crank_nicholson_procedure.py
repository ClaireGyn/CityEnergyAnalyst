# -*- coding: utf-8 -*-


from __future__ import division
from sandbox.ghapple import rc_model_SIA_with_TABS
from sandbox.ghapple import control_heating_cooling_systems
from cea.demand import airconditioning_model



__author__ = "Gabriel Happle"
__copyright__ = "Copyright 2016, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Gabriel Happle"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "thomas@arch.ethz.ch"
__status__ = "Production"


def calc_rc_model_demand_heating_cooling(bpr, tsd, t, gv):

    # following the procedure in 2.3.2 in SIA 2044 / Korrigenda C1 zum Merkblatt SIA 2044:2011 / Korrigenda C2 zum Mekblatt SIA 2044:2011

    # STEP 1
    # ******
    if not control_heating_cooling_systems.is_active_heating_system(bpr, tsd, t) \
            and not control_heating_cooling_systems.is_active_cooling_system(bpr, tsd, t):

        # calculate temperatures
        rc_model_temperatures = rc_model_SIA_with_TABS.calc_rc_model_temperatures_no_heating_cooling(bpr, tsd, t)

        # write to tsd
        tsd['theta_a'][t] = rc_model_temperatures['theta_a']
        tsd['theta_m'][t] = rc_model_temperatures['theta_m']
        tsd['theta_c'][t] = rc_model_temperatures['theta_c']
        tsd['theta_o'][t] = rc_model_temperatures['theta_o']
        tsd['Qcs'][t] = 0
        tsd['Qcs_em_ls'][t] = 0
        tsd['Qcs_sen'][t] = 0
        tsd['Qcsf'][t] = 0
        tsd['Qcsf_lat'][t] = 0
        tsd['Qhs_lat'][t] = 0
        tsd['Qhs_em_ls'][t] = 0
        tsd['Qhs_lat'][t] = 0
        tsd['Qhs_lat_HVAC'][t] = 0
        tsd['Qhs_sen'][t] = 0
        tsd['Qhs_sen_HVAC'][t] = 0
        tsd['Qhsf'][t] = 0
        tsd['Qhsf_lat'][t] = 0
        #tsd['system_status'][t] = 'systems off'

    elif control_heating_cooling_systems.is_active_heating_system(bpr, tsd, t):
        # case for heating

        # STEP 1
        # ******
        # calculate temperatures with 0 heating power
        rc_model_temperatures_0 = rc_model_SIA_with_TABS.calc_rc_model_temperatures_no_heating_cooling(bpr, tsd, t)

        theta_a_0 = rc_model_temperatures_0['theta_a']

        # STEP 2
        # ******
        # calculate temperatures with 10 W/m2 heating power
        phi_hc_10 = 10 * bpr.rc_model['Af']
        rc_model_temperatures_10 = rc_model_SIA_with_TABS.calc_rc_model_temperatures_heating(phi_hc_10, bpr, tsd, t)

        theta_a_10 = rc_model_temperatures_10['theta_a']

        theta_a_set = tsd['ta_hs_set'][t]

        # interpolate heating power
        # (64) in SIA 2044 / Korrigenda C1 zum Merkblatt SIA 2044:2011 / Korrigenda C2 zum Mekblatt SIA 2044:2011
        phi_hc_ul = phi_hc_10*(theta_a_set - theta_a_0) / (theta_a_10 - theta_a_0)

        # STEP 3
        # ******
        # check if available power is sufficient
        phi_h_max = bpr.hvac['Qhsmax_Wm2'] * bpr.rc_model['Af']

        if 0 < phi_hc_ul <= phi_h_max:
            # case heating with phi_hc_ul
            # calculate temperatures with this power
            phi_h_act = phi_hc_ul

        elif 0 < phi_hc_ul > phi_h_max:
            # case heating with max power available
            # calculate temperatures with this power
            phi_h_act = phi_h_max

        else:
            raise

        # STEP 4
        # ******
        rc_model_temperatures = rc_model_SIA_with_TABS.calc_rc_model_temperatures_heating(phi_h_act, bpr, tsd, t)

        # STEP 5 - latent heat demand of AC systems
        # ******
        if control_heating_cooling_systems.heating_system_is_ac(bpr):
            airconditioning_model.calc_hvac_heating(bpr, tsd, t, gv)

        #elif not control_heating_cooling_systems.heating_system_is_ac(bpr):

        #else:
           # raise ValueError


        # STEP 6 - emission system losses
        # ******


        # set temperatures to tsd for heating
        tsd['theta_a'][t] = rc_model_temperatures['theta_a']
        tsd['theta_m'][t] = rc_model_temperatures['theta_m']
        tsd['theta_c'][t] = rc_model_temperatures['theta_c']
        tsd['theta_o'][t] = rc_model_temperatures['theta_o']
        tsd['Qcs'][t] = 0
        tsd['Qcs_em_ls'][t] = 0
        tsd['Qcs_sen'][t] = 0
        tsd['Qcsf'][t] = 0
        tsd['Qcsf_lat'][t] = 0
        tsd['Qhs_lat'][t] = 0
        tsd['Qhs_em_ls'][t] = 0
        tsd['Qhs_lat'][t] = 0
        tsd['Qhs_lat_HVAC'][t] = 0
        tsd['Qhs_sen'][t] = phi_h_act
        tsd['Qhs_sen_HVAC'][t] = 0
        tsd['Qhsf'][t] = 0
        tsd['Qhsf_lat'][t] = 0
        # TODO: losses

    elif control_heating_cooling_systems.is_active_cooling_system(bpr, tsd, t):

        # case for cooling
        print('COOLING')

        # STEP 1
        # ******
        # calculate temperatures with 0 heating power
        rc_model_temperatures_0 = rc_model_SIA_with_TABS.calc_rc_model_temperatures_no_heating_cooling(bpr, tsd, t)

        theta_a_0 = rc_model_temperatures_0['theta_a']

        # STEP 2
        # ******
        # calculate temperatures with 10 W/m2 cooling power
        phi_hc_10 = 10 * bpr.rc_model['Af']
        rc_model_temperatures_10 = rc_model_SIA_with_TABS.calc_rc_model_temperatures_cooling(phi_hc_10, bpr, tsd, t)

        theta_a_10 = rc_model_temperatures_10['theta_a']

        theta_a_set = tsd['ta_cs_set'][t]

        # interpolate heating power
        # (64) in SIA 2044 / Korrigenda C1 zum Merkblatt SIA 2044:2011 / Korrigenda C2 zum Mekblatt SIA 2044:2011
        phi_hc_ul = phi_hc_10 * (theta_a_set - theta_a_0) / (theta_a_10 - theta_a_0)

        # STEP 3
        # ******
        # check if available power is sufficient
        phi_c_max = -bpr.hvac['Qcsmax_Wm2'] * bpr.rc_model['Af']

        if 0 > phi_hc_ul >= phi_c_max:
            # case heating with phi_hc_ul
            # calculate temperatures with this power
            phi_c_act = phi_hc_ul

        elif 0 > phi_hc_ul < phi_c_max:
            # case heating with max power available
            # calculate temperatures with this power
            phi_h_act = phi_c_max

        else:
            raise

        # STEP 4
        # ******
        rc_model_temperatures = rc_model_SIA_with_TABS.calc_rc_model_temperatures_heating(phi_c_act, bpr, tsd, t)

        # STEP 5 - latent heat demand of AC systems
        # ******
        if control_heating_cooling_systems.cooling_system_is_ac(bpr):
            # write necessary parameters for AC calculation to tsd
            tsd['theta_a'][t] = rc_model_temperatures['theta_a']
            tsd['theta_m'][t] = rc_model_temperatures['theta_m']
            tsd['theta_c'][t] = rc_model_temperatures['theta_c']
            tsd['theta_o'][t] = rc_model_temperatures['theta_o']
            tsd['Qcs_sen'][t] = phi_c_act
            #tsd['system_status'][t] = {'AC cooling'}

            air_con_model_loads_flows_temperatures = airconditioning_model.calc_hvac_cooling(bpr, tsd, t, gv)

            # update temperatures for over cooling case
            if air_con_model_loads_flows_temperatures['q_cs_sen_hvac'] < phi_c_act:
                print('AC over cooling')
                phi_c_act = air_con_model_loads_flows_temperatures['q_cs_sen_hvac']
                rc_model_temperatures = rc_model_SIA_with_TABS.calc_rc_model_temperatures_heating(phi_c_act, bpr, tsd,
                                                                                                  t)
                #tsd['system_status'][t] = 'AC over cooling'

        #elif not control_heating_cooling_systems.heating_system_is_ac(bpr):

        #else:
            #raise ValueError


        # STEP 6 - emission system losses
        # ******
        # q_em_ls_cooling = ses.calc_q_em_ls_cooling(bpr, tsd, hoy)


        # set temperatures to tsd for heating
        tsd['theta_a'][t] = rc_model_temperatures['theta_a']
        tsd['theta_m'][t] = rc_model_temperatures['theta_m']
        tsd['theta_c'][t] = rc_model_temperatures['theta_c']
        tsd['theta_o'][t] = rc_model_temperatures['theta_o']
        tsd['Qcs'][t] = 0
        tsd['Qcs_em_ls'][t] = 0
        tsd['Qcs_sen'][t] = phi_c_act
        tsd['Qcsf'][t] = 0
        tsd['Qcsf_lat'][t] = 0
        tsd['Qhs_lat'][t] = 0
        tsd['Qhs_em_ls'][t] = 0
        tsd['Qhs_lat'][t] = 0
        tsd['Qhs_lat_HVAC'][t] = 0
        tsd['Qhs_sen'][t] = 0
        tsd['Qhs_sen_HVAC'][t] = 0
        tsd['Qhsf'][t] = 0
        tsd['Qhsf_lat'][t] = 0
        # TODO: losses


def update_tsd_no_heating(tsd, t):

    tsd['phi_h_act'][t] = 0


def update_tsd_no_cooling(tsd, t):

    tsd['phi_c_act'][t] = 0