import logging
import logging.config
from GlobalConfig import InitConfig,GetConfig
import numpy as np
import scipy.linalg as la
    
MY_ID = 'SparseBayes'

class SparseBayes(object):
    def __init__(self):
        old_settings = np.seterr(all='warn',divide='raise',invalid='raise')
#        InitConfig()
        self.config = GetConfig()
#        self.config.read(['LGus.conf'])
        logging.config.fileConfig('logging.conf')
        self.appLogger = logging.getLogger('Learning')
        if id(np.dot) == id(np.core.multiarray.dot):
            self.appLogger.info("Not using blas/lapack!")
        self.config = GetConfig()
        self.GAUSSIAN_SNR_INIT = self.config.getfloat(MY_ID,'GAUSSIAN_SNR_INIT')
        self.INIT_ALPHA_MAX = self.config.getfloat(MY_ID,'INIT_ALPHA_MAX')
        self.INIT_ALPHA_MIN = self.config.getfloat(MY_ID,'INIT_ALPHA_MIN')
        self.ALIGNMENT_ZERO = self.config.getfloat(MY_ID,'ALIGNMENT_ZERO')
        self.CONTROL_ZeroFactor = self.config.getfloat(MY_ID,'CONTROL_ZeroFactor')
        self.CONTROL_MinDeltaLogAlpha = self.config.getfloat(MY_ID,'CONTROL_MinDeltaLogAlpha')
        self.CONTROL_MinDeltaLogBeta = self.config.getfloat(MY_ID,'CONTROL_MinDeltaLogBeta')
        self.CONTROL_PriorityAddition = self.config.getboolean(MY_ID,'CONTROL_PriorityAddition')
        self.CONTROL_PriorityDeletion = self.config.getboolean(MY_ID,'CONTROL_PriorityDeletion')
        self.CONTROL_BetaUpdateStart = self.config.getint(MY_ID,'CONTROL_BetaUpdateStart')
        self.CONTROL_BetaUpdateFrequency = self.config.getint(MY_ID,'CONTROL_BetaUpdateFrequency')
        self.CONTROL_BetaMaxFactor = self.config.getfloat(MY_ID,'CONTROL_BetaMaxFactor')
        self.CONTROL_PosteriorModeFrequency = self.config.getint(MY_ID,'CONTROL_PosteriorModeFrequency')
        self.CONTROL_BasisAlignmentTest = self.config.getboolean(MY_ID,'CONTROL_BasisAlignmentTest')
        self.CONTROL_AlignmentMax = 1 - self.ALIGNMENT_ZERO
        self.CONTROL_BasisFunctionMax = self.config.getint(MY_ID,'CONTROL_BasisFunctionMax')
        self.OPTIONS_iteration = self.config.getint(MY_ID,'OPTIONS_iteration')
        self.OPTIONS_monitor = self.config.getint(MY_ID,'OPTIONS_monitor')
        self.SETTING_noiseStdDev = self.config.getfloat(MY_ID,'SETTING_noiseStdDev')
        self.ACTION_REESTIMATE = self.config.getint(MY_ID,'ACTION_REESTIMATE')
        self.ACTION_ADD = self.config.getint(MY_ID,'ACTION_ADD')
        self.ACTION_DELETE = self.config.getint(MY_ID,'ACTION_DELETE')
        self.ACTION_TERMINATE = self.config.getint(MY_ID,'ACTION_TERMINATE')
        self.ACTION_NOISE_ONLY = self.config.getint(MY_ID,'ACTION_NOISE_ONLY')
        self.ACTION_ALIGNMENT_SKIP = self.config.getint(MY_ID,'ACTION_ALIGNMENT_SKIP')

    def preprocess(self,BASIS):
#        self.appLogger.debug('preprocess')
        try:
            N,M = BASIS.shape
        except:
            self.appLogger.error('Error BASIS:\n %s'%str(BASIS))
#            print 'Error BASIS:\n %s'%str(BASIS)
            raise RuntimeError      
        Scales = np.atleast_2d(np.sqrt(np.sum((BASIS**2),axis=0))).T
        Scales[Scales==0] = 1
        
        for m in range(M):
            BASIS[:,m] = BASIS[:,m]/Scales[m]
            
        return BASIS,Scales
    
    def initialize(self,BASIS,Targets):
#        self.appLogger.debug('initialize')
        # preprocess
        BASIS,Scales = self.preprocess(BASIS)
        
        # beta
#        self.appLogger.debug('beta')
        if True:
            beta = 1/self.SETTING_noiseStdDev**2
        else:
            stdt = max([1e-6,np.std(Targets)])
            beta = 1/(stdt*self.GAUSSIAN_SNR_INIT)**2
#        self.appLogger.debug('beta %s'%str(beta))
            
        
        # PHI
#        self.appLogger.debug('PHI')
        proj = np.dot(BASIS.T,Targets)
#        self.appLogger.debug('proj %s'%str(proj))
        Used = np.array([np.argmax(np.abs(proj))])
#        self.appLogger.debug('Used %s'%str(Used))
        PHI = BASIS[:,Used]
#        self.appLogger.debug('PHI %s'%str(PHI))
        N,M = PHI.shape

        # Mu
#        self.appLogger.debug('Mu')
        Mu = np.array([])
#        self.appLogger.debug('Mu %s'%str(Mu))
        
        # hyperparameters: Alpha
#        self.appLogger.debug('Alpha')
        s = np.diag(np.dot(PHI.T,PHI))*beta
#        self.appLogger.debug('s %s'%str(s))
        q = np.dot(PHI.T,Targets)*beta
#        self.appLogger.debug('q %s'%str(q))
        Alpha = s**2/(q**2-s)
#        self.appLogger.debug('Alpha %s'%str(Alpha))
        Alpha[Alpha<0] = self.INIT_ALPHA_MAX
#        self.appLogger.debug('Alpha %s'%str(Alpha))
        if M == 1:
            self.appLogger.info('Initial alpha = %g'%Alpha)
            
        return BASIS,Scales,Alpha,beta,Mu,PHI,Used
    
    def full_statistics(self,BASIS,PHI,Targets,Used,Alpha,beta,BASIS_PHI,BASIS_Targets):
#        self.appLogger.debug('full_statistics')

        MAX_POSTMODE_ITS = 25
        try:
            N,M_full = BASIS.shape
        except ValueError:
            M_full = 1
        try:
            n,M = PHI.shape
        except ValueError:
            M = 1

#        self.appLogger.debug('BASIS %s'%str(BASIS))
#        self.appLogger.debug('PHI %s'%str(PHI))
#        self.appLogger.debug('Targets %s'%str(Targets))
#        self.appLogger.debug('Used %s'%str(Used))
#        self.appLogger.debug('Alpha %s'%str(Alpha))
#        self.appLogger.debug('beta %s'%str(beta))
#        self.appLogger.debug('BASIS_PHI %s'%str(BASIS_PHI))
#        self.appLogger.debug('BASIS_Targets %s'%str(BASIS_Targets))

    
        # posterior
#        self.appLogger.debug('posterior')
        U = la.cholesky(np.dot(PHI.T,PHI)*beta+np.diag(Alpha.ravel(),k=0))
#        self.appLogger.debug('U %s'%str(U))
        Ui = la.inv(U)
#        self.appLogger.debug('Ui %s'%str(Ui))
        SIGMA = np.dot(Ui,Ui.T)
#        self.appLogger.debug('SIGMA %s'%str(SIGMA))
        
        Mu = np.dot(SIGMA,np.dot(PHI.T,Targets))*beta
#        self.appLogger.debug('Mu %s'%str(Mu))
        
        y = np.dot(PHI,Mu)
#        self.appLogger.debug('y %s'%str(y))
        e = Targets - y
#        self.appLogger.debug('e %s'%str(e))
        ED = np.dot(e.T,e)
#        self.appLogger.debug('ED %s'%str(ED))
        
        dataLikely = (N*np.log(beta) - beta*ED)/2
#        self.appLogger.debug('dataLikely %s'%str(dataLikely))
        
        # log marginal likelihood
#        self.appLogger.debug('log marginal likelihood')
#        logdetHOver2 = np.atleast_2d(np.sum(np.log(np.diag(U)))).T
        logdetHOver2 = np.sum(np.log(np.diag(U)))
#        self.appLogger.debug('logdetHOver2 %s'%str(logdetHOver2))
        logML = dataLikely - np.dot((Mu**2).T,Alpha)/2 + np.sum(np.log(Alpha))/2 - logdetHOver2
#        self.appLogger.debug('logML %s'%str(logML))
        
        # well-determinedness factors
#        self.appLogger.debug('well-determinedness factors')
        DiagC = np.atleast_2d(np.sum(Ui**2,1)).T
#        self.appLogger.debug('DiagC %s'%str(DiagC))
        Gamma = 1 - Alpha * DiagC #TBA
#        self.appLogger.debug('Gamma %s'%str(Gamma))
        
        # Q & S
#        self.appLogger.debug('Q & S')
        betaBASIS_PHI = beta*BASIS_PHI
#        self.appLogger.debug('betaBASIS_PHI %s'%str(betaBASIS_PHI))
#        self.appLogger.debug('np.dot(betaBASIS_PHI,Ui)**2 %s'%str(np.dot(betaBASIS_PHI,Ui)**2))
#        self.appLogger.debug('np.sum(np.dot(betaBASIS_PHI,Ui)**2,1) %s'%str(np.sum(np.dot(betaBASIS_PHI,Ui)**2,1)))
        S_in = beta - np.atleast_2d(np.sum(np.dot(betaBASIS_PHI,Ui)**2,1)).T
#        self.appLogger.debug('S_in %s'%str(S_in))
        Q_in = beta * (BASIS_Targets - np.dot(BASIS_PHI,Mu))
#        self.appLogger.debug('Q_in %s'%str(Q_in))
        
        S_out = S_in.copy()
        Q_out = Q_in.copy()
        
        try:
            S_out[Used] = (Alpha * S_in[Used])/(Alpha - S_in[Used])
#            self.appLogger.debug('S_out %s'%str(S_out))
        except FloatingPointError as e:
            self.appLogger.error(e)
        try:
            Q_out[Used] = (Alpha * Q_in[Used])/(Alpha - S_in[Used])
#            self.appLogger.debug('Q_out %s'%str(Q_out))
        except FloatingPointError as e:
            self.appLogger.error(e)
        
        Factor = Q_out * Q_out - S_out
#        self.appLogger.debug('Factor %s'%str(Factor))

        return SIGMA,Mu,S_in,Q_in,S_out,Q_out,Factor,logML,Gamma,betaBASIS_PHI,beta
        
#    def sequential_update(self,X,Targets,Scales,BASIS,PHI,BASIS_PHI,BASIS_Targets,\
#                               Used,Alpha,beta,\
#                               SIGMA,Mu,S_in,Q_in,S_out,Q_out,Factor,logML,Gamma,BASIS_B_PHI):
    def sequential_update(self,X,Targets,Scales,BASIS,PHI,BASIS_PHI,BASIS_Targets,\
                               Used,Alpha,beta,Aligned_out,Aligned_in,align_defer_count,\
                               SIGMA,Mu,S_in,Q_in,S_out,Q_out,Factor,logML,Gamma,BASIS_B_PHI):
#        self.appLogger.debug('sequential_update')
        # diagnosis
        update_count = 0
        add_count = 0
        delete_count = 0
        beta_count = 0
        
        count = 0
        log_marginal_log = np.array([])
        
        try:
            N,M_full = BASIS.shape
        except ValueError:
            M_full = 1
        try:
            n,M = PHI.shape
        except ValueError:
            M = 1

#        Aligned_out = np.array([])
#        Aligned_in = np.array([])
        align_defer_count = 0

        i = 0;full_count = 0
        LAST_ITERATION = False
        
        while (not LAST_ITERATION):
            i += 1
            
            # decision phase
#            self.appLogger.debug('decision phase')
            DeltaML = np.zeros((M_full,1))
#            self.appLogger.debug('DeltaML %s'%str(DeltaML))
            Action = self.ACTION_REESTIMATE*np.ones((M_full,1))
#            self.appLogger.debug('Action %s'%str(Action))
            UsedFactor = Factor[Used]
#            self.appLogger.debug('UsedFactor %s'%str(UsedFactor))
            
            # re-estimation: must be a positive 'factor' and already in the model
#            iu = np.ravel(UsedFactor > self.CONTROL_ZeroFactor)
#            self.appLogger.debug('re-estimation?')
            iu = (UsedFactor.ravel() > self.CONTROL_ZeroFactor)
#            self.appLogger.debug('iu %s'%str(iu))
            index = Used[iu]
#            self.appLogger.debug('index %s'%str(index))
            try:
                new_Alpha = S_out[index]**2/Factor[index]
#                self.appLogger.debug('new_Alpha %s'%str(new_Alpha))
            except FloatingPointError as e:
                self.appLogger.error(e)
                raise RuntimeError,e

            try:
                Delta = 1/new_Alpha - 1/Alpha[iu]
#                self.appLogger.debug('Delta %s'%str(Delta))
            except FloatingPointError as e:
                self.appLogger.error(e)
                raise RuntimeError,e
                
            # quick computation of change in log-likelihood given all re-estimations
            try:
                DeltaML[index] = (Delta * (Q_in[index]**2)/(Delta * S_in[index] + 1) - np.log(1 + S_in[index] * Delta))/2
#                self.appLogger.debug('DeltaML %s'%str(DeltaML))
            except FloatingPointError as e:
                self.appLogger.error(e)
                raise RuntimeError,e

            # deletion: if negative factor and in model
#            self.appLogger.debug('deletion?')
            iu = np.logical_not(iu)
#            self.appLogger.debug('iu %s'%str(iu))
            index = Used[iu]
#            self.appLogger.debug('index %s'%str(index))
            any_to_delete = True if len(index) > 0 else False
            if any_to_delete:
                # quick computation of change in log-likelihood given all deletions
#                DeltaML[index] = -(Q_out[index]**2/(S_out[index] - Alpha[iu]) - np.log(1 + S_out[index] / Alpha[iu]))/2
                try:                
                    DeltaML[index] = -(Q_out[index]**2/(S_out[index] + Alpha[iu]) - np.log(1 + S_out[index]/Alpha[iu]))/2
#                    self.appLogger.debug('DeltaML %s'%str(DeltaML))
                except FloatingPointError as e:
                    self.appLogger.error(e)
                    raise RuntimeError,e

                Action[index] = self.ACTION_DELETE
#                self.appLogger.debug('Action %s'%str(Action))
            
            # addition: must be a positive factor and out of the model
#            GoodFactor = (Factor > self.CONTROL_ZeroFactor).copy()
#            self.appLogger.debug('addition?')
            GoodFactor = Factor > self.CONTROL_ZeroFactor
#            self.appLogger.debug('GoodFactor %s'%str(GoodFactor))
            GoodFactor[Used] = False
#            self.appLogger.debug('GoodFactor %s'%str(GoodFactor))
            if self.CONTROL_BasisAlignmentTest:
                try:
                    GoodFactor[Aligned_out] = False
#                    self.appLogger.debug('GoodFactor %s'%str(GoodFactor))
                except IndexError as e:
                    self.appLogger.debug(e)
#                    raise RuntimeError,e
            index = GoodFactor.nonzero()
#            self.appLogger.debug('index %s'%str(index))
#            any_to_add = True if len(index) > 0 else False
            any_to_add = True if len(index[0]) > 0 else False
            if any_to_add:
#                self.appLogger.debug('any to add')
                # quick computation of change in log-likelihood given all additions
                try:
                    quot = Q_in[index]**2/S_in[index]
#                    self.appLogger.debug('quot %s'%str(quot))
                except FloatingPointError as e:
                    self.appLogger.error(e)
                    raise RuntimeError,e
                DeltaML[index] = (quot - 1 - np.log(quot))/2
#                self.appLogger.debug('DeltaML %s'%str(DeltaML))
                Action[index] = self.ACTION_ADD
#                self.appLogger.debug('Action %s'%str(Action))
            # preference
            if (any_to_add and self.CONTROL_PriorityAddition) or \
            (any_to_delete and self.CONTROL_PriorityDeletion):
#                self.appLogger.debug('priority set')
                # We won't perform re-estimation this iteration, which we achieve by
                # zero-ing out the delta
                DeltaML[Action==self.ACTION_REESTIMATE] = 0
                #Furthermore, we should enforce ADD if preferred and DELETE is not
                # - and vice-versa
                if any_to_add and self.CONTROL_PriorityAddition and not self.CONTROL_PriorityDeletion:
                    DeltaML[Action==self.ACTION_DELETE] = 0
                if any_to_delete and self.CONTROL_PriorityDeletion and not self.CONTROL_PriorityAddition:
                    DeltaML[Action==self.ACTION_ADD] = 0
#            self.appLogger.debug('DeltaML %s'%str(DeltaML))
            # choose the action that results in the greatest change in likelihood
            delta_log_marginal,nu = DeltaML.max(axis=0),DeltaML.argmax(axis=0)
#            self.appLogger.debug('delta_log_marginal %s'%str(delta_log_marginal))
#            self.appLogger.debug('nu %s'%str(nu))
            selected_Action = Action[nu]
#            self.appLogger.debug('selected_Action %s'%str(selected_Action))
            any_worthwhile_Action = delta_log_marginal > 0
#            self.appLogger.debug('any_worthwhile_Action %s'%str(any_worthwhile_Action))
            
            # need to note if basis nu is already in the model, and if so,
            # find its interior index, denoted by "j"
            if selected_Action == self.ACTION_REESTIMATE or selected_Action == self.ACTION_DELETE:
                j = (Used==nu).nonzero()[0]
#                self.appLogger.debug('j %s'%str(j))
#                j = (Used==nu).nonzero()
#                j = j[0] if len(j) < 2 else j
                
            
            # get the individual basis vector for update and compute its optimal alpha
#            self.appLogger.debug('compute optimal alpha for the basis to update')
            Phi = BASIS[:,nu]
#            self.appLogger.debug('Phi %s'%str(Phi))
            try:
                new_Alpha = S_out[nu]**2/Factor[nu]
#                self.appLogger.debug('new_Alpha %s'%str(new_Alpha))
            except FloatingPointError as e:
                self.appLogger.error(e)
                raise RuntimeError,e
            
            # terminate conditions
            if not any_worthwhile_Action or\
            (selected_Action == self.ACTION_REESTIMATE and \
             np.abs(np.log(new_Alpha) - np.log(Alpha[j])) < self.CONTROL_MinDeltaLogAlpha and \
             not any_to_delete):
                act_ = 'potential termination'
                selected_Action = self.ACTION_TERMINATE
                
            # alignment checks
#            self.appLogger.debug('alignment checks')
            if self.CONTROL_BasisAlignmentTest:
                if selected_Action == self.ACTION_ADD:
                    # rule out addition if the new basis vector is aligned too closely to
                    # one or more already in the model
                    p = np.dot(Phi.T,PHI)
#                    self.appLogger.debug('p %s'%str(p))
                    find_Aligned = (p.ravel() > self.CONTROL_AlignmentMax).nonzero()
#                    self.appLogger.debug('find_Aligned %s'%str(find_Aligned))
                    num_Aligned = find_Aligned[0].size
                    if num_Aligned > 0:
                        # the added basis function is effectively indistinguishable from one present already
                        selected_Action = self.ACTION_ALIGNMENT_SKIP
                        act_ = 'alignment-deferred addition'
                        align_defer_count += 1
                        Aligned_out = np.concatenate((Aligned_out,nu.repeat(num_Aligned))).astype('int')
                        Aligned_in = np.concatenate((Aligned_in,Used[find_Aligned])).astype('int')
                        self.appLogger.info('Alignment out of %s'%str(Aligned_out))
#                        self.appLogger.debug('Aligned_in %s'%str(Aligned_in))
#                        self.appLogger.debug('Aligned_out %s'%str(Aligned_out))
                if selected_Action == self.ACTION_DELETE:
                    # reinstate any previously deferred basis functions resulting from this basis function
                    find_Aligned = (Aligned_in == nu).nonzero()
                    num_Aligned = find_Aligned[0].size
                    if num_Aligned > 0:
                        reinstated = Aligned_out[find_Aligned]
                        Aligned_in = np.delete(Aligned_in,find_Aligned)
                        Aligned_out = np.delete(Aligned_out,find_Aligned)
                        self.appLogger.info('Alignment reinstatement of %s'%str(reinstated))
#                        self.appLogger.debug('Aligned_in %s'%str(Aligned_in))
#                        self.appLogger.debug('Aligned_out %s'%str(Aligned_out))
            
            # action phase
            # note if we've made a change which necessitates later updating of the statistics
#            self.appLogger.debug('action phase')

            UPDATE_REQUIRED = False
            
            if selected_Action == self.ACTION_REESTIMATE:
#                self.appLogger.debug('ACTION_REESTIMATE')
                # basis function 'nu' is already in the model,
                # and we're re-estimating its corresponding alpha
                old_Alpha = Alpha[j]
                Alpha[j] = new_Alpha
#                self.appLogger.debug('Alpha %s'%str(Alpha))
#                s_j = SIGMA[:,j].copy()
                s_j = SIGMA[:,j]
#                self.appLogger.debug('s_j %s'%str(s_j))
                try:
                    deltaInv = 1/(new_Alpha - old_Alpha)
#                    self.appLogger.debug('deltaInv %s'%str(deltaInv))
                except FloatingPointError as e:
                    self.appLogger.error(e)
                    raise RuntimeError,e
                try:
                    kappa = 1/(SIGMA[j,j] + deltaInv)
#                    self.appLogger.debug('kappa %s'%str(kappa))
                except FloatingPointError as e:
                    self.appLogger.error(e)
                    raise RuntimeError,e
                tmp = kappa * s_j
#                self.appLogger.debug('tmp %s'%str(tmp))
                SIGMANEW = SIGMA - np.dot(tmp,s_j.T)
#                self.appLogger.debug('SIGMANEW %s'%str(SIGMANEW))
                deltaMu = -Mu[j] * tmp
#                self.appLogger.debug('deltaMu %s'%str(deltaMu))
                Mu = Mu + deltaMu
#                self.appLogger.debug('Mu %s'%str(Mu))
                
                S_in = S_in + kappa * np.dot(BASIS_B_PHI,s_j)**2
#                self.appLogger.debug('S_in %s'%str(S_in))
                Q_in = Q_in - np.dot(BASIS_B_PHI,deltaMu)
#                self.appLogger.debug('Q_in %s'%str(Q_in))
                
                update_count += 1
                act_ = 're-estimation'
                UPDATE_REQUIRED = True
                
            elif selected_Action == self.ACTION_ADD:
#                self.appLogger.debug('ACTION_ADD')
                # basis function nu is not in the model, and we're adding it in
                BASIS_Phi = np.dot(BASIS.T,Phi)
#                self.appLogger.debug('BASIS_Phi %s'%str(BASIS_Phi))
                BASIS_PHI = np.hstack((BASIS_PHI,BASIS_Phi))
#                self.appLogger.debug('BASIS_PHI %s'%str(BASIS_PHI))
                B_Phi = beta * Phi
#                self.appLogger.debug('B_Phi %s'%str(B_Phi))
                BASIS_B_Phi = beta * BASIS_Phi
#                self.appLogger.debug('BASIS_B_Phi %s'%str(BASIS_B_Phi))
                tmp = np.dot(np.dot(B_Phi.T,PHI),SIGMA).T
#                self.appLogger.debug('tmp %s'%str(tmp))
                Alpha = np.vstack((Alpha,new_Alpha))
#                self.appLogger.debug('Alpha %s'%str(Alpha))
                PHI = np.hstack((PHI,Phi))
#                self.appLogger.debug('PHI %s'%str(PHI))
                try:
                    s_ii = 1/(new_Alpha + S_in[nu])
#                    self.appLogger.debug('s_ii %s'%str(s_ii))
                except FloatingPointError as e:
                    self.appLogger.error(e)
                    raise RuntimeError,e
                s_i = -(s_ii * tmp)
#                self.appLogger.debug('s_i %s'%str(s_i))
                TAU = -np.dot(s_i,tmp.T)
#                self.appLogger.debug('TAU %s'%str(TAU))
                SIGMANEW = np.vstack((np.hstack((SIGMA+TAU,s_i)),np.hstack((s_i.T,s_ii))))
#                self.appLogger.debug('SIGMANEW %s'%str(SIGMANEW))
#                SIGMANEW = np.vstack((np.hstack((SIGMA+TAU,s_i)),np.hstack((s_i.T,np.atleast_2d(s_ii)))))
                mu_i = s_ii * Q_in[nu]
#                self.appLogger.debug('mu_i %s'%str(mu_i))
                deltaMu = np.vstack((-mu_i*tmp,mu_i))
#                self.appLogger.debug('deltaMu %s'%str(deltaMu))
                Mu = np.vstack((Mu,0)) + deltaMu
#                self.appLogger.debug('Mu %s'%str(Mu))
                
                mCi = BASIS_B_Phi - np.dot(BASIS_B_PHI,tmp)
#                self.appLogger.debug('mCi %s'%str(mCi))
                S_in = S_in - s_ii * mCi**2
#                self.appLogger.debug('S_in %s'%str(S_in))
                Q_in = Q_in - mu_i * mCi
#                self.appLogger.debug('S_in %s'%str(S_in))
                
                Used = np.concatenate((Used,nu))
#                self.appLogger.debug('Used %s'%str(Used))
                
                add_count += 1
                act_ = 'addition'
                UPDATE_REQUIRED = True
                
            elif selected_Action == self.ACTION_DELETE:
#                self.appLogger.debug('ACTION_DELETE')
                # basis function nu is in the model, but we're removing it
                BASIS_PHI = np.delete(BASIS_PHI,j,1)
#                self.appLogger.debug('BASIS_PHI %s'%str(BASIS_PHI))
                PHI = np.delete(PHI,j,1)
#                self.appLogger.debug('PHI %s'%str(PHI))
                Alpha = np.delete(Alpha,j,0)
#                self.appLogger.debug('Alpha %s'%str(Alpha))
#                s_jj = SIGMA[j,j].copy()
                s_jj = SIGMA[j,j]
#                self.appLogger.debug('s_jj %s'%str(s_jj))
#                s_j = SIGMA[:,j].copy()
                s_j = SIGMA[:,j]
#                self.appLogger.debug('s_j %s'%str(s_j))
                tmp = s_j/s_jj
#                self.appLogger.debug('tmp %s'%str(tmp))
                SIGMANEW = SIGMA - np.dot(tmp,s_j.T)
                SIGMANEW = np.delete(SIGMANEW,j,0)
                SIGMANEW = np.delete(SIGMANEW,j,1)
#                self.appLogger.debug('SIGMANEW %s'%str(SIGMANEW))
                deltaMu = -Mu[j] * tmp
#                self.appLogger.debug('deltaMu %s'%str(deltaMu))
#                mu_j = Mu[j].copy()
                mu_j = Mu[j]
#                self.appLogger.debug('mu_j %s'%str(mu_j))

                Mu = Mu + deltaMu
                Mu = np.delete(Mu,j,0)
#                self.appLogger.debug('Mu %s'%str(Mu))
                
                jPm = np.dot(BASIS_B_PHI,s_j)
#                self.appLogger.debug('jPm %s'%str(jPm))
                try:
                    S_in = S_in + jPm**2/s_jj
#                    self.appLogger.debug('S_in %s'%str(S_in))
                except FloatingPointError as e:
                    self.appLogger.error(e)
                    raise RuntimeError,e
                try:
                    Q_in = Q_in + (jPm * mu_j)/s_jj
#                    self.appLogger.debug('Q_in %s'%str(Q_in))
                except FloatingPointError as e:
                    self.appLogger.error(e)
                    raise RuntimeError,e
                
                Used = np.delete(Used,j,0)
#                self.appLogger.debug('Used %s'%str(Used))

                delete_count += 1
                act_ = 'deletion'
                UPDATE_REQUIRED = True
                
            M = len(Used)
            if M == 0:
                self.appLogger.error('Null PHI: \nX:\n %s \nY:\n %s \nBASIS:\n %s'%(str(X),str(Targets),str(self.raw_BASIS)))
#                print 'Null PHI: \nX:\n %s \nY: %s\n \nBASIS:\n %s'%(str(self.X),str(Targets),str(BASIS))
                import pickle
                pickle.dump(X,open('X','w'))
                pickle.dump(Targets,open('Y','w'))
                pickle.dump(self.raw_BASIS,open('B','w'))
                raise RuntimeError,(X,Targets,self.raw_BASIS)
            
#            self.appLogger.debug('ACTION: %s of %d (%g)'%(act_,nu,delta_log_marginal))
                 
            # update statistics
            if UPDATE_REQUIRED:
#                self.appLogger.debug('UPDATE_REQUIRED')
                # S_in and S_out values were calculated earlier
                # Here update the S_out and Q_out values and relevance factors
                S_out = S_in.copy()
                Q_out = Q_in.copy()
                try:
                    tmp = Alpha/(Alpha - S_in[Used])
#                    self.appLogger.debug('tmp %s'%str(tmp))
                except FloatingPointError as e:
                    self.appLogger.error(e)
                    raise RuntimeError,e
                S_out[Used] = tmp * S_in[Used]
#                self.appLogger.debug('S_out %s'%str(S_out))
                Q_out[Used] = tmp * Q_in[Used]
#                self.appLogger.debug('Q_out %s'%str(Q_out))
#                print Q_in
                Factor = Q_out * Q_out - S_out
#                self.appLogger.debug('Factor %s'%str(Factor))
#                SIGMA = SIGMANEW.copy()
                SIGMA = SIGMANEW
#                self.appLogger.debug('SIGMA %s'%str(SIGMA))
                Gamma = 1 - np.ravel(Alpha) * np.diag(SIGMA)
#                self.appLogger.debug('Gamma %s'%str(Gamma))
                BASIS_B_PHI = beta * BASIS_PHI
#                self.appLogger.debug('BASIS_B_PHI %s'%str(BASIS_B_PHI))
                
                if delta_log_marginal < 0:
                    self.appLogger.warning('** Alert **  DECREASE IN LIKELIHOOD !! (%g)'%delta_log_marginal)

                logML += delta_log_marginal
                count = count + 1
                log_marginal_log = np.concatenate((log_marginal_log,logML.ravel()))
            
            # Gaussian noise estimate
            if selected_Action == self.ACTION_TERMINATE or \
                i <= self.CONTROL_BetaUpdateStart or \
                i % self.CONTROL_BetaUpdateFrequency == 0:
#                self.appLogger.debug('Gaussian noise estimate')
                betaZ1 = beta
#                self.appLogger.debug('betaZ1 %s'%str(betaZ1))
                y = np.dot(PHI,Mu)
                e = Targets - y
                if np.dot(e.T,e) > 0:
                    beta = (N - np.sum(Gamma))/np.dot(e.T,e)
#                    self.appLogger.debug('1) beta %s'%str(beta))
                    # work-around zero-noise issue
                    if np.var(Targets) > 1:
                        beta = np.min(np.vstack((beta,self.CONTROL_BetaMaxFactor/np.var(Targets))))
#                        self.appLogger.debug('2) beta %s'%str(beta))
                    else:
                        beta = np.min(np.vstack((beta,self.CONTROL_BetaMaxFactor)))
#                        self.appLogger.debug('3) beta %s'%str(beta))
                else:
                    # work-around zero-noise issue
                    if np.var(Targets) > 1:
                        beta = self.CONTROL_BetaMaxFactor/np.var(Targets)
#                        self.appLogger.debug('4) beta %s'%str(beta))
                    else:
                        beta = self.CONTROL_BetaMaxFactor
#                        self.appLogger.debug('5) beta %s'%str(beta))
    
                delta_log_beta = np.log(beta) - np.log(betaZ1)
#                self.appLogger.debug('delta_log_beta %s'%str(delta_log_beta))
                
                if np.abs(delta_log_beta) > self.CONTROL_MinDeltaLogBeta:
                    self.appLogger.info('Large delta_log_beta %g'%delta_log_beta)
                    SIGMA,Mu,S_in,Q_in,S_out,Q_out,Factor,logML,Gamma,BASIS_B_PHI,beta = \
                    self.full_statistics(BASIS,PHI,Targets,Used,Alpha,beta,BASIS_PHI,BASIS_Targets)
                    full_count += 1
                    count = count + 1;
                    log_marginal_log = np.concatenate((log_marginal_log,logML.copy().ravel()))
                    if selected_Action == self.ACTION_TERMINATE:
                        selected_Action = self.ACTION_NOISE_ONLY
                        self.appLogger.info('Noise update (termination deferred)')
                        
            if selected_Action == self.ACTION_TERMINATE:
                self.appLogger.info('** Stopping at iteration %d (Max_delta_ml=%g) **'%(i,delta_log_marginal))
                self.appLogger.info('%4d> L = %.6f\t Gamma = %.2f (M = %d)'%(i,logML/N,np.sum(Gamma),M))
                break
            
            # check for "natural" termination
            if i == self.OPTIONS_iteration:
                LAST_ITERATION = True
            
            if ((self.OPTIONS_monitor > 0) and (i % self.OPTIONS_monitor == 0)) or LAST_ITERATION:
                self.appLogger.info('%5d> L = %.6f\t Gamma = %.2f (M = %d)'%(i,logML/N,np.sum(Gamma),M))

        # post-process
        self.appLogger.debug('post process')
        if selected_Action != self.ACTION_TERMINATE:
            self.appLogger.info('Iteration limit: algorithm did not converge')
        
        total = add_count + delete_count + update_count
        if self.CONTROL_BasisAlignmentTest:
            total += align_defer_count
            
        if total == 0: total = 1
        
        self.appLogger.info('Action Summary')
        self.appLogger.info('==============')
        self.appLogger.info('Added\t\t%6d (%.0f%%)'%(add_count,100*add_count/total))
        self.appLogger.info('Deleted\t\t%6d (%.0f%%)'%(delete_count,100*delete_count/total))
        self.appLogger.info('Reestimated\t%6d (%.0f%%)'%(update_count,100*update_count/total))
        if self.CONTROL_BasisAlignmentTest and align_defer_count:
            self.appLogger.info('--------------');
            self.appLogger.info('Deferred\t%6d (%.0f%%)'%(align_defer_count,100*align_defer_count/total))
        self.appLogger.info('==============')
        self.appLogger.info('Total of %d likelihood updates'%count)
#        self.appLogger.info('Time to run: %s', SB2_FormatTime(t1));
        
        Relevant,index = np.sort(Used),np.argsort(Used)
        Mu = Mu[index] / Scales[Used[index]]
        Alpha = Alpha[index] / Scales[Used[index]]**2
        
#        return Used,Relevant,Mu,Alpha,beta,update_count,add_count,delete_count,full_count    
        return Used,Aligned_out,Aligned_in,align_defer_count,\
            Relevant,Mu,Alpha,beta,update_count,add_count,delete_count,full_count    

    def learn(self,X,Targets,basis_func,raw_BASIS=None,extendable=True):
#    def learn(self,X,Targets,basis_func,BASIS=None,extendable=True):

        if raw_BASIS == None:
            raw_BASIS = basis_func(X)
#        if BASIS == None:
#            BASIS = basis_func(X)
        
        # initialization
#        self.appLogger.info('Initialization')
        BASIS,Scales,Alpha,beta,Mu,PHI,Used = self.initialize(raw_BASIS.copy(),Targets)
#        BASIS,Scales,Alpha,beta,Mu,PHI,Used = self.initialize(BASIS,Targets)
#        print BASIS,Scales,Alpha,beta,Mu,PHI,Used
        
        BASIS_PHI = np.dot(BASIS.T,PHI)
        BASIS_Targets = np.dot(BASIS.T,Targets)
        
        # full computation
#        self.appLogger.info('Full computation')
        SIGMA,Mu,S_in,Q_in,S_out,Q_out,Factor,logML,Gamma,BASIS_B_PHI,beta = \
        self.full_statistics(BASIS,PHI,Targets,Used,Alpha,beta,BASIS_PHI,BASIS_Targets)
        
        Aligned_out = np.array([])
        Aligned_in = np.array([])
        align_defer_count = 0

#        Used,Relevant,Mu,Alpha,beta,update_count,add_count,delete_count,full_count = \
#        self.sequential_update(X,Targets,Scales,BASIS,PHI,BASIS_PHI,BASIS_Targets,\
#                               Used,Alpha,beta,\
#                               SIGMA,Mu,S_in,Q_in,S_out,Q_out,Factor,logML,Gamma,BASIS_B_PHI)
        Used,Aligned_out,Aligned_in,align_defer_count,\
        Relevant,Mu,Alpha,beta,update_count,add_count,delete_count,full_count = \
        self.sequential_update(X,Targets,Scales,BASIS,PHI,BASIS_PHI,BASIS_Targets,\
                               Used,Alpha,beta,Aligned_out,Aligned_in,align_defer_count,\
                               SIGMA,Mu,S_in,Q_in,S_out,Q_out,Factor,logML,Gamma,BASIS_B_PHI)
        
        if extendable:
#            self.X,self.Targets,self.raw_BASIS,self.BASIS,self.Used,\
#            self.Alpha,self.beta =\
#            X,Targets,raw_BASIS,BASIS,Used,\
#            Alpha,beta
            self.X,self.Targets,self.raw_BASIS,self.BASIS,self.Used,\
            self.Alpha,self.beta,\
            self.Aligned_out,self.Aligned_in,self.align_defer_count =\
            X,Targets,raw_BASIS,BASIS,Used,\
            Alpha,beta,\
            Aligned_out,Aligned_in,align_defer_count
#            
#            self.X,self.Targets,self.BASIS,self.Used,\
#            self.Alpha,self.beta,\
#            self.Aligned_out,self.Aligned_in,self.align_defer_count =\
#            X,Targets,BASIS,Used,\
#            Alpha,beta,\
#            Aligned_out,Aligned_in,align_defer_count
        
#        return Relevant,Mu,Alpha,beta,BASIS,update_count,add_count,delete_count,full_count
        return Relevant,Mu,Alpha,beta,update_count,add_count,delete_count,full_count
                
    def incremental_learn(self,new_X,new_T,inc_basis_func,raw_BASIS=None,extendable=True):
#    def incremental_learn(self,new_X,new_T,inc_basis_func,BASIS=None,extendable=True):
        try:
#            X,Targets,raw_BASIS,BASIS,Used,\
#            Alpha,beta = \
#            self.X,self.Targets,self.raw_BASIS,self.BASIS,self.Used,\
#            self.Alpha,self.beta
            X,Targets,raw_BASIS,BASIS,Used,\
            Alpha,beta,\
            Aligned_out,Aligned_in,align_defer_count = \
            self.X,self.Targets,self.raw_BASIS,self.BASIS,self.Used,\
            self.Alpha,self.beta,\
            self.Aligned_out,self.Aligned_in,self.align_defer_count

#            X,Targets,BASIS,Used,\
#            Alpha,beta,\
#            Aligned_out,Aligned_in,align_defer_count = \
#            self.X,self.Targets,self.BASIS,self.Used,\
#            self.Alpha,self.beta,\
#            self.Aligned_out,self.Aligned_in,self.align_defer_count
#        except NameError:
        except:
            return self.learn(new_X,new_T,inc_basis_func,raw_BASIS=raw_BASIS)
#            return self.learn(new_X,new_T,inc_basis_func,BASIS=BASIS)
#            print "First, use 'learn' method with extendable=True"

#        X = np.vstack((X,new_X))
        X += new_X
        Targets = np.vstack((Targets,new_T))
        
        if len(X) > self.CONTROL_BasisFunctionMax and len(Used) > 1:
            X.pop(0)
            raw_BASIS = np.delete(raw_BASIS,0,0)
            raw_BASIS = np.delete(raw_BASIS,0,1)

            Targets = np.delete(Targets,0,0)

#            self.appLogger.info('Aligned_out: %s'%str(Aligned_out))
#            self.appLogger.info('Aligned_in: %s'%str(Aligned_in))
            find_Aligned = (Aligned_in == np.array([0])).nonzero()
            num_Aligned = find_Aligned[0].size
            if num_Aligned > 0:
                self.appLogger.info('By limit on max basis vectors, alignment reinstatement of %s'%str(Aligned_out[find_Aligned]))
                Aligned_in = np.delete(Aligned_in,find_Aligned)
                Aligned_out = np.delete(Aligned_out,find_Aligned)
#                self.appLogger.info('Aligned_out: %s'%str(Aligned_out))
#                self.appLogger.info('Aligned_in: %s'%str(Aligned_in))
            find_Aligned = (Aligned_out == np.array([0])).nonzero()
            num_Aligned = find_Aligned[0].size
            if num_Aligned > 0:
                self.appLogger.info('By limit on max basis vectors, delete alignment of [0]')
                Aligned_in = np.delete(Aligned_in,find_Aligned)
                Aligned_out = np.delete(Aligned_out,find_Aligned)
#                self.appLogger.info('Aligned_out: %s'%str(Aligned_out))
#                self.appLogger.info('Aligned_in: %s'%str(Aligned_in))
            Aligned_in -= 1
            Aligned_out -= 1
#            self.appLogger.info('Aligned_out: %s'%str(Aligned_out))
#            self.appLogger.info('Aligned_in: %s'%str(Aligned_in))

            self.appLogger.info('Shrink Used(%d) %s'%(len(Used),str(Used)))
            Used -= 1
            index = (Used == -1).nonzero()
            Used = np.delete(Used,index)
            Alpha = np.atleast_2d(np.delete(Alpha,index)).T
            self.appLogger.info('to(%d) %s'%(len(Used),str(Used)))
            
        raw_BASIS = inc_basis_func(X,raw_BASIS)
#        BASIS = inc_basis_func(X,BASIS)
            
        # pre-process
#        self.appLogger.info('Pre-process')
        BASIS,Scales = self.preprocess(raw_BASIS.copy())
#        BASIS,Scales = self.preprocess(BASIS)
        
        PHI = BASIS[:,Used]
#        print BASIS,Scales,Alpha,beta,Mu,PHI,Used
        
        BASIS_PHI = np.dot(BASIS.T,PHI)
        BASIS_Targets = np.dot(BASIS.T,Targets)
        
        # full computation
#        self.appLogger.info('Full computation') 
        SIGMA,Mu,S_in,Q_in,S_out,Q_out,Factor,logML,Gamma,BASIS_B_PHI,beta = \
        self.full_statistics(BASIS,PHI,Targets,Used,Alpha,beta,BASIS_PHI,BASIS_Targets)
        
#        Used,Relevant,Mu,Alpha,beta,update_count,add_count,delete_count,full_count = \
#        self.sequential_update(X,Targets,Scales,BASIS,PHI,BASIS_PHI,BASIS_Targets,\
#                               Used,Alpha,beta,\
#                               SIGMA,Mu,S_in,Q_in,S_out,Q_out,Factor,logML,Gamma,BASIS_B_PHI)
        Used,Aligned_out,Aligned_in,align_defer_count,\
        Relevant,Mu,Alpha,beta,update_count,add_count,delete_count,full_count = \
        self.sequential_update(X,Targets,Scales,BASIS,PHI,BASIS_PHI,BASIS_Targets,\
                               Used,Alpha,beta,Aligned_out,Aligned_in,align_defer_count,\
                               SIGMA,Mu,S_in,Q_in,S_out,Q_out,Factor,logML,Gamma,BASIS_B_PHI)

        if extendable:
#            self.X,self.Targets,self.raw_BASIS,self.BASIS,self.Used,\
#            self.Alpha,self.beta =\
#            X,Targets,raw_BASIS,BASIS,Used,\
#            Alpha,beta
            self.X,self.Targets,self.raw_BASIS,self.BASIS,self.Used,\
            self.Alpha,self.beta,\
            self.Aligned_out,self.Aligned_in,self.align_defer_count =\
            X,Targets,raw_BASIS,BASIS,Used,\
            Alpha,beta,\
            Aligned_out,Aligned_in,align_defer_count
#                        
#            self.X,self.Targets,self.BASIS,self.Used,\
#            self.Alpha,self.beta,\
#            self.Aligned_out,self.Aligned_in,self.align_defer_count =\
#            X,Targets,BASIS,Used,\
#            Alpha,beta,\
#            Aligned_out,Aligned_in,align_defer_count
        
#        return Relevant,Mu,Alpha,beta,BASIS,update_count,add_count,delete_count,full_count
        return Relevant,Mu,Alpha,beta,update_count,add_count,delete_count,full_count
                
    def get_basis_size(self):
        try: 
            return len(self.X)
        except:
            return 0
    
    def get_basis_points(self):
        return self.X
