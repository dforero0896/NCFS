
# coding: utf-8
#!/usr/bin/env python3

# In[1]:


from tkinter import *
from tkinter.messagebox import showinfo
import ZODB, ZODB.FileStorage
from BTrees.OOBTree import BTree
from ZODB.PersistentMapping import PersistentMapping
import persistent
import transaction
from tkinter.scrolledtext import ScrolledText
from datetime import *
class Consulta(persistent.Persistent):
    motivo ='DESCONOCIDO'
    diagnostico = 'DESCONOCIDO'
    tratamiento = 'NINGUNO'

    def __init__(self):
        self.fecha = str(date.today())
        self.revisionSistemas = PersistentMapping({'cabeza y cuello':'', u'tórax, respiratorio':'', 'abdomen, digestivo':'', 'genitourinario':'', 'extremidades, oesteoarticular':'', u'neurológico':'', 'generales':'', 'mentales':''})
        self.examenFisico = PersistentMapping({'peso':'', 'talla':'', 'fr':'', 'fc':'', 'ta':''})
        self.cheqOrganos = PersistentMapping({'cabeza':'', u'tórax':'', 'abdomen':'', 'extremidades':'', u'neurológico':''})
        transaction.commit()

class Historia(persistent.Persistent):
    def adicionarConsulta(self,consulta):
        self.consultas[str(date.today())] = consulta
        transaction.commit()
    def adicionarAntecedentes(self,antecedentesDict):
        for key, item in antecedentesDict.items():
            self.antecedentes[key] = item
        transaction.commit()
    def mostrarAntecedentes(self):
        for key, item in self.antecedentes.items():
            print(key, item)
    def __init__(self, numero):
        self.numero = numero
        self.fechaApertura = str(date.today())
        self.antecedentes=PersistentMapping({u'patológicos':"", u'quirúrgicos':'', u'traumáticos':'', u'toxicoalérgicos':'', u'ginecoobstétricos':'', u'familiares':'', u'medicamentos':''})
        self.consultas = BTree()
        transaction.commit()

class Paciente(persistent.Persistent):
    def cambiarDatos(self, dato_key, dato_value):
        self.datosPersonales[dato_key]=dato_value
    def crearHistoria(self):
        self.historia = Historia(self.datosPersonales['id'])
    def __init__(self):
        self.datosPersonales = PersistentMapping({'nombre':'', 'id':00000, 'email':'', 'telefono':'', 'direccion':'', 'procedencia':'', 'fechaNacimiento':'', 'edad':99, 'lugarNacimiento':'', 'sexo':'', 'eps':''})
        #self.datosPersonales = BTree()
        #self.datosPersonales.update({'nombre':'', 'id':'', 'email':'', 'telefono':'', 'direccion':'', 'procedencia':'', 'fechaNacimiento':'', 'edad':99, 'lugarNacimiento':'', 'sexo':'', 'eps':''})
        transaction.commit()
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
        storage = ZODB.FileStorage.FileStorage('pacientes.fs')
        db = ZODB.DB(storage)
        connection = db.open()
        root = connection.root
        if not hasattr(root, 'pacientes'):
            root.pacientes = BTree()
        return root

    def getHistoryFromName(self):
        root = self.root
        nStr = self.NOMBRE.get()
        try:
            if nStr =="":
                raise NameError('ERROR: Ingrese un nombre para el paciente.')
            elif not root.pacientes.has_key(nStr):
                raise NameError('ERROR: El paciente no existe en la base de datos')
            paciente= root.pacientes[nStr]
            historia = paciente.historia
            archivoHistorias = open(self.SRCDIR+"historia_"+nStr.replace(' ','')+".txt", "w", encoding='latin-1')
            archivoHistorias.write(u'Historia del Paciente: %s, ID %s:\n'%(nStr, paciente.datosPersonales['id']))
            archivoHistorias.write(u'Fecha de creación: %s'%historia.fechaApertura)
            archivoHistorias.write(u'\section*{Antecedentes}')
            for tipo, antecedente in historia.antecedentes.items():
                archivoHistorias.write('\item \\textbf{%s}: %s'%(tipo.capitalize(), antecedente.capitalize()))
            for fecha, consulta in historia.consultas.items():
                archivoHistorias.write(u'\section*{Consulta de %s}'%fecha)
                archivoHistorias.write(u'\\textbf{Motivo:} %s'%consulta.motivo)
                archivoHistorias.write(u'\subsection*{Revisión Sistemas}')
                for key, value in consulta.revisionSistemas.items():
                    archivoHistorias.write(u'\\textbf{%s:} %s\n'%(key.capitalize(), value.capitalize()))
                archivoHistorias.write(u'\subsection*{Examen Físico}')
                for key, value in consulta.examenFisico.items():
                    archivoHistorias.write(u'\\textbf{%s:} %s\n'%(key.capitalize(), value.capitalize()))
                archivoHistorias.write(u'\subsection*{Chequeo Órganos}')
                for key, value in consulta.cheqOrganos.items():
                    archivoHistorias.write(u'\\textbf{%s:} %s\n'%(key.capitalize(), value.capitalize()))
                archivoHistorias.write(u'\\textbf{Diagnóstico:} %s\n'%consulta.diagnostico)
                archivoHistorias.write(u'\\textbf{Tratamiento:} %s'%consulta.tratamiento.replace(' ', '\n'))

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
        root = self.root
        nStr = self.NOMBRE.get()
        try:
            if nStr =="":
                raise NameError('ERROR: Ingrese un nombre para el paciente.')
            elif not root.pacientes.has_key(nStr):
                raise NameError('ERROR: El paciente no existe en la base de datos')
            paciente= root.pacientes[nStr]

            archivoFormulas = open(self.SRCDIR+"formula_"+nStr.replace(' ','')+".txt", "w", encoding='latin-1')
            archivoFormulas.write(u'Paciente: %s, ID %s:\n'%(nStr, paciente.datosPersonales['id']))
            consultas = paciente.historia.consultas
            print(consultas.has_key(str(date.today())))
            if len(consultas)==0:
                raise IndexError(u'Aún no existen fórmulas para el paciente.')
            fechas = [datetime.strptime(dstr, '%Y-%m-%d') for dstr in consultas.keys()]
            ultimaConsulta = max(fechas)
            ultimaFormula = consultas[str(ultimaConsulta.date())].tratamiento
            archivoFormulas.write(ultimaFormula)
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

    def adicionarPaciente(self, datos_dict, root):
        datoGet = {dato:datos_dict[dato].get() for dato in datos_dict.keys()}
        try:
            if root.pacientes.has_key(datoGet['nombre']):
                raise NameError('Ya existe un paciente con el nombre: %s'%datoGet['nombre'])
            root.pacientes[datoGet['nombre']] = Paciente()
            for datoKey, datoVal in datoGet.items():
                root.pacientes[datoGet['nombre']].datosPersonales[datoKey] = datoVal
            transaction.commit()
            self.crearHistoriaWindow(root.pacientes[datoGet['nombre']])
        except NameError as ne:
            self.showErrorMsg(ne.args[0])
    def test(self):
        root = self.root
        root.pacientes['Jane Doe'].historia.mostrarAntecedentes()
    def modificarPaciente(self, datos_dict, root):
        datoGet = {dato:datos_dict[dato].get() for dato in datos_dict.keys()}
        try:
            if not root.pacientes.has_key(datoGet['nombre']):
                raise NameError('No existe un paciente con el nombre: %s para ser modificado'%datoGet['nombre'])
            root.pacientes[datoGet['nombre']] = Paciente()
            for datoKey, datoVal in datoGet.items():
                root.pacientes[datoGet['nombre']].datosPersonales[datoKey] = datoVal
            transaction.commit()
            self.showDoneMsg('El paciente %s ha sido modificado con exito'%datoGet['nombre'])
        except NameError as ne:
            self.showErrorMsg(ne.args[0])
    def adicionarAntecedentes(self, antec_dict, paciente):
        datoGet = {dato:antec_dict[dato].get() for dato in antec_dict.keys()}
        paciente.historia.adicionarAntecedentes(datoGet)
        self.showDoneMsg('El paciente %s ha sido agregado con exito'%paciente.datosPersonales['nombre'])
    def adicionarPacienteWindow(self):
        root = self.root
        dummyPaciente = Paciente()
        datos = dummyPaciente.datosPersonales.keys()
        popUp = Toplevel()
        popUp.title('Adicionar Paciente')
        datoLabels = [Label(popUp, text=dato.capitalize()) for dato in datos]
        datoSpaces = {dato:Entry(popUp) for dato in datos}
        [label.grid(row=2+i, column=1) for i, label in enumerate(datoLabels)]
        [space.grid(row=2+i, column=2) for i, space in enumerate(datoSpaces.values())]
        passFunc = lambda : self.adicionarPaciente(datoSpaces, root)
        adicionarPacienteButton = Button(popUp, text='Adicionar', command = passFunc)
        adicionarPacienteButton.grid(row = len(datos)+2, column = 1)
        closeButton = Button(popUp,text='Cerrar', command=popUp.destroy)
        closeButton.grid(row=len(datos)+2, column=2)
    def modificarPacienteWindow(self):
        root = self.root
        dummyPaciente = Paciente()
        datos = dummyPaciente.datosPersonales.keys()
        popUp = Toplevel()
        popUp.title('Modificar Paciente')
        datoLabels = [Label(popUp, text=dato.capitalize()) for dato in datos]
        datoSpaces = {dato:Entry(popUp) for dato in datos}
        [label.grid(row=2+i, column=1) for i, label in enumerate(datoLabels)]
        [space.grid(row=2+i, column=2) for i, space in enumerate(datoSpaces.values())]
        passFunc = lambda : self.modificarPaciente(datoSpaces, root)
        modificarPacienteButton = Button(popUp, text='Modificar', command = passFunc)
        modificarPacienteButton.grid(row = len(datos)+2, column = 1)
        closeButton = Button(popUp,text='Cerrar', command=popUp.destroy)
        closeButton.grid(row=len(datos)+2, column=2)
    def crearHistoriaWindow(self, paciente):
        root = self.root
        paciente.crearHistoria()
        datos = paciente.historia.antecedentes.keys()
        popUp = Toplevel()
        popUp.title('Adicionar Antecedentes para %s'%paciente.datosPersonales['nombre'])
        datoLabels = [Label(popUp, text=dato.capitalize()) for dato in datos]
        datoSpaces = {dato:Entry(popUp) for dato in datos}
        [label.grid(row=2+i, column=1) for i, label in enumerate(datoLabels)]
        [space.grid(row=2+i, column=3) for i, space in enumerate(datoSpaces.values())]
        passFunc = lambda : self.adicionarAntecedentes(datoSpaces, paciente)
        adicionarAntecedentesButton = Button(popUp, text='Adicionar', command = passFunc)
        adicionarAntecedentesButton.grid(row = len(datos)+2, column = 1)
        closeButton = Button(popUp,text='Cerrar', command=popUp.destroy)
        closeButton.grid(row=len(datos)+2, column=3)
    def guardarConsulta(self, consulta, info):
        motivo = info[0]
        consulta.motivo = motivo
        toFill = [consulta.revisionSistemas, consulta.examenFisico, consulta.cheqOrganos]
        for dic, targ in zip(info[1:-2], toFill):
            dictGet = {key:dic[key].get(1.0, END) for key in dic.keys()}
            for key, value in dictGet.items():
                targ[key] = value
        diagnost = info[-2]
        tratam = info[-1]
        consulta.diagnostico = diagnost
        consulta.tratamiento = tratam

        transaction.commit()
        self.showDoneMsg(u'La consulta se ha guardado con éxito.\nPuede cerrar la ventana')
        return consulta
    def crearNuevaConsultaWindow(self):
        root = self.root
        nombre = self.NOMBRE.get()
        try:
            if nombre=='':
                raise NameError("Por favor introduzca un nombre para el paciente.")
            elif not root.pacientes.has_key(nombre):
                raise NameError("El paciente no existe en la base de datos.")
            paciente = root.pacientes[nombre]
            consulta = Consulta()
            rS = consulta.revisionSistemas.keys()
            eF = consulta.examenFisico.keys()
            cO = consulta.cheqOrganos.keys()
            popUp = Toplevel()
            popUp.title('Consulta de %s, el %s'%(nombre, consulta.fecha))
            motivoLabel = Label(popUp, text = 'Motivo', font='Helvetica 18 bold')
            motivoLabel.grid(row=2, column=1)
            motivoSpace = ScrolledText(popUp, height=2, width=30)
            motivoSpace.grid(row=2, column=2)
            rSTitle = Label(popUp, text = u'Revisión Sistemas', font='Helvetica 18 bold')
            rSTitle.grid(row=3, column = 1)
            rSLabels = [Label(popUp, text=dato.capitalize()) for dato in rS]
            rSSpaces = {dato:ScrolledText(popUp, height=2, width=30) for dato in rS}
            [label.grid(row=4+i, column=1) for i, label in enumerate(rSLabels)]
            [space.grid(row=4+i, column=2) for i, space in enumerate(rSSpaces.values())]

            eFTitle = Label(popUp, text = u'Examen Físico', font='Helvetica 18 bold')
            eFTitle.grid(row=3, column = 3)
            eFLabels = [Label(popUp, text=dato.capitalize()) for dato in eF]
            eFSpaces = {dato:ScrolledText(popUp, height=2, width=30) for dato in eF}
            [label.grid(row=4+i, column=3) for i, label in enumerate(eFLabels)]
            [space.grid(row=4+i, column=4) for i, space in enumerate(eFSpaces.values())]


            cOTitle = Label(popUp, text = u'Chequeo Órganos', font='Helvetica 18 bold')
            cOTitle.grid(row=3, column = 5)
            cOLabels = [Label(popUp, text=dato.capitalize()) for dato in cO]
            cOSpaces = {dato:ScrolledText(popUp, height=2, width=30) for dato in cO}
            [label.grid(row=4+i, column=5) for i, label in enumerate(cOLabels)]
            [space.grid(row=4+i, column=6) for i, space in enumerate(cOSpaces.values())]

            diagLabel = Label(popUp, text = u'Diagnóstico', font='Helvetica 18 bold')
            diagLabel.grid(row = 5 + len(rS) , column = 1)
            diagSpace = ScrolledText(popUp, height=2, width=30)
            diagSpace.grid(row = 5 + len(rS), column = 2)
            tratamLabel = Label(popUp, text = 'Tratamiento', font='Helvetica 18 bold')
            tratamLabel.grid(row = 5 + len(rS), column = 3)
            tratamSpace = ScrolledText(popUp, height=2, width=30)
            tratamSpace.grid(row = 5 + len(rS), column = 4)
            toDo = lambda: paciente.historia.adicionarConsulta(self.guardarConsulta(consulta, [motivoSpace.get(1.0, END), rSSpaces, eFSpaces, cOSpaces, diagSpace.get(1.0, END), tratamSpace.get(1.0, END)]))
            allSave = Button(popUp, text='Guardar', command = toDo, font='Helvetica 18 bold')
            allSave.grid(row= 5 + len(rS), column = 5)
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

        self.GENFORM = Button(self, text=u'Fórmula', command=self.getFormulaFromName)
        self.GENFORM.grid(row=3, column = 4)

        self.CRCONSULTA = Button(self, text='Nueva Consulta', command = self.crearNuevaConsultaWindow)
        self.CRCONSULTA.grid(row = 4, column = 4)

        self.LIMPIAR = Button(self, text='Limpiar', command = self.clearNameField)
        self.LIMPIAR.grid(row = 2, column=4)

        self.ADDPACIENTE = Button(self, text='Adicionar Paciente', command= self.adicionarPacienteWindow)
        self.ADDPACIENTE.grid(row = 4, column = 1)

        self.MODPACIENTE = Button(self, text='Modificar Paciente', command= self.modificarPacienteWindow)
        self.MODPACIENTE.grid(row = 4, column = 3)

        self.QUIT = Button(self)
        self.QUIT["text"] = "Salir"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.grid(row=3, column = 1)

    SRCDIR = './'
    RESDIR = './res/'
    name = ""

    def __init__(self, master=None):
        self.root=self.createConnectionToDB()
        Frame.__init__(self, master)
        #default_font = master.nametofont("TkDefaultFont")
        #default_font.configure(size=48)
        master.option_add( "*font", "Arial 14 bold" )

        master.title("Generar Documentos")
        master.geometry('700x400')
        self.pack()
        self.createWidgets()


root = Tk()
app = Application(root)
app.mainloop()
root.destroy()
#TODO: Fancy python string tamplates for both documents. Include all patients' data in the history.
