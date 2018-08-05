
# coding: utf-8
#!/usr/bin/env python3

# In[1]:


from tkinter import *
from tkinter.messagebox import showinfo
class Application(Frame):
    def showDoneMsg(self,message):
        popUp = Toplevel()
        popUp.title('Hecho')
        doneMsgLabel = Label(popUp, text=message)
        doneMsgLabel.grid(row=2, column=2)
        closeButton = Button(popUp,text='Cerrar', command=popUp.destroy)
        closeButton.grid(row=3, column=2)
    def showErrorMsg(self,message):
        popUp = Toplevel()
        popUp.title('Error')
        errorMsgLabel = Label(popUp, text=message)
        errorMsgLabel.grid(row=2, column=2)
        closeButton = Button(popUp,text='Cerrar', command=popUp.destroy)
        closeButton.grid(row=3, column=2)
    def clearNameField(self):
        self.NOMBRE.delete(0,END)
    def createConnectionToDB(self):
        import pandas as pd
        import sqlite3
        cnx = sqlite3.connect('../historias.db')
        df = pd.read_sql_query("SELECT * FROM historias", cnx)
        return df
    def getHistoryFromName(self):
        df = self.createConnectionToDB()
        nStr = self.NOMBRE.get()
        try:
            if nStr =="":
                raise NameError('ERROR: Por favor ingrese un nombre para el paciente.')
            elif not df['Nombre'].str.contains(nStr).any():
                raise NameError('ERROR: El paciente no existe en la base de datos')
            datosPaciente=df[df['Nombre'].str.contains(nStr, na=False)].reset_index(drop=True)
            datosPaciente['Cedula'][0]
            archivoHistorias = open(self.SRCDIR+"historia_"+nStr.replace(' ','')+".txt", "w", encoding='latin-1')
            archivoHistorias.write(u'Historia del paciente %s, ID %i:\n'%(nStr, datosPaciente['Cedula'][0]))
            fechas = datosPaciente['Fecha'].values
            tratamientos = datosPaciente['Tratamiento'].values
            efisico = datosPaciente['Examen Fisico'].values
            diagnostico = datosPaciente['Diagnostico'].values
            antecedentes = datosPaciente['Antecedentes'].values
            sintomas = datosPaciente['Sintomas'].values
            for i in range(len(fechas)):
                if i==0:
                    archivoHistorias.write('\subsection*{'+str(fechas[i])+':}'+'\n \subsubsection*{Antecedentes:} '+str(antecedentes[i])+'\n \subsubsection*{Síntomas:} '+str(sintomas[i])+'\n \subsubsection*{Examen Físico:} '+str(efisico[i])+'\n \subsubsection*{Diagnóstico:} '+str(diagnostico[i])+'\n \subsubsection*{Tratamiento:} ' + str(tratamientos[i])+'\n')
                else:
                    archivoHistorias.write('\subsection*{'+str(fechas[i])+':}'+'\n \subsubsection*{Síntomas:} '+str(sintomas[i])+'\n \subsubsection*{Examen Físico:} '+str(efisico[i])+'\n \subsubsection*{Diagnóstico:} '+str(diagnostico[i])+'\n \subsubsection*{Tratamiento:} ' + str(tratamientos[i])+'\n')
            archivoHistorias.close()

            head = open(self.RESDIR+'headHist.txt','r',encoding='latin-1')
            headContents = head.readlines()
            head.close()
            historia = open(self.SRCDIR+'historia_'+nStr.replace(' ','')+".txt", "r",encoding='latin-1')
            historiaContents = historia.readlines()
            headContents=[s.replace('NombrePaciente', historiaContents[0]) for s in headContents]
            #formulaFixContents = ['\item '+tip for tip in historiaContents[1:]]
            historia.close()
            tail = open(self.RESDIR+'tailHist.txt', 'r', encoding='utf-8')
            tailContents = tail.readlines()
            tail.close()
            finalHist = open('historia'+nStr.replace(' ','')+".tex", 'w', encoding='utf-8')
            toWrite = headContents+historiaContents[1:]+tailContents
            for line in toWrite:
                finalHist.write(line)
            finalHist.close()
            import subprocess

            #subprocess.check_call(['pdflatex', '-output-directory', '../HistoriasPacientes', finalHist.name])
            subprocess.check_call(['pdflatex', finalHist.name])
            #subprocess.check_call(['cleanSource.bat'])
            subprocess.check_call(['./cleanSource.sh'])
            self.showDoneMsg('La historia ha sido exportada al archivo:\n '+finalHist.name.replace('tex', 'pdf'))
        except NameError as ne:
            self.showErrorMsg(ne.args[0])
        except(KeyError,IndexError):
            self.showErrorMsg(u'ERROR: El paciente no existe.')

    def getFormulaFromName(self):
        df = self.createConnectionToDB()
        nStr = self.NOMBRE.get()
        try:
            if nStr =="":
                raise NameError('ERROR: Ingrese un nombre para el paciente.')
            elif not df['Nombre'].str.contains(nStr).any():
                raise NameError('ERROR: El paciente no existe en la base de datos')
            datosPaciente=df[df['Nombre'].str.contains(nStr, na=False)].reset_index(drop=True)
            datosPaciente['Cedula'][0]
            archivoFormulas = open(self.SRCDIR+"formula_"+nStr.replace(' ','')+".txt", "w")
            archivoFormulas.write(u'Paciente: %s, ID %i:\n'%(nStr, datosPaciente['Cedula'][0]))
            formulasNoVacias = datosPaciente['Formula'].values[datosPaciente['Formula'].values!=None]
            if len(formulasNoVacias)==0:
                raise IndexError(u'Aún no existen fórmulas para el paciente.')
            archivoFormulas.write(formulasNoVacias[len(formulasNoVacias)-1])
            archivoFormulas.close()

            head = open(self.RESDIR+'head.txt','r',encoding='latin-1')
            headContents = head.readlines()
            head.close()
            formula = open(self.SRCDIR+'formula_'+nStr.replace(' ','')+".txt", "r",encoding='latin-1')
            formulaContents = formula.readlines()
            headContents=[s.replace('NombrePaciente', formulaContents[0]) for s in headContents]
            formulaFixContents = ['\item '+tip for tip in formulaContents[1:]]
            formula.close()
            tail = open(self.RESDIR+'tail.txt', 'r', encoding='utf-8')
            tailContents = tail.readlines()
            tail.close()
            finalFormula = open('formula'+nStr.replace(' ','')+".tex", 'w', encoding='utf-8')
            toWrite = headContents+formulaFixContents+tailContents
            for line in toWrite:
                finalFormula.write(line)
            finalFormula.close()
            import subprocess
            #subprocess.check_call(['pdflatex', '-output-directory', '../FormulasPacientes', finalFormula.name])
            subprocess.check_call(['pdflatex', finalFormula.name])
            #subprocess.check_call(['cleanSource.bat'])
            subprocess.check_call(['./cleanSource.sh'])
            self.showDoneMsg('La formula ha sido exportada al archivo:\n '+finalFormula.name.replace('tex','pdf'))
        except IndexError as ie:
            self.showErrorMsg(ie.args[0])
        except NameError as ne:
            self.showErrorMsg(ne.args[0])




    def createWidgets(self):
        self.LABEL_NOMBRE = Label(self, text='Nombre del Paciente')
        self.LABEL_NOMBRE.grid(row=2, column=1, sticky=W, pady=4)
        self.NOMBRE = Entry(self,textvariable = self.name)
        self.NOMBRE['text'] = 'Introduzca el nombre del paciente'
        self.NOMBRE.grid(row=2, column = 3)

        self.GENHIST = Button(self, text='Historia', command=self.getHistoryFromName)
        self.GENHIST.grid(row=3, column = 3)

        self.GENFORM = Button(self, text='Formula', command=self.getFormulaFromName)
        self.GENFORM.grid(row=3, column = 4)

        self.LIMPIAR = Button(self, text='Limpiar', command = self.clearNameField)
        self.LIMPIAR.grid(row = 2, column=4)


        self.QUIT = Button(self)
        self.QUIT["text"] = "Salir"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.grid(row=3, column = 1)




    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.SRCDIR = './'
        self.RESDIR = './res/'
        self.name = StringVar()
        master.title("Generar Documentos")
        master.geometry('400x100')
        self.pack()
        self.createWidgets()

root = Tk()
app = Application(root)
app.mainloop()
root.destroy()
