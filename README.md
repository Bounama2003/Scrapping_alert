# Scrapping_alert
 Script simple en python pour Scrapper le prix d'un article sur Alibaba ou n'importe quel site et renvoyer un alerte sur notre téléphone si le prix est en baisse avec un suivi de 24/7
# Installation
  # 1. Créer un environnement virtuel:
      python -m venv your_virtual_environment
  # 2. Activer l'environnement virtuel
     # a. Sous windows
        your_virtual_environment\Scrips\activate
	 # b. Sous Mac
		source your_virtual_environment/bin/activate
  # 3. Installer les dépendances:
      pip install -r requirements.txt
# Configuration des variables d'environnement
  # 1. Créer un fichier .env à la racine et ajoutez
      PUSHOVER_TOKEN="your_pushover_token"
	  PUSHOVER_USER_KEY="your_pushover_user_key"
	  BRIGHTDATA_PROXY="your_bright_data_proxy"
#. Exécution

    python price_alert.py
# NB: Ces données ne doivent pas être publiés dans des sites ou autre vous pouvez l'utiliser à titre personnel ou à titre d'apprentissage
  
