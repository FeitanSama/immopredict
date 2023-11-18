import requests

def get_list_of_adresses(adresse,limit):
    """
    Récupère une liste d'adresses à partir de l'API Adresse Data Gouv.
    https://adresse.data.gouv.fr/api-doc/adresse

    Args:
        adresse (str): L'adresse à rechercher.
        limit (int): Le nombre maximum de résultats à retourner.

    Returns:
        list: Une liste de résultats contenant des informations sur les adresses correspondant à la requête.
            Chaque élément de la liste est un dictionnaire contenant des données sur une adresse spécifique.
            Les données incluses peuvent varier, mais elles peuvent inclure des informations telles que la localisation
            géographique, la rue, la ville, le code postal, etc.

    Raises:
        - Aucune exception n'est gérée dans cette fonction. Cependant, des erreurs peuvent survenir lors de l'exécution
          si l'adresse n'est pas valide ou si la limite est définie à une valeur inappropriée.

    Exemple:
        Pour récupérer une liste d'adresses correspondant à "123 Rue de la République" avec une limite de 5 résultats :
        >>> results = get_list_of_adresses("123 Rue de la République", 5)
        >>> print(results)

    Remarques:
        Cette fonction dépend de l'API Adresse Data Gouv (https://api-adresse.data.gouv.fr/), et nécessite
        que le module 'requests' soit installé pour effectuer des requêtes HTTP. Assurez-vous d'importer
        le module 'requests' dans votre script Python avant d'utiliser cette fonction.
    """
    adresse = adresse.replace(' ','+')
    url = f'https://api-adresse.data.gouv.fr/search/?q={adresse}&limit={limit}'
    results = requests.get(url).json()
    return results

def get_info_of_specific_adresse(adresse):
    """
    Récupère une liste d'adresses à partir de l'API Adresse Data Gouv.
    https://adresse.data.gouv.fr/api-doc/adresse

    Args:
        adresse (str): L'adresse à rechercher.

    Returns:
        list: Une liste contenant des informations sur l'adresse correspondant à la requête.
            Les données incluses peuvent varier, mais elles peuvent inclure des informations telles que la localisation
            géographique, la rue, la ville, le code postal, etc.


    Exemple:
        Pour récupérer une liste d'adresses correspondant à "123 Rue de la République":
        >>> results = get_list_of_adresses("123 Rue de la République")
        >>> print(results)

    Remarques:
        Cette fonction dépend de l'API Adresse Data Gouv (https://api-adresse.data.gouv.fr/), et nécessite
        que le module 'requests' soit installé pour effectuer des requêtes HTTP. Assurez-vous d'importer
        le module 'requests' dans votre script Python avant d'utiliser cette fonction.
    """
    adresse = adresse.replace(' ','+')
    url = f'https://api-adresse.data.gouv.fr/search/?q={adresse}&limit={1}'
    result = requests.get(url).json()
    return result