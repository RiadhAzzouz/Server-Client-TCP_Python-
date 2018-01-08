#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = '192.168.43.158'        
PORT = 1301

import socket, sys, threading, time
import os

MyLock = threading.Lock()

def readID(line):   #LIRE ID DU STOCK.TXT
    x=""
    i=0;
    while line[i]!=" ":
        x+=line[i]
        i+=1

    return x
    
def readQt(line):      #LIRE QUANTITE DU STOCK.TXT
    x=""
    i=0
    j=0
    while line[i]!="\n":
        if line[i] ==" ":
            j+=1
        i+=1
        if j==2:
            if line[i]!='\n':
                x+=line[i]
        
    return x
    
def readPrix(line):   #LIRE PRIX DU STOCK.TXT
    x=""
    i=0
    while line[i]!=" ":
        i+=1
    j = i+1
    while line[j]!=" ":
        x+=line[j]
        j+=1

    return x

def openFile(filename):    #OUVRIR UN FICHIER DANS UNE LISTE
    f = open(filename,"r")
    lines = f.readlines()
    f.close()
    return lines



def readTotal(line):       #LIRE SOMME A PAYER DU FACTURE.TXT
    x=""
    i=0 
    while line[i]!=" ":
        i+=1
    j = i+1
    while line[j]!="\n":
        x+=line[j]
        j+=1
    return x

 
class ThreadClient(threading.Thread):
    
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connexion = conn
       
    def recevoirFacture(self):
        lines = openFile("d:/facture.txt")
        lines.reverse()
        x = readTotal(lines[0])
        self.connexion.send("Somme à payer : "+x+"\n")

    def consulterHisto(self):
        f = open("d:/histo.txt","r") 
        lines = f.read()
        f.close()
        self.connexion.send(lines)

    def consulterStock(self):
        self.connexion.send("Donner l'ID du produit :\n")
        x = self.connexion.recv(255)
        f = open('d:/Stock.txt','r')
        
        lines = f.readlines()
        f.close()

        b = False
        for line in lines:
            if readID(line) == x:
                b = True
                l = line
                break

        if b== False:
            self.connexion.send("Le produit n'existe pas \n")
        else:
            self.connexion.send(l)


    def consulterFacture(self):
        self.connexion.send("Donner l'ID du client :")
        x = self.connexion.recv(255)
        f = open("d:/facture.txt","r") 
        lines = f.readlines()
        f.close()

        l=""
        b = False
        for line in lines:
            if readID(line) == x:
                b = True
                l += line
                

        if b== False:
            self.connexion.send("La facture n'existe pas \n")
        else:
            self.connexion.send(l)


    def acheterProduit(self):

        self.connexion.send("Donner l'ID du produit :\n")
        x = self.connexion.recv(255)
        print x
        lines = openFile("d:/Stock.txt")
        b = False
        for line in lines:
            if readID(line) == x:
                b = True
                l = line
                break

        if b== False:
            self.connexion.send("Le produit n'existe pas \n")
            if MyLock.locked():
                MyLock.release()
            self.run()
        else:
            self.connexion.send(l+"Donner la quantité :\n")
            q = self.connexion.recv(255)
            self.connexion.send("Saisir votre ID :\n")
            id1 = self.connexion.recv(255)
            qt = readQt(l)
            w = readPrix(l)
            print "quantite demandée :"+ q +" ***** Stock : "+qt
            k = int(qt)-int(q)
            qn = str(k)
            if k >= 0:
                c = 0
                for i in lines:
                    if readID(i) == x:
                        w = readPrix(i)
                        newLine = x + " " + w + " " + qn + "\n" 
                        break
                    c+=1

                lines[c] = newLine
                fw = open("d:/Stock.txt","w")
                for line1 in lines:
                    fw.write(line1)
                fw.close()
                #AJOUT DANS FACTURE 
                somme = int(w) * int(q)
                line2 = id1 + " " + str(somme) + "\n"
                fa = open("d:/facture.txt","a")
                fa.write(line2)
                fa.close()
                #AJOUT DANS HISTORIQUE
                fah = open("d:/histo.txt","a")
                line2 = id1 + " " + x + " " + q + " " + "succes\n"
                fah.write(line2)
                fah.close()
                self.connexion.send("Operation effectuée avec succes\n")
                    
            
            else:
                #AJOUT DANS HISTORIQUE
                fah = open("d:/histo.txt","a")
                line2 = id1 + " " + x + " " + q + " " + "echec\n"
                fah.write(line2)
                fah.close()
                self.connexion.send("Vous avez dépasser la quantité disponible\n Réessayer(Y/N) ?\n")
                y = self.connexion.recv(255)
                if y in ('Y' , 'y'):
                    if MyLock.locked():
                        MyLock.release()
                    self.run()
                    
 
    def run(self):
        nom = self.getName()
        r = self.connexion.recv(255)
        print(r)
        if r == "1":
            self.consulterStock()
            self.run()
        if r == "2":
            self.consulterFacture()
            self.run()
        if r == "3":
            self.consulterHisto()
            self.run()
        if r == "4":
            print self.getName() + " Acquiring Lock \n"
            if not MyLock.acquire():
                print "Waiting ... \n"
            else:
                print self.getName() + " Lock Acquired \n"
                self.acheterProduit()            
                MyLock.release()            
            self.run()
        if r == "5":
            self.recevoirFacture()
            self.run()
        if r == "6":
            print("Client déconnecté...")
            #self.connexion.close()      # couper la connexion côté serveur
            del conn_client[nom]        # supprimer son entrée dans le dictionnaire
            print "Client %s déconnecté." % nom        # Chaque thread possède un nom
  



          

# Initialisation du serveur - Mise en place du socket :
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    mySocket.bind((HOST, PORT))
except socket.error:
    print "La liaison du socket à l'adresse choisie a échoué."
    sys.exit()
print "Serveur prêt, en attente de requêtes ..."
mySocket.listen(5)

# Attente et prise en charge des connexions demandées par les clients :
conn_client = {}                # dictionnaire des connexions clients
while 1:    
    connexion, adresse = mySocket.accept()
    # Créer un nouvel objet thread pour gérer la connexion :
    th = ThreadClient(connexion)
    th.start()
    # Mémoriser la connexion dans le dictionnaire : 
    it = th.getName()        # identifiant du thread
    conn_client[it] = connexion
    print "Client %s connecté, adresse IP %s, port %s." %\
           (it, adresse[0], adresse[1])
    # Dialogue avec le client :
    #connexion.send("Vous êtes connecté. Envoyez vos messages.")
