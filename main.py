#!/usr/bin/python
# -*- coding: utf-8 -*-

####################
# Copywright 2017-2018 Marcin Pustuła
# pustula.marcin@gmail.com
####################

from lmfit import Minimizer, Parameters, fit_report
#import numpy as np
from numpy import inf, float64, array, sqrt
#import pandas as pd
from pandas import DataFrame, read_csv, read_json
import json

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os.path
import time
        
import mainwindow, new_dialog, average, about
from subprocess import call
from PIL import Image,ImageQt ##when using with PyQt4, need to change 
                              ## in /usr/lib/python3/dist-packages/PIL/ImageQt.py
                              ## from 'except ImportError'  to 'except (ImportError, RuntimeError)'



def excepthookA(excType, excValue, tracebackobj):
    """
    Global function to catch unhandled exceptions.
    
    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """
    
    separator = '-' * 40
    logFile = "errors.log"
    notice ="An unhandled exception occurred.\n"
    versionInfo="2.0"
    timeString = time.strftime("%Y-%m-%d, %H:%M:%S")

    errmsg = '%s: \n%s' % (str(excType), str(excValue))
    sections = [timeString,separator, errmsg, separator]
    msg = '\n'.join(sections)
    try:
        f = open(logFile, "a")
        f.write(msg)
        f.write(versionInfo)
        f.close()
    except IOError:
        pass
    errorbox = QtWidgets.QMessageBox()
    errorbox.setText(str(notice)+str(msg))
    errorbox.exec_()


sys.excepthook = excepthookA

class App(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)
      
        self.actionNew_File.triggered.connect(self.new_file)
        self.actionNew_set_2.triggered.connect(self.create_set)
        self.actionSave_as.triggered.connect(self.save_file_as)
        self.actionSave.triggered.connect(self.save_file)
        self.actionOpen_file.triggered.connect(self.open_file)
        self.actionEdit_file_info.triggered.connect(self.edit_file)
        self.actionEdit_set.triggered.connect(self.edit_set)
        self.actionDelete_point.triggered.connect(self.delete_set)
        self.actionQuit.triggered.connect(self.quit_app)
        self.actionCalculate_average_value.triggered.connect(self.calc_av)
        self.read_file.clicked.connect(self.read_from_file)
        self.plot_input.clicked.connect(self.plot_input_data)
        self.clear.clicked.connect(self.clear_input)
        self.start.clicked.connect(self.start_fitting)
        self.setDef.clicked.connect(self.save_default_plot_templ)
        self.restoreDef.clicked.connect(self.restore_default_plot_templ)
        self.listWidget.itemClicked.connect(self.click_set)
        self.tabWidget.currentChanged.connect(self.click_file)
        
        self.input_table.cellDoubleClicked.connect(self.df_changed)
        
        self.tabWidget.tabCloseRequested['int'].connect(self.close_request)
        
        print(QtWidgets.QStyleFactory.keys())
        
        self.actionAbout.triggered.connect(self.about)
        self.actionCopy_to_clipboard.triggered.connect(self.copy_image)
        
        copyAction = QtWidgets.QAction("Copy image to clipboard", self.plot)
        copyAction.triggered.connect(self.copy_image)
        self.plot.addAction(copyAction)
        
       # save_asAction = QtWidgets.QAction("Save image as", self.plot)
       # save_asAction.triggered.connect(self.copy_image)
       # self.plot.addAction(save_asAction)        
        
        
        table_width=self.input_table.width()
        
        self.input_table.setColumnWidth(0,table_width/2.3)
        self.input_table.setColumnWidth(1,table_width/2.3)
        self.input_table.setColumnWidth(2,table_width/2.3)
        
        fit_templ=open('gnuplot/fit_templ.gp','r').read()
        
        self.textEdit_2.setText(fit_templ)
        
        
        self.files={}
        
        self.current_file=None   
        
        #self.new_file()
        self.set_enabled()
        
    def about(self):
        
        about=About(self)
        about.show()
        
    def calc_av(self):
        av_dialog=Average(self)
        
        
        kd_dicts=[{'name':x.name, 'kd':x.fit_params['Kd'],'kd_err':x.kd_err} for x in self.current_file.sets.values()]
        av_dialog.file_name.setText(self.current_file.name)
        av_dialog.tableWidget.clearContents()
        av_dialog.tableWidget.setRowCount(len(kd_dicts))
        
        for i, item in enumerate(kd_dicts):        
            av_dialog.tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(item['name']))
            av_dialog.tableWidget.setItem(i,1,QtWidgets.QTableWidgetItem('{:>10.6f}'.format(item['kd'])))
            av_dialog.tableWidget.setItem(i,2,QtWidgets.QTableWidgetItem('{:>10.6f}'.format(item['kd_err'])))
            av_dialog.tableWidget.setItem(i,3,QtWidgets.QTableWidgetItem('Yes'))
        
        av_dialog.show()

        
    def copy_image(self):
        image=self.plot.pixmap()
        QtWidgets.QApplication.clipboard().setPixmap(image)
        
    def set_enabled(self):
        
        no_file_widgets=[self.frame,self.menuPoint,self.actionEdit_file_info,self.actionSave,self.actionSave_as,self.menuPlot,
                         self.actionCalculate_average_value]
        no_point_widgets=[self.scrollArea,self.actionEdit_set,self.actionDelete_point,self.actionCalculate_average_value,
                          self.actionCopy_to_clipboard]
        #point_required_widgets=[self.scrollArea,self.menuPoint,self.]
        if not self.files:
            [x.setEnabled(False) for x in no_file_widgets]
        else:
            if not self.current_file.current_set:
                [x.setEnabled(True) for x in no_file_widgets]
                [x.setEnabled(False) for x in no_point_widgets]
            else:
                [x.setEnabled(True) for x in no_file_widgets]
                [x.setEnabled(True) for x in no_point_widgets]
                
        
    def new_file(self):
        
        newFileDialog=New(self)
        newFileDialog.show()

        if newFileDialog.exec_():
            file_name=newFileDialog.fileName.text()
            comment=newFileDialog.fileComment.toPlainText()
            point_name=newFileDialog.PointName.text()
        
            if file_name!='':
                new_file=SampleFile(self,file_name)
            else:
                new_file=SampleFile(self)
                
            self.files[new_file.name]=new_file
            self.current_file=new_file
            new_file.comment=comment

            tab = QtWidgets.QWidget()
            tab.setObjectName(new_file.name)
            self.tabWidget.addTab(tab, new_file.name)      
            
            self.tabWidget.setCurrentWidget(tab)
            
            if point_name!="":
                self.current_file.add_set(point_name)
                
            self.activate_file(self.current_file)

    

    def edit_file(self):
        
        newFileDialog=New(self)
        newFileDialog.fileName.setText(self.current_file.name)
        newFileDialog.fileComment.setText(self.current_file.comment)
        newFileDialog.PointName.setEnabled(False)
        newFileDialog.show()

        if newFileDialog.exec_():
           file_name=newFileDialog.fileName.text()
           comment=newFileDialog.fileComment.toPlainText()

           self.current_file.change_name(file_name)
           
           self.current_file.comment=comment
           
           self.tabWidget.currentWidget().setObjectName(file_name)
           self.tabWidget.setTabText(self.tabWidget.currentIndex(),file_name)
           
           self.activate_file(self.current_file)
        
        
    def click_file(self):
        current_widget=self.tabWidget.currentWidget()
        if current_widget:
            current_file_name=current_widget.objectName()

            current_file=self.files[current_file_name]
        
            self.current_file=current_file
            self.activate_file(current_file)
        else:
            self.listWidget.clear()
            self.clear_input()
            self.set_enabled()
        

    
        
    def activate_file(self,target_file):
        
        self.listWidget.clear()
        if target_file.sets:
            self.listWidget.addItems(target_file.sets.keys())
        
        self.label_file_name.setText(target_file.name)
        self.label_comment.setText(target_file.comment)
        
        self.select_set(target_file.current_set)
        if self.current_file.saved:
            self.label_saved.setText('')
        else:
            self.label_saved.setText('(modified)')
        self.set_enabled()
        
    def select_set(self,set_obj):
        
        #self.listWidget.setCurrentItem(self.current_file.current_set)
        if set_obj:
            for index in range(self.listWidget.count()):
                name=self.listWidget.item(index).text()
                if name==set_obj.name:
                    self.listWidget.setCurrentRow(index)
                    self.click_set()
                    break
        else:
            self.clear_input()
    
    def click_set(self):
        curr_item=self.listWidget.currentItem()
        item=curr_item.text()
        obj=self.current_file.sets[item]
        
        self.data_fit=obj
        self.current_file.current_set=obj
        self.load_file()
        self.set_enabled()
        
        
    def create_set(self):
        
        newFileDialog=New(self)
        newFileDialog.fileName.setText(self.current_file.name)
        newFileDialog.fileName.setEnabled(False)
        newFileDialog.fileComment.setText(self.current_file.comment)
        newFileDialog.fileComment.setEnabled(False)
        newFileDialog.show()

        if newFileDialog.exec_():
           point_name=newFileDialog.PointName.text()
            
           if point_name=='':
               new_set_name=self.current_file.add_set()
           else:
               new_set_name=self.current_file.add_set(point_name)
                     
           self.activate_file(self.current_file)
        self.set_enabled()
           
    def delete_set(self):
        curr_item=self.listWidget.currentItem()
        item=curr_item.text()
        obj=self.current_file.sets[item]
        
        ans=QtWidgets.QMessageBox.question(self, 'Delete point', "Do you really want to delete selected point?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ans == QtWidgets.QMessageBox.Yes:
            self.current_file.delete_set(obj)
            self.activate_file(self.current_file)
        
    def edit_set(self):
        
        newFileDialog=New(self)
        newFileDialog.fileName.setText(self.current_file.name)
        newFileDialog.fileName.setEnabled(False)
        newFileDialog.fileComment.setText(self.current_file.comment)
        newFileDialog.fileComment.setEnabled(False)
        newFileDialog.PointName.setText(self.data_fit.name)
        newFileDialog.show()
        
        if newFileDialog.exec_():
            point_name=newFileDialog.PointName.text()
            
            if point_name!='':
                self.data_fit.change_name(point_name)
                self.activate_file(self.current_file)
        


    def open_file(self):
        cwd=os.getcwd()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', cwd,'(*.bcc)')[0]
        if fileName:
            width=self.plot.width()
            height=self.plot.height()
            fit_templ=self.textEdit_2.toPlainText()
                
            new_file=SampleFile(self)
            new_file.read_from_file(fileName,width,height,fit_templ)
            self.files[new_file.name]=new_file
            self.current_file=new_file
    
            tab = QtWidgets.QWidget()
            tab.setObjectName(new_file.name)
            self.tabWidget.addTab(tab, new_file.name)      
            self.tabWidget.setCurrentWidget(tab)
            
            self.activate_file(self.current_file)
            self.listWidget.setCurrentRow(0)
            self.click_set()
            self.current_file.set_saved(True)
        
        
    def save_file(self):
        self.save_file_obj(self.current_file)
        
    def save_file_as(self):
        self.save_file_obj_as(self.current_file)
        
    def save_file_obj(self,file_obj):
        filename=file_obj.filename
        if filename:
            file_obj.save(filename)
        else:
            self.save_file_obj_as(file_obj)

    def save_file_obj_as(self,file_obj):
        cwd=os.getcwd()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', cwd, '(*.bcc)')[0]
        if fileName:        
            file_obj.save(fileName)
            QtWidgets.QMessageBox.information(self, 'Saving file', "The file has been saved succesfully.", QtWidgets.QMessageBox.Ok)

    def closeEvent(self,evnt):
        evnt.ignore()
        self.quit_app()

    def quit_app(self):
        ans=None
        for x in reversed(range(self.tabWidget.count())):
            answer=self.close_request(x)
            if answer=='stop':
                ans='stop'
                break
            
        if ans!='stop':
            sys.exit()
        
    def close_request(self,index):
        widget = self.tabWidget.widget(index)
        file_name=widget.objectName()
        file_obj=self.files[file_name]
        return self.close_file(file_obj,index)
        
    def close_file(self,file_obj,index):
        if file_obj.saved:
            self.files.pop(file_obj.name)
            self.removeTab(index)
        else:
            ans=QtWidgets.QMessageBox.question(self, 'Close file', 'The file "'+file_obj.name+'"  has been modified. Do you want to save the changes?', 
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            if ans == QtWidgets.QMessageBox.Yes:
                self.save_file_obj(file_obj)
                self.files.pop(file_obj.name)
                self.removeTab(index)
            elif ans == QtWidgets.QMessageBox.No:
                self.files.pop(file_obj.name)
                self.removeTab(index)
            else:
                return "stop"
            
    def removeTab(self, index):
        widget = self.tabWidget.widget(index)
        if widget is not None:
            widget.deleteLater()
        self.tabWidget.removeTab(index)
        
    def load_file(self):
        if not self.data_fit.data_df.empty:
            self.fill_from_df(self.data_fit.data_df)
            self.plot_pic(self,picture=self.data_fit.picture)
        else:
            self.clear_input()
            
        self.textEdit.setText(self.data_fit.fit_result)

        if self.data_fit.params:        
            p0=self.data_fit.params['P0']
            self.protein.setValue(p0.value)
            Nsc=self.data_fit.params['Nsc']
            self.Nfactor.setValue(Nsc.value)
            kd=self.data_fit.params['Kd']
            self.kd.setValue(kd.value)
            self.kd_fix.setChecked(not kd.vary)
            
            if kd.min!=-inf:
                self.kd_is_min.setChecked(True)
                self.kd_min.setValue(kd.min)
            else:
                self.kd_is_min.setChecked(False)
                self.kd_min.setValue(0.0)
    
            if kd.max!=inf:
                self.kd_is_max.setChecked(True)
                self.kd_max.setValue(kd.max)
            else:
                self.kd_is_max.setChecked(False)
                self.kd_max.setValue(0.0)
                
            dm=self.data_fit.params['Dm']
            self.dm.setValue(dm.value)
            self.dm_fix.setChecked(not dm.vary)
            
            if dm.min!=-inf:
                self.dm_is_min.setChecked(True)
                self.dm_min.setValue(dm.min)
            else:
                self.dm_is_min.setChecked(False)
                self.dm_min.setValue(0.0)
    
            if dm.max!=inf:
                self.dm_is_max.setChecked(True)
                self.dm_max.setValue(dm.max)
            else:
                self.dm_is_max.setChecked(False)
                self.dm_max.setValue(0.0)
                
    def df_changed(self):
        self.current_file.set_saved(False)
        self.read_from_table()
            
    def read_from_file(self):
        cdir=os.getcwd()
        f_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose file', cdir,'CSV (*.csv)')[0]
        if f_name:              
            fil_name=os.path.relpath(str(f_name))
        
            input_df=read_csv(fil_name,sep=';')
            #self.input_table.setRowCount(len(input_df))
            self.fill_from_df(input_df)
        
    def fill_from_df(self,input_df):

        self.input_table.clearContents()
        for i, item in enumerate(input_df.index.tolist()):
            ligand=input_df.loc[item,'X']
            h=input_df.loc[item,'H']
            n=input_df.loc[item,'N']
        
            self.input_table.setItem(i,0,QtWidgets.QTableWidgetItem('{:>5.2f}'.format(ligand)))
            self.input_table.setItem(i,1,QtWidgets.QTableWidgetItem('{:>8.4f}'.format(h)))
            self.input_table.setItem(i,2,QtWidgets.QTableWidgetItem('{:>8.4f}'.format(n)))


    def read_from_table(self):
        data_df=DataFrame(index=range(self.input_table.rowCount()),columns=['X','H','N'])
        
        for i in range(self.input_table.rowCount()):
            for j in range(self.input_table.columnCount()):
                item=self.input_table.item(i,j)
                if item:
                    text=item.text()
                    if text!='':
                        data_df.ix[i,j]=float(text)
                    
        data_df=data_df.dropna()
                              
        N_scalling=self.Nfactor.value()
        P_conc=self.protein.value() 
        
        self.data_df=data_df
        try:
            self.data_fit.prepare_df(data_df,N_scalling,P_conc)
        except:
            pass
        
    def plot_input_data(self):
        
        self.plot_pic('points')
    
    def plot_pic(self,dat='points',picture=None):
        self.read_from_table()

        width=self.plot.width()
        height=self.plot.height()

        if not picture:
            fit_templ=self.textEdit_2.toPlainText()
            picture=self.data_fit.prepare_plot(dat,width,height,fit_templ)
        
        picture0=QtGui.QPixmap.fromImage(ImageQt.ImageQt(picture))
        
        picture = picture0.scaled(width,height, QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation)
        self.plot.setPixmap(picture)
        
    def clear_input(self):
        self.current_file.set_saved(False)
        self.input_table.clearContents()
        self.plot.setPixmap(QtGui.QPixmap(''))
        self.textEdit.setText('')
                
    def read_params(self):
        p_conc=self.protein.value()
        if self.p_is_min.isChecked():
            p_min=self.p_min.value()
        else:
            p_min=None
        if self.p_is_max.isChecked():
            p_max=self.p_max.value()
        else:
            p_max=None
            
        N_scaling=self.Nfactor.value()
        
        Kd=self.kd.value()
        if self.kd_is_min.isChecked():
            kd_min=self.kd_min.value()
        else:
            kd_min=None
        if self.kd_is_max.isChecked():
            kd_max=self.kd_max.value()
        else:
            kd_max=None
            
        Dm=self.dm.value()
        if self.dm_is_min.isChecked():
            dm_min=self.dm_min.value()
        else:
            dm_min=None
        if self.dm_is_max.isChecked():
            dm_max=self.dm_max.value()
        else:
            dm_max=None

        params = Parameters()
        params.add('Dm', value=Dm,vary=not self.dm_fix.isChecked(),min=dm_min,max=dm_max)
        params.add('Kd', value=Kd,vary=not self.kd_fix.isChecked(),min=kd_min,max=kd_max)
        params.add('P0', value=p_conc,vary=not self.p_fix.isChecked(),min=p_min,max=p_max)
        params.add('Nsc',value=N_scaling,vary=False)
        
        self.data_fit.set_params(params)

    def start_fitting(self):
        self.current_file.set_saved(False)
        self.read_from_table()
        self.read_params()

        fit_result=self.data_fit.fitting()
        text=fit_result[0]
        self.textEdit.setText(text)      
        self.plot_pic('fit')
        
    def save_default_plot_templ(self):
        fit_templ=self.textEdit_2.toPlainText()
        templ_file=open('gnuplot/fit_templ.gp','w')
        templ_file.write(fit_templ)
        templ_file.close()
        
    def restore_default_plot_templ(self):
        orig_file=open('gnuplot/fit_templ_original.gp','r').read()
        templ_file=open('gnuplot/fit_templ.gp','w')
        templ_file.write(orig_file)
        templ_file.close()
        self.textEdit_2.setText(orig_file)
        

class New(QtWidgets.QDialog, new_dialog.Ui_New):
    
    def __init__(self, parent=None):
        super(New, self).__init__(parent)
        self.setupUi(self)
        
class About(QtWidgets.QDialog, about.Ui_Dialog):
    
    def __init__(self, parent=None):
        super(About, self).__init__(parent)
        self.setupUi(self)
        
class Average(QtWidgets.QDialog, average.Ui_Dialog):
    def __init__(self, parent=None):
        super(Average, self).__init__(parent)
        self.setupUi(self)
        self.tableWidget.cellDoubleClicked.connect(self.select_row)
        self.pushButton_2.clicked.connect(self.calc_avg)
        
        self.tableWidget.setColumnWidth(0,200)
        self.tableWidget.setColumnWidth(1,200)
        self.tableWidget.setColumnWidth(2,200)
        self.tableWidget.setColumnWidth(3,100)
        
    def select_row(self):
        row_id=self.tableWidget.currentRow()
        item_text=self.tableWidget.item(row_id,3).text()
        if item_text=='Yes':
            new_text='No'
        elif item_text=='No':
            new_text='Yes'
        self.tableWidget.setItem(row_id,3,QtWidgets.QTableWidgetItem(new_text))
        
    def calc_avg(self):
        a=0
        b=0
        
        for i in range(self.tableWidget.rowCount()):
            inc=self.tableWidget.item(i,3).text()
            if inc=='Yes':
                kd=float(self.tableWidget.item(i,1).text())
                kd_err=float(self.tableWidget.item(i,2).text())
                a=a+kd/(kd_err**2)
                b=b+1/(kd_err**2)
        
        if not b==0:
            kd_avg=a/b
            err_avg=b**(-0.5)
    
            self.lineEdit.setText('{:>10.6f}'.format(kd_avg))
            self.lineEdit_2.setText('{:>10.6f}'.format(err_avg))
        else:
            self.lineEdit.setText('error')
            self.lineEdit_2.setText('error')
        
        
class SampleFile(object):
    
    def __init__(self,parent,name='File',sets={}):
        self.parent=parent
        self.set_name(name)
        self.sets={}
        self.comment=''
        self.saved=False
        self.filename=''
        #self.names=[x.name for x in self.sets]
        
        self.current_set=None

    def set_saved(self,x=True):
        self.saved=x
        if x:
            self.parent.label_saved.setText('')
        else:
            self.parent.label_saved.setText('(modified)')
        
    def set_name(self,name):
        if not name in self.parent.files.keys():
            self.name=name
        else:
            i=1
            while 1:
                name_mod=name+'_'+'%d'%i
                if not name_mod in self.parent.files.keys():
                    self.name=name_mod
                    break
                else:
                    i=i+1
        self.set_saved(False)
        return self.name
        
    def change_name(self,new_name):
        old_name=self.name
        new_name_final=self.set_name(new_name)
        
        self.parent.files[new_name_final]=self.parent.files.pop(old_name)
        
    def add_set(self,name='set'):
        new_set=FitData(self,name)
        self.sets[new_set.name]=new_set
        self.current_set=new_set
        self.set_saved(False)
        return new_set.name
        
    def delete_set(self,set_obj):
        self.sets.pop(set_obj.name)
        self.set_saved(False)
        self.current_set=None
        
            
    def save(self,filename):
        
        json_dict={'name':self.name,'comment':self.comment}
        sets_dict={}
        for item in self.sets:
            sets_dict[item]=self.sets[item].json_dump()
        json_dict['sets']=sets_dict
        with open(filename,'w') as output:
            json.dump(json_dict,output)
        self.set_saved(True)
        self.filename=filename
            
    def read_from_file(self,filename,plot_w,plot_h,pl_templ):
        
        with open(filename,'r') as input:
            json_dict=json.load(input)
            
        self.set_name(json_dict['name'])
        self.comment=json_dict['comment']
        
        self.parent.files[self.name]=self
        
        sets_dict=json_dict['sets']        
        for item in sets_dict:
            set_json=sets_dict[item]
            set_dict=json.loads(set_json)
            name=set_dict['name']
            fit_result=set_dict['fit_result']
            fit_params=set_dict['fit_params']
            df_json=set_dict['df']
            df=read_json(df_json)
            params=Parameters()
            params.loads(set_dict['params'])
            try:
                kd_err=float(set_dict['kd_err'])
            except KeyError:
                kd_err=0
            
            fit_obj=FitData(self,name,df,params,fit_result,fit_params,kd_err)

            self.sets[fit_obj.name]=fit_obj
        self.set_saved(True)
        self.filename=filename


class FitData(object):
    
    
    def __init__(self,parent,name='set',data=DataFrame(),params=None,result=None,fit_params=None, \
                    kd_err=0,picture=None):
        self.parent=parent
        self.set_name(name)
        #self.parent.names.append(name)
        #self.parent.sets[name]=self
        self.data_df=data
        self.params=params
        self.fit_result=result
        self.fit_params=fit_params
        self.picture=picture
        self.kd_err=kd_err
        
            
    def set_name(self,name='set'):
        if not name in self.parent.sets.keys():
            self.name=name
        else:
            i=1
            while 1:
                name_mod=name+'_'+'%d'%i
                if not name_mod in self.parent.sets.keys():
                    self.name=name_mod
                    break
                else:
                    i=i+1
        self.parent.set_saved(False)
        return self.name
        
        
    def change_name(self,new_name):
        old_name=self.name       
        new_name_final=self.set_name(new_name)
        self.parent.sets[new_name_final]=self.parent.sets.pop(old_name)
        
        
        
    def prepare_df(self,data_df,N_sc,P_con):
         
        data_df['dH']=data_df['H']-data_df['H'][0]
        data_df['dN']=data_df['N']-data_df['N'][0]
        
        data_df['L_conc']=data_df['X']*P_con
        data_df['D']=(0.5*((data_df['dH'])**2+(N_sc**2)*(data_df['dN'])**2))**0.5
        
        self.data_df=data_df
        
        return data_df
                
    def prepare_plot(self,dat='points',width=512,height=512,fit_templ=None):
        

            
        plot_df=self.data_df[['L_conc','D']]
        plot_df.to_csv('gnuplot/temp.dat',sep=' ',header=False,index=False)
        #fit_templ=open('gnuplot/fit_templ.gp','r').read()
                
        ratio=height/width
        
        if dat=='fit':
            kd=self.fit_params['Kd']
            dm=self.fit_params['Dm']
            p_co=self.fit_params['P0']
            fit_gp=fit_templ%(width,height,ratio,kd,dm,p_co,'')
        else:
            fit_gp=fit_templ%(width,height,ratio,1,1,1,'#')
        fit_out=open('gnuplot/fit.gp','w')
        fit_out.write(fit_gp)
        fit_out.close()
        os.chdir('gnuplot/')
        call(['gnuplot','fit.gp'])####Linux
        #call(['gnuplot/bin/gnuplot.exe','fit.gp'])####Windows
        os.chdir('..')
        
        self.picture=Image.open('gnuplot/fit.png')
        
        return self.picture
    
    def set_params(self,params):

        self.params=params
    
    def chemical_shift(params, x, data):
            """ model decaying sine wave, subtract data"""
            v = params.valuesdict()
            model = (v['Dm']*((v['Kd']+x+v['P0'])-sqrt((v['Kd']+x+v['P0'])**2-(4*v['P0']*x))))/(2*v['P0'])
            return model - data
        
    def fitting(self):
        
        x=array(self.data_df['L_conc'].values,dtype=float64)
        data=array(self.data_df['D'].values,dtype=float64)
         
      
        minner = Minimizer(FitData.chemical_shift, self.params, fcn_args=(x, data))
        result = minner.minimize()

        self.fit_result=fit_report(result)
        self.fit_params=result.params.valuesdict()
        self.kd_err=result.params['Kd'].stderr


        return (self.fit_result,result.params.valuesdict())
        
    def json_dump(self):
        
        if self.params:
            params_json=self.params.dumps()
        else:
            params_json=''
        json_dict={'name':self.name,'params':params_json,'fit_result':self.fit_result,
                   'fit_params':self.fit_params,'df':self.data_df.to_json(),'kd_err':str(self.kd_err)}
                   
        return json.dumps(json_dict)
        
        

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    qt_translator = QtCore.QTranslator()
    qt_translator.load("qt_en",QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
    app.installTranslator(qt_translator)
    
    app.setStyle(QtWidgets.QStyleFactory.create('Breeze'))
    

      
    form = App()
    form.show()
    app.exec_()
    
if __name__ == '__main__':
    main()

