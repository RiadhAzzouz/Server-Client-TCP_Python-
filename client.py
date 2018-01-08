#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Définition d'un client réseau gérant en parallèle l'émission
 # et la réception des messages (utilisation de 2 THREADS).

host = '192.168.43.158'
port = 44444

import socket, sys, threading, time


	

class ThreadEmission(threading.Thread):
	
	def __init__(self, conn):
		threading.Thread.__init__(self)
		self.connexion = conn           # réf. du socket de connexion
	
	def demande(self,x):
		self.connexion.send(x.encode())
		r = self.connexion.recv(9999)
		print("%s\n" % r)
		id = raw_input()
		self.connexion.send(id)
		x = self.connexion.recv(9999)
		print x

	def recevoirFacture(self,a):
		self.connexion.send(a.encode())
		msg = self.connexion.recv(1000)
		print msg

	def acheterPro(self,a):
		self.connexion.send(a.encode())
		print "Acquiring Lock \n"
		print "Waiting ... \n"
		r = self.connexion.recv(9999)
		print "Lock Acquired \n"
		print("%s\n" % r)
		id = raw_input()
		self.connexion.send(id)
		x = self.connexion.recv(9999)
		print x
		if x == "Le produit n'existe pas \n":
			self.acheterPro(a)
		else:
			qt = raw_input()
			self.connexion.send(qt)
			id1 = self.connexion.recv(1000)
			print id1
			id1 = raw_input()
			self.connexion.send(id1)
			b = self.connexion.recv(9999)
			print b
			ch = "Operation effectuée avec succes\n"
			if b!= ch:
				rep = raw_input()
				self.connexion.send(rep)
				if rep in ('Y' , 'y'):
					self.acheterPro(a)

	def menu(self):
	
		print("1- Consulter le stock d'un produit \n")
		print("2- Consulter les factures d'un client \n")
		print("3- Consulter l'historique des commandes \n")
		print("4- Acheter un produit \n")
		print("5- Recevoir une facture \n")
		print("6- Quitter \n")

		r = int(input("Saisir votre choix \n"))
		if r == 1:
			self.demande("1")
			self.menu()
		elif r == 2:
			self.demande("2")
			self.menu()
		elif r == 3:
			self.connexion.send("3")
			r = self.connexion.recv(9999)
			print("%s\n" % r)
			self.menu()
		elif r == 4:
			self.acheterPro("4")
			self.menu()
		elif r == 5:
			self.recevoirFacture("5")
			self.menu()
		elif r == 6:
			self.connexion.send("6")
			print("A bientot\n")
			sys.exit()
		else:
			print("Choix Invalide \n")
			self.menu()

	def run(self):
		self.menu()


# Programme principal - Établissement de la connexion :
connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	connexion.connect((host, port))
except socket.error:
	print "La connexion a échoué."
	sys.exit()    
print "Connexion établie avec le serveur."
			
# Dialogue avec le serveur : on lance deux threads pour gérer
# indépendamment l'émission et la réception des messages :
th_E = ThreadEmission(connexion)
#th_R = ThreadReception(connexion)

th_E.start()
#th_R.start()
