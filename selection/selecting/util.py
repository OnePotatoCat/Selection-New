import pandas as pd

def start_dew_input(v, tdry, tin, tout):
    ndt	= (tdry-tout)/(tdry-tin)
    ndt2 = ndt**2
    ndt3 = ndt**3
    dt	= tout-tin
    dt2	= dt**2
    dt3	= dt**3
    v_ndt=	v*ndt
    v_ndt2=	v*ndt**2
    v_ndt3=	v*ndt**3
    v_dt= v*dt
    v_dt2= v*dt**2
    v_dt3= v*dt**3

    data = {
        'tdry':[tdry],
        'v':[v],
        'tin':[tin],
        'tout':[tout],
        'ndt':[ndt],
        'ndt2':[ndt2],
        'ndt3':[ndt3],
        'dt':[dt],
        'dt2':[dt2],
        'dt3':[dt3],
        'v_ndt':[v_ndt],
        'v_ndt2':[v_ndt2],
        'v_ndt3':[v_ndt3],
        'v_dt':[v_dt],
        'v_dt2':[v_dt2],
        'v_dt3':[v_dt3]
    }
    return pd.DataFrame(data)


def wet_input(v, tdry, tdew, tin, tout):
    ndt_dry=(tdry-tout)/(tdry-tin)
    ndt_dew=(tdew-tout)/(tdew-tin)
    nndt = ndt_dew/ndt_dry
    vnndt=v*nndt
    vnndt2=v*nndt
    vnndt3=v*nndt*nndt
    v2nndt=v*v*nndt   
    v2nndt2=v*v*nndt*nndt  
    v2nndt3=v*v*nndt*nndt*nndt  
    v3nndt=v*v*v*nndt
    v3nndt2=v*v*v*nndt*nndt
    v3nndt3=v*v*v*nndt*nndt*nndt
    ndt_dry2=ndt_dry*ndt_dry
    ndt_drydew=ndt_dry*ndt_dew
    ndt_dew2=ndt_dew*ndt_dew
    ndt_dry3=ndt_dry*ndt_dry*ndt_dry
    ndt_dry2dew=ndt_dry*ndt_dry*ndt_dew
    ndt_drydew2=ndt_dry*ndt_dew*ndt_dew
    ndt_dew3=ndt_dew*ndt_dew*ndt_dew
    ndt_dry4=ndt_dry*ndt_dry*ndt_dry*ndt_dry
    ndt_dry3dew=ndt_dry*ndt_dry*ndt_dry*ndt_dew
    ndt_dry2dew2=ndt_dry*ndt_dry*ndt_dew*ndt_dew
    ndt_drydew3=ndt_dry*ndt_dew*ndt_dew*ndt_dew
    ndt_dew4=ndt_dew*ndt_dew*ndt_dew*ndt_dew
    vndt_dry=v*ndt_dry
    vndt_dew=v*ndt_dew
    vndt_dry2=v*ndt_dry*ndt_dry
    vndt_drydew=v*ndt_dry*ndt_dew
    vndt_dew2=v*ndt_dew*ndt_dew
    vndt_dry3=v*ndt_dry*ndt_dry*ndt_dry
    vndt_dry2dew=v*ndt_dry*ndt_dry*ndt_dew
    vndt_drydew2=v*ndt_dry*ndt_dew*ndt_dew
    vndt_dew3=v*ndt_dew*ndt_dew*ndt_dew
    vndt_dry4=v*ndt_dry*ndt_dry*ndt_dry*ndt_dry
    vndt_dry3dew=v*ndt_dry*ndt_dry*ndt_dry*ndt_dew
    vndt_dry2dew2=v*ndt_dry*ndt_dry*ndt_dew*ndt_dew
    vndt_drydew3=v*ndt_dry*ndt_dew*ndt_dew*ndt_dew
    vndt_dew4=v*ndt_dew*ndt_dew*ndt_dew*ndt_dew

    data = {   
        'ndt_dry':[ndt_dry],
        'ndt_dew':[ndt_dew],
        'ndt_dry2':[ndt_dry2],
        'ndt_drydew':[ndt_drydew],
        'ndt_dew2':[ndt_dew2],
        'ndt_dry3':[ndt_dry3],
        'ndt_dry2dew':[ndt_dry2dew],
        'ndt_drydew2':[ndt_drydew2],
        'ndt_dew3':[ndt_dew3],
        'vndt_dry':[vndt_dry],
        'vndt_dew':[vndt_dew],
        'vndt_dry2':[vndt_dry2],
        'vndt_drydew':[vndt_drydew],
        'vndt_dew2':[vndt_dew2],
        'vndt_dry3':[vndt_dry3],
        'vndt_dry2dew':[vndt_dry2dew],
        'vndt_drydew2':[vndt_drydew2],
        'vndt_dew3':[vndt_dew3],
        'vndt_dew4':[vndt_dew4],
        'tdew':[tdew],
        'tdry':[tdry],
        'tin':[tin],
        'tout':[tout],
        'v':[v]
    }
    return pd.DataFrame(data)


def dry_input(v, tdry, tin, tout):
    v3 = v*v*v
    ndt=(tdry-tout)/(tdry-tin)
    vndt=v*ndt
    vndt2=v*ndt*ndt
    vndt3=v*ndt*ndt*ndt
    vndt4=v*ndt*ndt*ndt*ndt
    vndt5=v*ndt*ndt*ndt*ndt*ndt
    data ={
        'tdry':[tdry],
        'v':[v],
        'tin':[tin],
        'tout':[tout],
        'v3':[v3],
        'ndt':[ndt],
        'vndt':[vndt],
        'vndt2':[vndt2],
        'vndt3':[vndt3],
        'vndt4':[vndt4],
        'vndt5':[vndt5],
    }
    return pd.DataFrame(data)

def dp_input(mdot):
    data={
        'mdot':[mdot],
        'mdot2':[mdot**2],
    }
    return pd.DataFrame(data)