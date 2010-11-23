# -*- coding:utf-8 -*-


from xml.dom.minidom import *
from util.constants import *


class ResultParser:
    
    def __init__(self, results):
        self.results = results
        self.doc = Document()
    
    def create_header(self):
        html = self.doc.createElement('html')
        header = self.doc.createElement('header')
        title = self.doc.createElement('title')
        title_text = self.doc.createTextNode("Tabelas com os resultados da simulacao")
        body = self.doc.createElement('body')
        self.doc.appendChild(html)
        html.appendChild(header)
        html.appendChild(body)
        header.appendChild(title)
        title.appendChild(title_text)
        
        return body
    
    def create_table(self, type, name):
        table = self.doc.createElement('table')
        table.setAttribute('cellspacing', '0')
        table.setAttribute('cellpadding', '4')
        table.setAttribute('border', '1')
        
        tr = self.doc.createElement('tr')
        th = self.doc.createElement('th')
        th.setAttribute('align', 'center')
        th.setAttribute('colspan', '31')
        th.appendChild(self.doc.createTextNode("Tabela com os resultados para a politica de atendimento " + name))
        tr.appendChild(th)
        table.appendChild(tr)
        
        tr = self.doc.createElement('tr')
        th = self.doc.createElement('th')
        th.setAttribute('align', 'center')
        th.setAttribute('style', 'font-weight: bold')
        th.appendChild(self.doc.createTextNode("uti."))
        tr.appendChild(th)
        headers = ['E[N1]', 'E[N2]', 'E[T1]', 'E[T2]', 'E[Nq1]', 'E[Nq2]', 'E[W1]', 'E[W2]', 'V(W1)', 'V(W2)']
        for header in headers:
            th = self.doc.createElement('th')
            th.setAttribute('align', 'center')
            th.setAttribute('colspan', '3')
            th.appendChild(self.doc.createTextNode(header))
            tr.appendChild(th)
        table.appendChild(tr)
        
        utilizations = self.results[type].keys()
        utilizations.sort()
        for utilization in utilizations:
            tr = self.doc.createElement('tr')
            td = self.doc.createElement('td')
            td.setAttribute('align', 'center')
            td.setAttribute('style', 'font-weight: bold')
            td.appendChild(self.doc.createTextNode(str(utilization)))
            tr.appendChild(td)
            for key in self.results[type][utilization]['simulator'].keys():
                td = self.doc.createElement('td')
                td.setAttribute('align', 'center')
                td.appendChild(self.doc.createTextNode(str(round(self.results[type][utilization]['analytic'][key], 5))))
                tr.appendChild(td)
                td = self.doc.createElement('td')
                td.setAttribute('align', 'center')
                td.appendChild(self.doc.createTextNode(str(round(self.results[type][utilization]['simulator'][key]['value'], 5))))
                tr.appendChild(td)
                td = self.doc.createElement('td')
                td.setAttribute('align', 'center')
                td.appendChild(self.doc.createTextNode(str(round((2.0*self.results[type][utilization]['simulator'][key]['c_i']/self.results[type][utilization]['simulator'][key]['value'])*100.0, 2)) + "%"))
                tr.appendChild(td)
            table.appendChild(tr)
            
        return table
    
    def parse(self):
        body = self.create_header()
        table_fcfs = self.create_table(FCFS, 'F.C.F.S')
        table_lcfs = self.create_table(LCFS, 'L.C.F.S')
        table_lcfs.setAttribute('style', 'margin-top:100px')
        body.appendChild(table_fcfs)
        body.appendChild(table_lcfs)
    
    def write(self, filename):
        file = open(filename, "w")
        print >>file, self.doc.toprettyxml()
        file.close()
        