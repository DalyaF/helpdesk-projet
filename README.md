# 🛠️ Helpdesk - Système de Tickets de Support Interne

Ce projet est une application web simple de gestion des tickets de support interne à destination des départements comme l’IT, les Ressources Humaines ou la Logistique. Il permet de créer, suivre et résoudre les demandes internes au sein d'une entreprise.

## 🚀 Stack Technique

- Frontend : HTML, CSS  
- Backend : Python (Flask)
- Base de données : MySQL

## 📌 Fonctionnalités principales

- ✅ Formulaire de création de ticket :
  - Titre
  - Description
  - Priorité (Basse, Moyenne, Haute, Urgente)
  - Département concerné (IT, RH, Logistique)

- 📂 Base de données :
  - Table `tickets` pour stocker les demandes
  - Table `departments` pour catégoriser les services
  - Table `comments` pour le suivi des échanges

- 👨‍🔧 Interface technicien :
  - Affichage de tous les tickets par ordre de priorité
  - Filtres par département, statut, priorité
  - Consultation des détails d’un ticket
  - Mise à jour du statut (Nouveau, En cours, En attente, Résolu, Fermé)
  - Ajout de commentaires

## 🎯 Objectif entreprise

Cet outil vise à améliorer le suivi et la gestion des demandes internes pour :
- le support informatique (IT),
- les ressources humaines (RH),
- la logistique ou tout autre service transversal.

## 🗂️ Structure des fichiers

