import os
import glob

import numpy as np 
import h5py as h5

import arepo
from tqdm import tqdm

def make_projection_snap(path, snapnum, parttype=[0, 2, 3, 4], 
                         center=np.array([200, 200, 200]), width=30., nres=256):

    sn = arepo.Snapshot(path+'/output', snapnum, parttype=parttype, 
                        combineFiles=True, fields=['Coordinates', 'Masses'])

    range_xy = [[center[0] - width/2.0, center[0] + width/2.0], [center[1] - width/2.0, center[1] + width/2.0]]
    range_xz = [[center[0] - width/2.0, center[0] + width/2.0], [center[2] - width/2.0, center[2] + width/2.0]]
    range_yz = [[center[1] - width/2.0, center[1] + width/2.0], [center[2] - width/2.0, center[2] + width/2.0]]

    surf = (width/nres)**(2.0)

    heatmap_xy_out = []
    heatmap_xz_out = []
    heatmap_yz_out = []
    for pt in parttype:
        if sn.NumPart_Total[pt] == 0:
            heatmap_xy_out.append(np.zeros((nres, nres)))
            heatmap_xz_out.append(np.zeros((nres, nres)))
            heatmap_yz_out.append(np.zeros((nres, nres)))
            continue

        part = getattr(sn, 'part'+str(pt))

        x = part.pos[:,0]
        y = part.pos[:,1]
        z = part.pos[:,2]

        xbool = np.logical_and(x > center[0] - width/2.0, x < center[0] + width/2.0)
        ybool = np.logical_and(y > center[1] - width/2.0, y < center[1] + width/2.0)
        zbool = np.logical_and(z > center[2] - width/2.0, z < center[2] + width/2.0)

        keys = np.logical_and(np.logical_and(xbool, ybool), zbool)

        if sn.MassTable[pt] > 0:
            weights = None
            postfac = sn.MassTable[pt] / surf
        else:
            weights = part.Masses[keys] / surf
            postfac = 1.0

        heatmap_xy, _, _ = np.histogram2d(x[keys], y[keys], bins=(nres, nres), range=range_xy, weights=weights)
        heatmap_xz, _, _ = np.histogram2d(x[keys], z[keys], bins=(nres, nres), range=range_xz, weights=weights)
        heatmap_yz, _, _ = np.histogram2d(y[keys], z[keys], bins=(nres, nres), range=range_yz, weights=weights)

        heatmap_xy *= postfac
        heatmap_xz *= postfac
        heatmap_yz *= postfac

        heatmap_xy_out.append(heatmap_xy)
        heatmap_xz_out.append(heatmap_xz)
        heatmap_yz_out.append(heatmap_yz)

    return heatmap_xy_out, heatmap_xz_out, heatmap_xy_out

def construct_update_projection_hdf5(name, path, parttype=[0, 2, 3, 4], center=np.array([200., 200., 200.]),
                                     width=30., nres=256, output_dir='data/'):

    fname = name + '_w' + "{:.01f}".format(width) + '_n' + str(nres) + '.hdf5' 

    f = h5.File(output_dir + '/' + fname, mode='a')

    for pt in parttype:
        if 'PartType' + str(pt) not in f.keys():
            f.create_group('PartType' + str(pt)+'/xy')
            f.create_group('PartType' + str(pt)+'/xz')
            f.create_group('PartType' + str(pt)+'/yz')

    nsnap = len(glob.glob(path+'/output/snapdir*/*.0.hdf5'))
    assert nsnap > 0

    for snap in tqdm(range(nsnap)):
        # check to see if the snapshot is already in the hdf5
        snap_key = 'snapshot_'+"{:03d}".format(snap)
        if snap_key not in f['PartType'+str(parttype[0])+'/xy']:
            
            xy, xz, yz = make_projection_snap(path, snap, parttype=parttype, 
                                              center=center, width=width, nres=nres)

            for i, pt in enumerate(parttype):
                f['PartType'+str(pt)+'/xy'].create_dataset(snap_key, data=xy[i])
                f['PartType'+str(pt)+'/xz'].create_dataset(snap_key, data=xz[i])
                f['PartType'+str(pt)+'/yz'].create_dataset(snap_key, data=yz[i])

    f.close()

if __name__ == '__main__':
    path = '../../runs/fid-dispPoly-fg0.1/lvl5'
    name = 'fid-dispPoly-fg0.1-lvl5'

    construct_update_projection_hdf5(name, path)