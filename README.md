pycomon: A simple internet connection monitor
=======================

This project aims to build a simple connection monitor than
can be used everyday to monitor ***ping*** and ***throughtput***,
or in other words, your ***lag*** and ***how fast you can download***.

The tool can do an instant test, but the main goal is to run an hourly test,
for as long as the program is running. The results can be read by
any spreadsheet software such as Excel, Libreoffice or even google drive.
This way you can examine all your data on your own (and then shove it in the face of your ISP).

How to use 
====================

Just open the program and type some urls in the first column. Then click on the box in the ***Enabled*** column.
That's it. Once per hour, the program will do a latency (ping) test and try to download the file from the link.

Keep in mind that if you choose a file that is too small, the download speed will not be very accurate.

Requirements
====================

Python 3. That's it. Everything else comes with Python.

Installing
====================

If you are on linux, just this will do the job:
```bash
sudo pip3 install pycomon
```

After this, the program will be avaiable as ***pycomon*** in the commandline.

It should be the same on windows. 

----

pycomon: Um monitor de conexão simples
======================

O objetivo deste projeto é construir uma ferramenta simples pra monitorar a sua conexão de internet.
O programa monitora o ***ping*** e o ***throughtput*** da sua conexão, ou, em outras palavras, o seu ***lag*** e a 
sua ***velocidade de download***.


Como usar
==============

É só abrir o programa e digitar as urls para testar na primeira coluna. Daí clique na caixa na coluna ***Enabled***.
É isso. Uma vez por hora o programa tentará fazer um teste de latência (ping) e tentará baixar o arquivo do link.

Tenha em mente que se você escolher um arquivo muito pequeno, a velocidade de download não sera muito precisa.

Requisitos
====================

Python 3. Só. Todo o resto vem com o Python.

Instalando
====================

Se voce está no linux, isso já faz o trabalho:
```bash
sudo pip install pycomon
```

Depois de rodar o comando acima, o programa estará disponível como ***pycomon*** na linha de comando.

Deve ser o mesmo no windows.
