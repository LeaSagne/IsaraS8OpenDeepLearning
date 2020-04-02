# IsaraS8OpenDeepLearning

Repository contenant les différents scripts Python nécessaires à la réalisation d'un exemple simple de classification d'images par un réseau neuronal convolutif.

Construit pour illustrer les TD sur Git, Python et Deep Learning du module S8-OPEN d'ISARA4.


**Logiciels requis :**

* Notepad++ ou autre éditeur de texte brut
* Firefox
* Gecko Driver 0.26 (pour faire du Web scraping avec Python et Firefox en prenant le contrôle du navigateur) : https://github.com/mozilla/geckodriver/releases
* Git 2.21.0 or higher
* Python 3.7.2 or higher in Anaconda
* Spyder Python IDE in Anaconda
* Keras (deep learning package for Python) in Anaconda
* Tensorflow in Anaconda (dont Tensorflow-eigen)
* vs2013_runtime in Anaconda


*Résolution de certains problèmes avec l'installation par défaut de Keras dans la distribution Anaconda :*

    python -m pip uninstall tensorflow
    python -m pip uninstall protobuf
    rmdir /S C:\Users\cberteletti\AppData\Local\Continuum\anaconda3\Lib\site-packages\tensor*
    python -m pip install tensorflow
