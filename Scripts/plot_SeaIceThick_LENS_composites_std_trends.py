"""
Scripts plots sit from LENS future
 
Notes
-----
    Source : http://psc.apl.washington.edu/zhang/IDAO/data_piomas.html
    Author : Zachary Labe
    Date   : 16 November 2016
"""

### Import modules
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as c
import datetime
import read_SeaIceThick_LENS as lens
import statsmodels.api as sm
from mpl_toolkits.basemap import Basemap, addcyclic, shiftgrid
import nclcmaps as ncm
from netCDF4 import Dataset
import scipy.stats as sts

### Define directories
directorydatal = '/surtsey/ypeings/'
directorydatap = '/surtsey/zlabe/seaice_obs/PIOMAS/Thickness/'  
directoryfigure = '/home/zlabe/Desktop/'
#directoryfigure = '/home/zlabe/Documents/Research/SeaIceVariability/Figures/'

### Define time           
now = datetime.datetime.now()
currentmn = str(now.month)
currentdy = str(now.day)
currentyr = str(now.year)
currenttime = currentmn + '_' + currentdy + '_' + currentyr
titletime = currentmn + '/' + currentdy + '/' + currentyr
print '\n' '----LENS/PIOMAS Trends and Sigma - %s----' % titletime 

### Alott time series
yearmin = 1920
yearmax = 2080
years = np.arange(yearmin,yearmax+1,1)
years2 = np.arange(2006,2080+1,1)
months = [r'Jan',r'Feb',r'Mar',r'Apr',r'May',r'Jun',r'Jul',r'Aug',
          r'Sep',r'Oct',r'Nov',r'Dec']
ensemble = ['02','03','04','05','06','07','08','09'] + \
        map(str,np.arange(10,39,1)) + map(str,np.arange(101,106,1))

### Call functions   
sith,lats,lons = lens.readLENSEnsemble(directorydatal,0.15,'historical')
sitf,lats,lons = lens.readLENSEnsemble(directorydatal,0.15,'rcp85')
lons2,lats2 = np.meshgrid(lons,lats)

def readPIOMAS(directorydata,threshold):
    files = 'piomas_regrid_sit_LENS_19792015.nc'
    filename = directorydata + files
    
    data = Dataset(filename)
    sitp = data.variables['sit'][:,:,156:180,:] # lats > 65
    data.close()
    
    ### Mask out threshold values
    if threshold == 'None':
        sitp[np.where(sitp < 0)] = np.nan
        sitp[np.where(sitp > 12)] = np.nan
    else:
        sitp[np.where(sitp < threshold)] = np.nan
        sitp[np.where(sitp < 0)] = np.nan
        sitp[np.where(sitp > 12)] = np.nan
    
    print 'Completed: Read PIOMAS SIT!'
    return sitp
    
sitp = readPIOMAS(directorydatap,0.15)

yearp1 = np.where((years >= 1980) & (years <= 1997))[0]
yearp2 = np.where((years >= 1998) & (years <= 2015))[0]
yearqh1 = np.where((years >= 1920) & (years <= 1962))[0]
yearqh2 = np.where((years >= 1963) & (years <= 2005))[0]
yearqf1 = np.where((years2 >= 2006) & (years2 <= 2042))[0]
yearqf2 = np.where((years2 >= 2043) & (years2 <= 2080))[0]
yearpp = np.where((years >= 1980) & (years <= 2015))[0]

### September 
sith_mo2 = np.nanmean(sith[:,:,9:12,:,:],axis=2)
sitf_mo2 = np.nanmean(sitf[:,:,9:12,:,:],axis=2)
#sitall_mo2 = np.append(sith[:,:,8,:,:],sitf[:,:,8,:,:],axis=1)
sitall_mo3 = np.append(np.nanmean(sith[:,:,9:12,:,:],axis=2),
                       np.nanmean(sitf[:,:,9:12,:,:],axis=2),axis=1)

sith1 = sith_mo2[:,yearqh1,:,:]
sith2 = sith_mo2[:,yearqh2,:,:]
sith3 = sitall_mo3[:,yearp1,:,:]

sitf1 = sitf_mo2[:,yearqf1,:,:]
sitf2 = sitf_mo2[:,yearqf2,:,:]
sitf3 = sitall_mo3[:,yearp2,:,:]

sitpp = sitall_mo3[:,yearpp,:,:]

sitp_mo = np.nanmean(sitp[:,9:12,:,:],axis=1)
sitp1 = sitp_mo[1:19]
sitp2 = sitp_mo[19:37]

def deTrend(y):
    x = np.arange(y.shape[0])
    
    slopes = np.empty((y.shape[1],y.shape[2]))
    intercepts = np.empty((y.shape[1],y.shape[2]))
    for i in xrange(y.shape[1]):
        for j in xrange(y.shape[2]):
            mask = np.isfinite(y[:,i,j])
            yy = y[:,i,j]           
            
            if np.isfinite(np.nanmean(yy)):
                slopes[i,j], intercepts[i,j], r_value, p_value, std_err = sts.linregress(x[mask],yy[mask])
            else:
                slopes[i,j] = np.nan
                intercepts[i,j] = np.nan
    
    y_detrend = np.empty(y.shape)        
    for i in xrange(y.shape[0]):
        y_detrend[i,:,:] = y[i,:,:] - (slopes*x[i] + intercepts)
        print 'Detrended over year %s!' % (i)
     
    print 'Completed: Detrended SIT data!' 
    return y_detrend,slopes
    
dt1,sitptrend1 = deTrend(sitp1)
dt2,sitptrend2 = deTrend(sitp2)
    
sith1dt = np.empty(sith1.shape)
sith2dt = np.empty(sith2.shape)
sith3dt = np.empty(sith3.shape)
sitf1dt = np.empty(sitf1.shape)
sitf2dt = np.empty(sitf2.shape)
sitf3dt = np.empty(sitf3.shape)
sitppdt = np.empty(sitpp.shape)
slopesh1 = np.empty((sith1.shape[0],sith1.shape[2],sith2.shape[3]))
slopesh2 = np.empty((sith1.shape[0],sith1.shape[2],sith2.shape[3]))
slopesh3 = np.empty((sith1.shape[0],sith1.shape[2],sith2.shape[3]))
slopesf1 = np.empty((sith1.shape[0],sith1.shape[2],sith2.shape[3]))
slopesf2 = np.empty((sith1.shape[0],sith1.shape[2],sith2.shape[3]))
slopesf3 = np.empty((sith1.shape[0],sith1.shape[2],sith2.shape[3]))
slopesf3 = np.empty((sith1.shape[0],sith1.shape[2],sith2.shape[3]))
slopesf3 = np.empty((sith1.shape[0],sith1.shape[2],sith2.shape[3]))
slopespp= np.empty((sith1.shape[0],sith1.shape[2],sith2.shape[3]))
for i in xrange(sith.shape[0]):
    sith1dt[i,:,:,:],slopesh1[i] = deTrend(sith1[i])
    sith2dt[i,:,:,:],slopesh2[i] = deTrend(sith2[i])
    sith3dt[i,:,:,:],slopesh3[i] = deTrend(sith3[i])
    sitf1dt[i,:,:,:],slopesf1[i] = deTrend(sitf1[i])
    sitf2dt[i,:,:,:],slopesf2[i] = deTrend(sitf2[i])
    sitf3dt[i,:,:,:],slopesf3[i] = deTrend(sitf3[i])
    sitppdt[i,:,:,:],slopespp[i] = deTrend(sitpp[i])
#    
#compositetrends = [np.nanmean(slopesh1,axis=0),np.nanmean(slopesh2,axis=0),
#                   np.nanmean(slopesh3,axis=0),sitptrend1, 
#                    np.nanmean(slopesf1,axis=0), 
#                    np.nanmean(slopesf2,axis=0), 
#                    np.nanmean(slopesf3,axis=0),sitptrend2]
                    
                    

sith1std = np.empty((sith.shape[0],sith.shape[3],sith.shape[4]))
sith2std = np.empty((sith.shape[0],sith.shape[3],sith.shape[4]))
sith3std = np.empty((sith.shape[0],sith.shape[3],sith.shape[4]))
sitf1std = np.empty((sith.shape[0],sith.shape[3],sith.shape[4]))
sitf2std = np.empty((sith.shape[0],sith.shape[3],sith.shape[4]))
sitf3std = np.empty((sith.shape[0],sith.shape[3],sith.shape[4]))
for i in xrange(sith.shape[0]):
    for j in xrange(sith.shape[3]):
        for k in xrange(sith.shape[4]):
            sith1std[i,j,k] = np.nanstd(sith1dt[i,:,j,k])
            sith2std[i,j,k] = np.nanstd(sith2dt[i,:,j,k])
            sith3std[i,j,k] = np.nanstd(sith3dt[i,:,j,k])
            sitf1std[i,j,k] = np.nanstd(sitf1dt[i,:,j,k])
            sitf2std[i,j,k] = np.nanstd(sitf2dt[i,:,j,k])
            sitf3std[i,j,k] = np.nanstd(sitf3dt[i,:,j,k])
            
sith1std = np.nanmean(sith1std,axis=0)
sith2std = np.nanmean(sith2std,axis=0)
sith3std = np.nanmean(sith3std,axis=0)
sitf1std = np.nanmean(sitf1std,axis=0)
sitf2std = np.nanmean(sitf2std,axis=0)
sitf3std = np.nanmean(sitf3std,axis=0)

composites = [sith1std,sith2std,sith3std,sitf1std,sitf2std,sitf3std]

### Create subplots
plt.rcParams['text.usetex']=True
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Avant Garde'

fig = plt.figure()
    
for i in xrange(len(composites)):
    ax = plt.subplot(2,3,i+1)
    
    ### Select variable
    var = composites[i]
    
    m = Basemap(projection='npstere',boundinglat=66,lon_0=270,
                resolution='l',round =True)
                
    var, lons_cyclic = addcyclic(var, lons)
    var, lons_cyclic = shiftgrid(180., var, lons_cyclic, start=False)
    lon2d, lat2d = np.meshgrid(lons_cyclic, lats)
    x, y = m(lon2d, lat2d)    
      
    m.drawmapboundary(fill_color='white')
    m.drawcoastlines(color='k',linewidth=0.2)
    parallels = np.arange(50,90,10)
    meridians = np.arange(-180,180,30)
#    m.drawparallels(parallels,labels=[False,False,False,False],
#                    linewidth=0.35,color='k',fontsize=1)
#    m.drawmeridians(meridians,labels=[False,False,False,False],
#                    linewidth=0.35,color='k',fontsize=1)
    m.drawlsmask(land_color='darkgrey',ocean_color='mintcream')
    
    ### Adjust maximum limits
    values = np.arange(0,1.1,0.1)  
    
    ### Plot filled contours    
    cs = m.contourf(x,y,var,
                    values,extend='max')
    cs1 = m.contour(x,y,var,
                    values,linewidths=0.2,colors='darkgrey',
                    linestyles='-')
                    
    ### Set colormap  
#    cmap = ncm.cmap('temp_19lev')        
    cs.set_cmap('cubehelix_r') 
    
cbar_ax = fig.add_axes([0.313,0.13,0.4,0.03])                
cbar = fig.colorbar(cs,cax=cbar_ax,orientation='horizontal',
                    extend='max',extendfrac=0.07,drawedges=True)  
                    
cbar.set_ticks(np.arange(0,1.1,0.5))
cbar.set_ticklabels(map(str,np.arange(0,1.1,0.5)))    
cbar.set_label(r'\textbf{std. dev. (meters)}')

plt.subplots_adjust(wspace=-0.28)
plt.subplots_adjust(hspace=0.15)
plt.subplots_adjust(bottom=0.2)
plt.subplots_adjust(top=0.87)
            
plt.annotate(r'\textbf{LENS}', xy=(0, 0), xytext=(0.35, 0.915),
            xycoords='figure fraction',fontsize=20,color='darkgrey',
            rotation=0)
plt.annotate(r'\textbf{LENS}', xy=(0, 0), xytext=(0.680, 0.915),
            xycoords='figure fraction',fontsize=20,color='darkgrey',
            rotation=0)
plt.annotate(r'\textbf{PIOMAS}', xy=(0, 0), xytext=(0.773, 0.892),
            xycoords='figure fraction',fontsize=7,color='darkgrey',
            rotation=0,ha='center')            
            
plt.annotate(r'\textbf{1980-1997}', xy=(0, 0), xytext=(0.79, 0.863),
            xycoords='figure fraction',fontsize=7,color='k',
            rotation=-40)                  
plt.annotate(r'\textbf{1998-2015}', xy=(0, 0), xytext=(0.79, 0.504),
            xycoords='figure fraction',fontsize=7,color='k',
            rotation=-40)

plt.annotate(r'\textbf{1920-1962}', xy=(0, 0), xytext=(0.24, 0.875),
            xycoords='figure fraction',fontsize=7,color='k',
            rotation=0)                               
plt.annotate(r'\textbf{1963-2005}', xy=(0, 0), xytext=(0.468, 0.875),
            xycoords='figure fraction',fontsize=7,color='k',
            rotation=0)
plt.annotate(r'\textbf{2006-2042}', xy=(0, 0), xytext=(0.24, 0.517),
            xycoords='figure fraction',fontsize=7,color='k',
            rotation=0)                     
plt.annotate(r'\textbf{2043-2080}', xy=(0, 0), xytext=(0.468, 0.517),
            xycoords='figure fraction',fontsize=7,color='k',
            rotation=0) 
    
### Save figure
plt.savefig(directoryfigure +'sit_rcp_composites_std_OND.png',dpi=500)

###########################################################################
###########################################################################
###########################################################################
###########################################################################
### Plot Composites
#plt.rc('text',usetex=True)
#plt.rc('font',**{'family':'sans-serif','sans-serif':['Avant Garde']}) 
#
#fig = plt.figure()
#ax = plt.subplot(111)
#
#m = Basemap(projection='npstere',boundinglat=66,lon_0=270,
#            resolution='l',round =True)
#            
#var = np.nanmean(slopespp,axis=0)*10.
#
#var, lons_cyclic = addcyclic(var, lons)
#var, lons_cyclic = shiftgrid(180., var, lons_cyclic, start=False)
#lon2d, lat2d = np.meshgrid(lons_cyclic, lats)
#x, y = m(lon2d, lat2d)    
#
#m.drawmapboundary(fill_color='white')
#m.drawcoastlines(color='k',linewidth=0.3)
#parallels = np.arange(50,90,10)
#meridians = np.arange(-180,180,30)
##m.drawparallels(parallels,labels=[False,False,False,False],
##                linewidth=0.3,color='k',fontsize=6)
##m.drawmeridians(meridians,labels=[False,False,False,False],
##                linewidth=0.3,color='k',fontsize=6)
#m.drawlsmask(land_color='darkgrey',ocean_color='mintcream')
#
## Make the plot continuous
#barlim = np.arange(-0.6,0.7,0.3)
#values = np.arange(-0.6,0.7,0.1)
#
#cs = m.contourf(x,y,var,
#                values,extend='both')
#cs1 = m.contour(x,y,var,
#                values,linewidths=0.2,colors='darkgrey',
#                linestyles='-')
#        
#cmap = ncm.cmap('NCV_blu_red')         
#cs.set_cmap(cmap)
#
#cbar = plt.colorbar(cs,drawedges=True)
#cbar.set_label(r'\textbf{SIT( m decade$^{-1}$ )}')
#cbar.set_ticks(barlim)
#cbar.set_ticklabels(map(str,barlim)) 
#plt.setp(ax.get_xticklabels(),visible=False)
#            
#plt.savefig(directoryfigure + 'LENS_trends.png',dpi=500)

###########################################################################
###########################################################################
###########################################################################
### Plot trends
#fig = plt.figure()
#
#for i in xrange(len(compositetrends)):
#    ax = plt.subplot(2,4,i+1)
#    
#    ### Select variable
#    var = compositetrends[i] * 10. # decadal trend
#    
#    m = Basemap(projection='npstere',boundinglat=66,lon_0=270,
#                resolution='l',round =True)
#                
#    var, lons_cyclic = addcyclic(var, lons)
#    var, lons_cyclic = shiftgrid(180., var, lons_cyclic, start=False)
#    lon2d, lat2d = np.meshgrid(lons_cyclic, lats)
#    x, y = m(lon2d, lat2d)      
#      
#    m.drawmapboundary(fill_color='white')
#    m.drawcoastlines(color='k',linewidth=0.2)
#    parallels = np.arange(50,90,10)
#    meridians = np.arange(-180,180,30)
##    m.drawparallels(parallels,labels=[False,False,False,False],
##                    linewidth=0.35,color='k',fontsize=1)
##    m.drawmeridians(meridians,labels=[False,False,False,False],
##                    linewidth=0.35,color='k',fontsize=1)
#    m.drawlsmask(land_color='darkgrey',ocean_color='mintcream')
#    
#    ### Adjust maximum limits
#    values = np.arange(-0.6,0.7,0.1)  
#    
#    ### Plot filled contours    
#    cs = m.contourf(x,y,var,
#                    values,extend='both')
#    cs1 = m.contour(x,y,var,
#                    values,linewidths=0.2,colors='darkgrey',
#                    linestyles='-')
#                    
#    ### Set colormap  
#    cmap = ncm.cmap('NCV_blu_red')         
#    cs.set_cmap(cmap)                            
#    
#cbar_ax = fig.add_axes([0.313,0.13,0.4,0.03])                
#cbar = fig.colorbar(cs,cax=cbar_ax,orientation='horizontal',
#                    extend='both',extendfrac=0.07,drawedges=True)  
#                    
#cbar.set_ticks(np.arange(-0.6,0.7,0.3))
#cbar.set_ticklabels(map(str,np.arange(-0.6,0.7,0.3)))    
#cbar.set_label('\textbf{SIT( m decade$^{-1}$ )}')
#
#plt.subplots_adjust(hspace=-0.3)
#plt.subplots_adjust(wspace=0.1)
#            
#plt.annotate(r'\textbf{LENS}', xy=(0, 0), xytext=(0.318, 0.87),
#            xycoords='figure fraction',fontsize=20,color='darkgrey',
#            rotation=0,ha='center')
#plt.annotate(r'\textbf{LENS}', xy=(0, 0), xytext=(0.595, 0.87),
#            xycoords='figure fraction',fontsize=20,color='darkgrey',
#            rotation=0,ha='center')
#plt.annotate(r'\textbf{PIOMAS}', xy=(0, 0), xytext=(0.635, 0.847),
#            xycoords='figure fraction',fontsize=7,color='darkgrey',
#            rotation=0,ha='center')
#plt.annotate(r'\textbf{PIOMAS}', xy=(0, 0), xytext=(0.72, 0.87),
#            xycoords='figure fraction',fontsize=20,color='k',
#            rotation=0)
#            
#plt.annotate(r'\textbf{1980-1997}', xy=(0, 0), xytext=(0.845, 0.815),
#            xycoords='figure fraction',fontsize=7,color='k',
#            rotation=-40)
#plt.annotate(r'\textbf{1998-2015}', xy=(0, 0), xytext=(0.845, 0.495),
#            xycoords='figure fraction',fontsize=7,color='k',
#            rotation=-40)
#plt.annotate(r'\textbf{1980-1997}', xy=(0, 0), xytext=(0.645, 0.815),
#            xycoords='figure fraction',fontsize=7,color='k',
#            rotation=-40)                  
#plt.annotate(r'\textbf{1998-2015}', xy=(0, 0), xytext=(0.645, 0.495),
#            xycoords='figure fraction',fontsize=7,color='k',
#            rotation=-40)
#
#plt.annotate(r'\textbf{1920-1962}', xy=(0, 0), xytext=(0.174, 0.815),
#            xycoords='figure fraction',fontsize=7,color='k',
#            rotation=0)                               
#plt.annotate(r'\textbf{1963-2005}', xy=(0, 0), xytext=(0.374, 0.815),
#            xycoords='figure fraction',fontsize=7,color='k',
#            rotation=0)
#plt.annotate(r'\textbf{2006-2042}', xy=(0, 0), xytext=(0.174, 0.495),
#            xycoords='figure fraction',fontsize=7,color='k',
#            rotation=0)                     
#plt.annotate(r'\textbf{2043-2080}', xy=(0, 0), xytext=(0.374, 0.495),
#            xycoords='figure fraction',fontsize=7,color='k',
#            rotation=0)  
#    
#### Save figure
#plt.savefig(directoryfigure +'sit_rcp_composites_trends.png',dpi=500)