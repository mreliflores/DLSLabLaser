import numpy as np
import io, os
import subprocess

class CONTIN():
    def __init__(self, path_contin, contin_points=100.0, angle=90.0, temperature=298.0, wavelength=650.0, viscosity=1.02, refractive_index=1.331, contin_limits=[150, 220]) -> None:
        assert os.path.isfile(path_contin)
        self.path_contin = path_contin
        self.NG = contin_points
        self.angle = angle
        self.temperature = temperature
        self.wavelength = wavelength
        self.viscosity = viscosity
        self.n = refractive_index
        self.gmnmx1 = contin_limits[0]
        self.gmnmx2 = contin_limits[1]
        
        self.debug = False
        pass

    def scatteringVector(self, angle, wavelength, refractive_index):
        return 4 * np.pi * refractive_index / (wavelength * 1e-7) * np.sin(np.radians(angle)/2)
    
    def StokesEinstein(self, T, eta, kB=1.3807e-16):
        return kB * T / (0.06 * eta * np.pi)

    def run(self, tau, g1, tauMin, tauMax):
        #print(tau)
        tau = list(tau)
        #print(tau)
        #print(np.array(g1, ndmin=0))
        dt = tau[1] - tau[0]
        init = int((tauMin - tau[0]) / dt)
        fin = int((tauMax - tau[0]) / dt)

        if tauMin < tau[0]:
            init = 0
        if tauMax > tau[len(tau)-1]:
            fin = len(tau)

        GMNMX1 = self.gmnmx1 * 5e-8
        GMNMX2 = self.gmnmx2 * 5e-8

        R21 = self.StokesEinstein(self.temperature, self.viscosity) * self.scatteringVector(self.angle, self.wavelength, self.n) ** 2
        R22 = -1
        R23 = 0
        #print(R21)

        last = 1  # for multi dataset evaluation this is -1 (false) except for the last one
        # we process here ONLY single files
        elements = 45  # just to have an array for it; last 2 lines are "end" and NY
        header = np.array([''] * elements, dtype='|S70')  # a single fortran line
        header[0] = 'filename'.ljust(70)  # the loaded file
        header[1] = 'LAST'.ljust(6) + str().rjust(5) + ('%15.4E' % last)  # see above
        header[2] = 'GMNMX'.ljust(6) + str(1).rjust(5) + ('%15.4E' % GMNMX1) # fit interval min
        header[3] = 'GMNMX'.ljust(6) + str(2).rjust(5) + ('%15.4E' % GMNMX2) # fit interval max
        header[4] = 'IWT'.ljust(6) + str().rjust(5) + ('%15.4E' % 5)  # fit strategy how to determine errors -> 5 from a prefit, results in 2 fits but good errors
        # unweighted fit IWT=1 ->errors equal; IWT=4 direct input of errors not implemented
        header[5] = 'NERFIT'.ljust(6) + str().rjust(5) + ('%15.4E' % 0)  # number of points around a point to determine error; safety margin default 10; we use 0
        header[6] = 'NINTT'.ljust(6) + str().rjust(5) + ('%15.4E' % -1)  # number of equally spaced sets in tk; <0 means direct input as used here
        header[7] = 'IFORMT'.ljust(6) + str().rjust(20)  # format of time variable for direct input
        header[8] = '(1F16.12)'.ljust(26)  # 1 in a row
        header[9] = 'IFORMY'.ljust(6) + str().rjust(20)  # format of y variable for direct input correlation
        header[10] = '(1F16.12)'.ljust(26)  # 1 in a row

        header[12] = 'NLINF'.ljust(6) + str().rjust(5) + ('%15.4E' % 0)  # allows a single const background , 0 no bkg
        header[13] = 'NG'.ljust(6) + str().rjust(5) + ('%15.4E' % self.NG)  # n_grid  points between gmin,gmax
        header[14] = 'DOUSNQ'.ljust(6) + str().rjust(5) + ('%15.4E' % 1)  # Do User INPUT ; to use the below given values anyway this is the default
        header[15] = 'IUSER'.ljust(6) + str(10).rjust(5) + ('%15.4E' % 4)  # selects the kernel see help above
        header[16] = 'RUSER'.ljust(6) + str(15).rjust(5) + ('%15.4E' % self.n)  # refractive index
        header[17] = 'RUSER'.ljust(6) + str(16).rjust(5) + ('%15.4E' % self.wavelength)  # wavelength  in nm
        header[18] = 'RUSER'.ljust(6) + str(17).rjust(5) + ('%15.4E' % self.angle)  # scattering angle in degrees
        header[19] = 'RUSER'.ljust(6) + str(18).rjust(5) + ('%15.4E' % self.temperature)  # absolute Temperature in K or proportionality constant
        header[20] = 'RUSER'.ljust(6) + str(19).rjust(5) + ('%15.4E' % self.viscosity)  # viscosity in centipoise
        header[25] = 'RUSER'.ljust(6) + str(10).rjust(5) + ('%15.4E' % 0)  # (0) means dont change; input is g1;
        # (1) input is intensity correlation g2; =>  calculate (g2/R21-1)^0.5
        # (-1) input is g2-1,  takes only the square root
        # ALV and Zetasizer Data are g2-1 -> -1

        header[22] = 'RUSER'.ljust(6) + str(21).rjust(5) + ('%15.4E' % R21)
        header[21] = 'RUSER'.ljust(6) + str(22).rjust(5) + ('%15.4E' % R22)
        header[23] = 'RUSER'.ljust(6) + str(23).rjust(5) + ('%15.4E' % R23)

        header[27] = 'IPRINT'.ljust(6) + str(1).rjust(5) + ('%15.4E' % 0)
        header[28] = 'IPRINT'.ljust(6) + str(2).rjust(5) + ('%15.4E' % 2)
        header[29] = 'PRY'.ljust(6) + str().rjust(5) + ('%15.4E' % -1)
        header[30] = 'PRWT'.ljust(6) + str().rjust(5) + ('%15.4E' % -1)
        header[31] = 'IPLRES'.ljust(6) + str(1).rjust(5) + ('%15.4E' % 0)
        header[32] = 'IPLRES'.ljust(6) + str(2).rjust(5) + ('%15.4E' % 0)
        header[34] = 'IPLFIT'.ljust(6) + str(1).rjust(5) + ('%15.4E' % 0)
        header[35] = 'IPLFIT'.ljust(6) + str(2).rjust(5) + ('%15.4E' % 2)
        header[36] = 'DOMOM'.ljust(6) + str().rjust(5) + ('%15.4E' % 1)
        header[37] = 'MOMNMX'.ljust(6) + str(1).rjust(5) + ('%15.4E' % -3)
        header[38] = 'MOMNMX'.ljust(6) + str(2).rjust(5) + ('%15.4E' % 3)

        header[26] = 'LUSER'.ljust(6) + str(3).rjust(5) + ('%15.4E' % 1)  # use rayleighDebyeGans formfactor (set to true => 1) or const 1 (set to false => -1 )
        header[33] = 'NONNEG'.ljust(6) + str().rjust(5) + ('%15.4E' % 1)
        header[-2] = 'END'.ljust(26)
        header[-1] = 'NY'.ljust(6) + str(0).rjust(5)  # Number of datapoints is set per file later
        # ende header für CONTIN als ASCII inputfile         ##################################

        header[-1] = 'NY'.ljust(6) + str(len(tau[init:fin])).rjust(5)
        file = "sample"

        header[0] = file #sample_name

        input = io.BytesIO()
        input.writelines([b' ' + line + b'\n' for line in header if line != b''])
        input.writelines([b' ' + (b'%10.12F' % float(line)) + b'\n' for line in tau[init:fin]])
        input.writelines([b' ' + (b'%10.12F' % float(line)) + b'\n' for line in g1[init:fin]])

        if self.debug:
            with open('./' + 'input.con', 'w') as f:
                f.writelines(input.getvalue().decode('utf-8'))

        p = subprocess.run(self.path_contin, input=input.getvalue(), capture_output=True)
        input.close()
        output = p.stdout.decode('utf-8')
        error = p.stderr.decode('utf-8')
        if p.returncode > 0 or len(output) == 0:
            if error != '':
                for line in error.split('\n'):
                    print('contin_std_err>', line)
            if len(output) == 0:
                print('there was nothing in output yet')

        # to debug output
        if self.debug:
            with open('./' + file + '.con', 'w') as f:
                f.writelines(output)
                pass
            pass

        blocks = output.split(file)

        # solution fit
        block = blocks[-2]  #Solution in list with contin format
        start = block.find('ABSCISSA') + len('ABSCISSA')
        end = block.find('1CONTIN')
        block = block.replace('D', 'E')
        try: 
            block = block.replace('\r', '\n')
        except:
            pass

        lines = block[start:end].split('\n')
        lines = list(filter(None, lines))

        temp = np.c_[[[float(item) for item in line[:22].split()] for line in lines]].T

        #Array with fitting [tau, g1_fit], great output!
        fit = temp[[1, 0]]
        self.tau_fit = fit[0]
        self.fit_ = fit[1]

        #Size distribution, chosen solution
        block = blocks[-1]
        start = block.find('ABSCISSA') + len('ABSCISSA')
        end = block.find('0PEAK')
        block = block.replace('D', 'E')
        try: 
            block = block.replace('\r', '\n')
        except:
            pass

        lines = block[start:end].split('\n')
        lines = list(filter(None, lines))

        temp = np.c_[[[float(item) for item in line[:31].split()] for line in lines]].T

        #Array with solution [radius, amplitude, error]
        result = temp[[2, 0, 1]]
        self.result = result
        self.Rh = result[0] * 2e7
        self.amp = result[1]

        #compute residuals
        self.residuals = g1 - self.fit_