import csv
import numpy as np
import matplotlib.pyplot as plt
import control
from control import matlab
from collections import deque
import scipy
from scipy import odr
from scipy.ndimage import gaussian_filter1d
from numpy.lib.function_base import append
from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.measurements import label



class parse_tanque_data():
    def __init__(self,filter_sigma = 3, posicao_corte = 0, file_name = 'dados_experimento1.csv'):
        self._posicao_corte = posicao_corte
        self._t_experimento = []
        self.x_deg =  0
        self.__soma = []
        self.tan_x,self.tan_y = [], []
        self._infls = []
        self._altura_tanque = []
        self._tensao = []
        self.ls = []
        self._filtrado = []
        self.filter_len = 7
        self._deque = deque(maxlen=self.filter_len)
        self._csv_file = open(file_name,'r')
                
        for row in self._csv_file:
            self._row = row.split(';')
            #print(self._row)
#            break
            if self._row[1] == 'alturaTanque1':
                pass
            else:
                if float(self._row[0]) <= self._posicao_corte:
                    pass
                else:
                    self._t_experimento.append(float(self._row[0]))
                    self._altura_tanque.append(float(self._row[1]))
                    self._tensao.append(float(self._row[3]))
                    self._deque.append(float(self._row[1]))
                    if float(self._row[0]) >= 475:
                        self.ls.append(float(self._row[1]))
                    
                    
                    if len(self._deque) == self.filter_len:
                        a = sum(self._deque)/self.filter_len
                        self._filtrado.append(sum(self._deque)/self.filter_len)
                        
        for w in range(self.filter_len-1):
            self._filtrado.append(a)
        self._V_filtrado = gaussian_filter1d(self._filtrado,filter_sigma)
        self._csv_file.close()
         

    def inflec_points(self):
        self._smooth_d2 = np.gradient(np.gradient(self._V_filtrado))
        self._infls = np.where(np.diff(np.sign(self._smooth_d2)))[0] + self._posicao_corte
        return self._infls
        
    def tanget(self):    
        self._tangent = np.diff(self._V_filtrado)

        self._m = self._tangent[self._infls[12]-(self._posicao_corte)] *4

        for ee in range(self._infls[12]-100,self._infls[12]+100):
            self.tan_x.append(ee)
            self.tan_y.append((self._m*ee)-19.7)
        return self.tan_x, self.tan_y

    def constantes(self):
        self.L = 311.27 - self.x_deg
        print(self.L)
        self.T = 358.23 - 311.27
        print(self.T)      
        self.K0 = (np.mean(self.ls) - self.m_inf) / (2.5 - 1.5)
        print(self.K0)
        
        
    def controlador(self):
        Kp = (0.9*self.T) / (self.K0*self.L)
        Ki = 3 * self.L
        print(Kp)
        print(Ki)
    
    def m_degrau(self):
        comp = self._tensao[0]
        for i in range(len(self._tensao)):
            self.__soma.append(self._altura_tanque[i])
            if comp != self._tensao[i]:
                #print(self._t_experimento[i])
                self.t_degrau = self._t_experimento[i]
                break
            comp = self._tensao[i]
        self.x_deg = self.t_degrau #+ self._posicao_corte
        return self.x_deg
        
    def stab_limit(self):
        
        self.m_inf = np.mean(self.__soma)
        self.ys = np.mean(self.ls)*1.02
        self.yi = np.mean(self.ls)*0.98
        self.m_sup = np.mean(self.ls)
        return self.m_inf, self.m_sup, self.yi, self.ys
    
    def run(self):
        self.inflec_points()
        self.m_degrau()
        self.stab_limit()
        self.tanget()
        self.constantes()
        self.controlador()
        
        
    # def pol(self):
    #     p = np.polyfit(self.t_experimento,self._V_filtrado,6)
    #     self.axx = []
    #     ass = []
    #     for i in range(150,539):
    #         ass.append(i)
    #         self.axx.append(self.f(i,6,p))
               
    # def f(self,x,grau,poli):
    #     self.func = 0
    #     for g in range(grau+1):
    #         #print(g)
    #         self.func = self.func + (poli[g]*(np.power(x,(grau-g)))) 
    #     return self.func   
    
    # def teste(self):
    #     poly_model = scipy.odr.polynomial(4)
    #     data = odr.Data(self._t_experimento,self._V_filtrado)
    #     odr_obj = odr.ODR(data,poly_model)
    #     output = odr_obj.run()
    #     poly = np.poly1d(output.beta[::-1])
    #     poly_y = poly(self._t_experimento)
    #     plt.plot(self._t_experimento,self._altura_tanque)
    #     plt.plot(self._t_experimento,poly_y)
    #     plt.show()
    
    
    def plot(self):
        plt.plot(self._t_experimento,self._altura_tanque,linewidth= "0.5",color="blue",label="Dados Coletados")
        
        plt.plot(self._t_experimento,self._V_filtrado,linewidth= "2",label = "Dados Suavizados",color = "orange")
        # plt.plot(self.tan_x,self.tan_y,label = "Tangente",color = "purple")
        # # for e,infl in enumerate(self._infls,1):
        # #     if ((infl >= self.x_deg) and infl <= (self.x_deg+100)):
        # plt.axvline(x=self._infls[12],color = 'k', label= f"Ponto de Inflexão {self._infls[12]}")
        # plt.ylim(min(self._altura_tanque),max(self._altura_tanque))
        # plt.axvline(x=self.x_deg, color = 'g',linestyle='--',label= "Momento do Degrau")
        # plt.axhline(y=self.ys,linestyle='--',color= 'yellow',linewidth= "0.5")
        # plt.axhline(y=self.yi,linestyle='--',color= 'yellow',label= "Margem 2% de erro",linewidth= "0.5")
        # plt.axhline(y=self.m_sup,linestyle='--',color= 'red',label= "Ponto de estabilização no infinito",linewidth= "0.5")
        # plt.axhline(y=self.m_inf,linestyle='--',color= 'red',label= "Ponto de estabilização inicial",linewidth= "0.5")
        plt.legend()
        plt.show()
    

    @property         
    def t_experimento(self):
         return self._t_experimento
    
    @property         
    def altura_tanque(self):
         return self._altura_tanque
    
    @property         
    def filtrado(self):
         return self._filtrado
              
a = parse_tanque_data()
# a.teste()
