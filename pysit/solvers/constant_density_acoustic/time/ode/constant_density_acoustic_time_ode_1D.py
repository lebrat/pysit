import numpy as np
import scipy.sparse as spsp

from pysit.solvers.wavefield_vector import *
from constant_density_acoustic_time_ode_base import *

from pysit.util import Bunch
from pysit.util.derivatives import build_derivative_matrix
from pysit.util.matrix_helpers import build_sigma, make_diag_mtx

__all__=['ConstantDensityAcousticTimeODE_1D']

__docformat__ = "restructuredtext en"
		
class ConstantDensityAcousticTimeODE_1D(ConstantDensityAcousticTimeODEBase):
	
	def __init__(self, mesh, **kwargs):
		
		self.operator_components = Bunch()
		
		ConstantDensityAcousticTimeODEBase.__init__(self, mesh, **kwargs)
		
	def _rebuild_operators(self):
		
		dof = self.mesh.dof(include_bc=True)
		
		oc = self.operator_components
		# Check if empty.  If empty, build the static components
		if not self.operator_components: 
			# build laplacian
			oc.L = build_derivative_matrix(self.mesh, 2, self.spatial_accuracy_order, use_shifted_differences=self.spatial_shifted_differences)
			
			# build sigmaz (stored as -1*sigmaz)
			sz = build_sigma(self.mesh, self.mesh.z)
			oc.minus_sigmaz = make_diag_mtx(-sz)
			
			# build Dz
			oc.Dz = build_derivative_matrix(self.mesh, 1, self.spatial_accuracy_order, dimension='z', use_shifted_differences=self.spatial_shifted_differences)
			
			# build other useful things
			oc.I     = spsp.eye(dof,dof)
			oc.empty = spsp.csr_matrix((dof,dof))
		
		C = self.model_parameters.C
		oc.m_inv = make_diag_mtx((C**2).reshape(-1,))
				
		self.A = spsp.bmat([[oc.empty,              oc.I,            oc.empty       ],
		                    [oc.m_inv*oc.L,         oc.minus_sigmaz, oc.m_inv*oc.Dz ],
		                    [oc.minus_sigmaz*oc.Dz, oc.empty,        oc.minus_sigmaz]])
						
		
	class WavefieldVector(WavefieldVectorBase):
		
		aux_names = ['v', 'Phiz']