je souhaite développer un outil agentique qui doit, à partir du nom d'une entreprise, me fournir  un résumé complet autour de cette dernière (activités, liens capitalistiques, CA, actualités).

Pour cela, j'ai plusieurs API possible:
- Identification du site de l'entreprise à partir du nom
- Accès à une base de données PostGre contenant des informations extraites du site web de l'entreprise à partir d'une URL
-  Récupération des documents INPI à partir du nom ou du SIREN
- Structuration des informations contenus dans les documents INPI pour en extraire des liens capitalistiques, et des informations financières
- Accès à une DB contenant des informations financières et/ou liens capits à partir d'un SIREN ou d'un nom
- Accès à des informations extraites des actualités d'une entreprise (ex: a levée des fonds et entreprises liées) 
Et d'autres outils en cours de développement.

L'objectif est du coup que mon agent principal soit capable de prendre des décisions pour utiliser chacun de ces outils, et qu'il le fasse de façon récursive sur les entreprises liées à l'entreprise principale. 